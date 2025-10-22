"""GuardrailAgent: Drop-in replacement for Agents SDK Agent with automatic guardrails.

This module provides the GuardrailAgent class that acts as a factory for creating
Agents SDK Agent instances with guardrails automatically configured from a pipeline
configuration file.

Tool-level guardrails are used for Prompt Injection Detection to check each tool
call and output, while other guardrails run at the agent level.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ._openai_utils import prepare_openai_kwargs
from .utils.conversation import merge_conversation_with_items, normalize_conversation

logger = logging.getLogger(__name__)

__all__ = ["GuardrailAgent"]

# Guardrails that should run at tool level (before/after each tool call)
# instead of at agent level (before/after entire agent interaction)
_TOOL_LEVEL_GUARDRAILS = ["Prompt Injection Detection"]

# Context variables used to expose conversation information during guardrail checks.
_agent_session: ContextVar[Any | None] = ContextVar("guardrails_agent_session", default=None)
_agent_conversation: ContextVar[tuple[dict[str, Any], ...] | None] = ContextVar(
    "guardrails_agent_conversation",
    default=None,
)
_AGENT_RUNNER_PATCHED = False


def _ensure_agent_runner_patch() -> None:
    """Patch AgentRunner.run once so sessions are exposed via ContextVars."""
    global _AGENT_RUNNER_PATCHED
    if _AGENT_RUNNER_PATCHED:
        return

    try:
        from agents.run import AgentRunner  # type: ignore
    except ImportError:
        return

    original_run = AgentRunner.run

    async def _patched_run(self, starting_agent, input, **kwargs):  # type: ignore[override]
        session = kwargs.get("session")
        fallback_history: list[dict[str, Any]] | None = None
        if session is None:
            fallback_history = normalize_conversation(input)

        session_token = _agent_session.set(session)
        conversation_token = _agent_conversation.set(tuple(dict(item) for item in fallback_history) if fallback_history else None)

        try:
            return await original_run(self, starting_agent, input, **kwargs)
        finally:
            _agent_session.reset(session_token)
            _agent_conversation.reset(conversation_token)

    AgentRunner.run = _patched_run  # type: ignore[assignment]
    _AGENT_RUNNER_PATCHED = True


def _cache_conversation(conversation: list[dict[str, Any]]) -> None:
    """Cache the normalized conversation for the current run."""
    _agent_conversation.set(tuple(dict(item) for item in conversation))


async def _load_agent_conversation() -> list[dict[str, Any]]:
    """Load the latest conversation snapshot from session or fallback storage."""
    cached = _agent_conversation.get()
    if cached is not None:
        return [dict(item) for item in cached]

    session = _agent_session.get()
    if session is not None:
        items = await session.get_items()
        conversation = normalize_conversation(items)
        _cache_conversation(conversation)
        return conversation

    return []


async def _conversation_with_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return conversation history including additional items."""
    base_history = await _load_agent_conversation()
    conversation = merge_conversation_with_items(base_history, items)
    _cache_conversation(conversation)
    return conversation


async def _conversation_with_tool_call(data: Any) -> list[dict[str, Any]]:
    """Build conversation history including the current tool call."""
    event = {
        "type": "function_call",
        "tool_name": data.context.tool_name,
        "arguments": data.context.tool_arguments,
        "call_id": getattr(data.context, "tool_call_id", None),
    }
    return await _conversation_with_items([event])


async def _conversation_with_tool_output(data: Any) -> list[dict[str, Any]]:
    """Build conversation history including the current tool output."""
    event = {
        "type": "function_call_output",
        "tool_name": data.context.tool_name,
        "arguments": data.context.tool_arguments,
        "output": str(data.output),
        "call_id": getattr(data.context, "tool_call_id", None),
    }
    return await _conversation_with_items([event])


def _separate_tool_level_from_agent_level(guardrails: list[Any]) -> tuple[list[Any], list[Any]]:
    """Separate tool-level guardrails from agent-level guardrails.

    Args:
        guardrails: List of configured guardrails

    Returns:
        Tuple of (tool_level_guardrails, agent_level_guardrails)
    """
    tool_level = []
    agent_level = []

    for guardrail in guardrails:
        if guardrail.definition.name in _TOOL_LEVEL_GUARDRAILS:
            tool_level.append(guardrail)
        else:
            agent_level.append(guardrail)

    return tool_level, agent_level


def _attach_guardrail_to_tools(tools: list[Any], guardrail: Callable, guardrail_type: str) -> None:
    """Attach a guardrail to all tools in the list.

    Args:
        tools: List of tool objects to attach the guardrail to
        guardrail: The guardrail function to attach
        guardrail_type: Either "input" or "output" to determine which list to append to
    """
    attr_name = "tool_input_guardrails" if guardrail_type == "input" else "tool_output_guardrails"

    for tool in tools:
        if not hasattr(tool, attr_name) or getattr(tool, attr_name) is None:
            setattr(tool, attr_name, [])
        getattr(tool, attr_name).append(guardrail)


def _create_default_tool_context() -> Any:
    """Create a default context for tool guardrails."""
    from openai import AsyncOpenAI

    @dataclass
    class DefaultContext:
        guardrail_llm: AsyncOpenAI

    return DefaultContext(guardrail_llm=AsyncOpenAI(**prepare_openai_kwargs({})))


def _create_conversation_context(
    conversation_history: list,
    base_context: Any,
) -> Any:
    """Create a context compatible with prompt injection detection that includes conversation history.

    Args:
        conversation_history: User messages for alignment checking
        base_context: Base context with guardrail_llm

    Returns:
        Context object with conversation history
    """

    @dataclass
    class ToolConversationContext:
        guardrail_llm: Any
        conversation_history: list

        def get_conversation_history(self) -> list:
            return self.conversation_history

    return ToolConversationContext(
        guardrail_llm=base_context.guardrail_llm,
        conversation_history=conversation_history,
    )


def _create_tool_guardrail(
    guardrail: Any,
    guardrail_type: str,
    context: Any,
    raise_guardrail_errors: bool,
    block_on_violations: bool,
) -> Callable:
    """Create a generic tool-level guardrail wrapper.

    Args:
        guardrail: The configured guardrail
        guardrail_type: "input" (before tool execution) or "output" (after tool execution)
        context: Guardrail context for LLM client
        raise_guardrail_errors: Whether to raise on errors
        block_on_violations: If True, use raise_exception (halt). If False, use reject_content (continue).

    Returns:
        Tool guardrail function decorated with @tool_input_guardrail or @tool_output_guardrail
    """
    try:
        from agents import (
            ToolGuardrailFunctionOutput,
            ToolInputGuardrailData,
            ToolOutputGuardrailData,
            tool_input_guardrail,
            tool_output_guardrail,
        )
    except ImportError as e:
        raise ImportError("The 'agents' package is required for tool guardrails. Please install it with: pip install openai-agents") from e

    from .runtime import run_guardrails

    if guardrail_type == "input":

        @tool_input_guardrail
        async def tool_input_gr(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
            """Check tool call before execution."""
            guardrail_name = guardrail.definition.name

            try:
                conversation_history = await _conversation_with_tool_call(data)
                ctx = _create_conversation_context(
                    conversation_history=conversation_history,
                    base_context=context,
                )
                check_data = json.dumps(
                    {
                        "tool_name": data.context.tool_name,
                        "arguments": data.context.tool_arguments,
                        "call_id": getattr(data.context, "tool_call_id", None),
                    }
                )

                # Run the guardrail
                results = await run_guardrails(
                    ctx=ctx,
                    data=check_data,
                    media_type="text/plain",
                    guardrails=[guardrail],
                    suppress_tripwire=True,
                    stage_name=f"tool_input_{guardrail_name.lower().replace(' ', '_')}",
                    raise_guardrail_errors=raise_guardrail_errors,
                )

                # Check results
                for result in results:
                    if result.tripwire_triggered:
                        observation = result.info.get("observation", f"{guardrail_name} triggered")
                        message = f"Tool call was violative of policy and was blocked by {guardrail_name}: {observation}."

                        if block_on_violations:
                            return ToolGuardrailFunctionOutput.raise_exception(output_info=result.info)
                        else:
                            return ToolGuardrailFunctionOutput.reject_content(message=message, output_info=result.info)

                return ToolGuardrailFunctionOutput(output_info=f"{guardrail_name} check passed")

            except Exception as e:
                if raise_guardrail_errors:
                    return ToolGuardrailFunctionOutput.raise_exception(output_info={"error": f"{guardrail_name} check error: {str(e)}"})
                else:
                    logger.warning(f"{guardrail_name} check error (treating as safe): {e}")
                    return ToolGuardrailFunctionOutput(output_info=f"{guardrail_name} check skipped due to error")

        return tool_input_gr

    else:  # output

        @tool_output_guardrail
        async def tool_output_gr(data: ToolOutputGuardrailData) -> ToolGuardrailFunctionOutput:
            """Check tool output after execution."""
            guardrail_name = guardrail.definition.name

            try:
                conversation_history = await _conversation_with_tool_output(data)
                ctx = _create_conversation_context(
                    conversation_history=conversation_history,
                    base_context=context,
                )
                check_data = json.dumps(
                    {
                        "tool_name": data.context.tool_name,
                        "arguments": data.context.tool_arguments,
                        "output": str(data.output),
                        "call_id": getattr(data.context, "tool_call_id", None),
                    }
                )

                # Run the guardrail
                results = await run_guardrails(
                    ctx=ctx,
                    data=check_data,
                    media_type="text/plain",
                    guardrails=[guardrail],
                    suppress_tripwire=True,
                    stage_name=f"tool_output_{guardrail_name.lower().replace(' ', '_')}",
                    raise_guardrail_errors=raise_guardrail_errors,
                )

                # Check results
                for result in results:
                    if result.tripwire_triggered:
                        observation = result.info.get("observation", f"{guardrail_name} triggered")
                        message = f"Tool output was violative of policy and was blocked by {guardrail_name}: {observation}."
                        if block_on_violations:
                            return ToolGuardrailFunctionOutput.raise_exception(output_info=result.info)
                        else:
                            return ToolGuardrailFunctionOutput.reject_content(message=message, output_info=result.info)

                return ToolGuardrailFunctionOutput(output_info=f"{guardrail_name} check passed")

            except Exception as e:
                if raise_guardrail_errors:
                    return ToolGuardrailFunctionOutput.raise_exception(output_info={"error": f"{guardrail_name} check error: {str(e)}"})
                else:
                    logger.warning(f"{guardrail_name} check error (treating as safe): {e}")
                    return ToolGuardrailFunctionOutput(output_info=f"{guardrail_name} check skipped due to error")

        return tool_output_gr


def _create_agents_guardrails_from_config(
    config: str | Path | dict[str, Any], stages: list[str], guardrail_type: str = "input", context: Any = None, raise_guardrail_errors: bool = False
) -> list[Any]:
    """Create agent-level guardrail functions from a pipeline configuration.

    NOTE: This automatically excludes "Prompt Injection Detection" guardrails
    since those are handled as tool-level guardrails.

    Args:
        config: Pipeline configuration (file path, dict, or JSON string)
        stages: List of pipeline stages to include ("pre_flight", "input", "output")
        guardrail_type: Type of guardrail for Agents SDK ("input" or "output")
        context: Optional context for guardrail execution (creates default if None)
        raise_guardrail_errors: If True, raise exceptions when guardrails fail to execute.
            If False (default), treat guardrail errors as safe and continue execution.

    Returns:
        List of guardrail functions that can be used with Agents SDK

    Raises:
        ImportError: If agents package is not available
    """
    try:
        from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, input_guardrail, output_guardrail
    except ImportError as e:
        raise ImportError("The 'agents' package is required to create agent guardrails. Please install it with: pip install openai-agents") from e

    # Import needed guardrails modules
    from .registry import default_spec_registry
    from .runtime import instantiate_guardrails, load_pipeline_bundles, run_guardrails

    # Load and parse the pipeline configuration
    pipeline = load_pipeline_bundles(config)

    # Instantiate guardrails for requested stages and filter out tool-level guardrails
    stage_guardrails = {}
    for stage_name in stages:
        stage = getattr(pipeline, stage_name, None)
        if stage:
            all_guardrails = instantiate_guardrails(stage, default_spec_registry)
            # Filter out tool-level guardrails - they're handled separately
            _, agent_level_guardrails = _separate_tool_level_from_agent_level(all_guardrails)
            stage_guardrails[stage_name] = agent_level_guardrails
        else:
            stage_guardrails[stage_name] = []

    # Create default context if none provided
    if context is None:
        from openai import AsyncOpenAI

        @dataclass
        class DefaultContext:
            guardrail_llm: AsyncOpenAI

        context = DefaultContext(guardrail_llm=AsyncOpenAI(**prepare_openai_kwargs({})))

    def _create_stage_guardrail(stage_name: str):
        async def stage_guardrail(ctx: RunContextWrapper[None], agent: Agent, input_data: str) -> GuardrailFunctionOutput:
            """Guardrail function for a specific pipeline stage."""
            try:
                # Get guardrails for this stage (already filtered to exclude prompt injection)
                guardrails = stage_guardrails.get(stage_name, [])
                if not guardrails:
                    return GuardrailFunctionOutput(output_info=None, tripwire_triggered=False)

                # Run the guardrails for this stage
                results = await run_guardrails(
                    ctx=context,
                    data=input_data,
                    media_type="text/plain",
                    guardrails=guardrails,
                    suppress_tripwire=True,  # We handle tripwires manually
                    stage_name=stage_name,
                    raise_guardrail_errors=raise_guardrail_errors,
                )

                # Check if any tripwires were triggered
                for result in results:
                    if result.tripwire_triggered:
                        guardrail_name = result.info.get("guardrail_name", "unknown") if isinstance(result.info, dict) else "unknown"
                        return GuardrailFunctionOutput(output_info=f"Guardrail {guardrail_name} triggered tripwire", tripwire_triggered=True)

                return GuardrailFunctionOutput(output_info=None, tripwire_triggered=False)

            except Exception as e:
                if raise_guardrail_errors:
                    # Re-raise the exception to stop execution
                    raise e
                else:
                    # Current behavior: treat errors as tripwires
                    return GuardrailFunctionOutput(output_info=f"Error running {stage_name} guardrails: {str(e)}", tripwire_triggered=True)

        # Set the function name for debugging
        stage_guardrail.__name__ = f"{stage_name}_guardrail"
        return stage_guardrail

    guardrail_functions = []

    for stage in stages:
        stage_guardrail = _create_stage_guardrail(stage)

        # Decorate with the appropriate guardrail decorator
        if guardrail_type == "input":
            stage_guardrail = input_guardrail(stage_guardrail)
        else:
            stage_guardrail = output_guardrail(stage_guardrail)

        guardrail_functions.append(stage_guardrail)

    return guardrail_functions


class GuardrailAgent:
    """Drop-in replacement for Agents SDK Agent with automatic guardrails integration.

    This class acts as a factory that creates a regular Agents SDK Agent instance
    with guardrails automatically configured from a pipeline configuration.

    Prompt Injection Detection guardrails are applied at the tool level (before and
    after each tool call), while other guardrails run at the agent level.

    When you supply an Agents Session via ``Runner.run(..., session=...)`` the
    guardrails automatically read the persisted conversation history. Without a
    session, guardrails operate on the conversation passed to ``Runner.run`` for
    the current turn.

    Example:
        ```python
        from guardrails import GuardrailAgent
        from agents import Runner, function_tool


        @function_tool
        def get_weather(location: str) -> str:
            return f"Weather in {location}: Sunny"


        agent = GuardrailAgent(
            config="guardrails_config.json",
            name="Weather Assistant",
            instructions="You help with weather information.",
            tools=[get_weather],
        )

        # Use with Agents SDK Runner - prompt injection checks run on each tool call
        result = await Runner.run(agent, "What's the weather in Tokyo?")
        ```
    """

    def __new__(
        cls,
        config: str | Path | dict[str, Any],
        name: str,
        instructions: str,
        raise_guardrail_errors: bool = False,
        block_on_tool_violations: bool = False,
        **agent_kwargs: Any,
    ) -> Any:  # Returns agents.Agent
        """Create a new Agent instance with guardrails automatically configured.

        This method acts as a factory that:
        1. Loads the pipeline configuration
        2. Separates tool-level from agent-level guardrails
        3. Applies agent-level guardrails as input/output guardrails
        4. Applies tool-level guardrails (e.g., Prompt Injection Detection) to all tools:
           - pre_flight + input stages → tool_input_guardrail (before tool execution)
           - output stage → tool_output_guardrail (after tool execution)
        5. Returns a regular Agent instance ready for use with Runner.run()

        Args:
            config: Pipeline configuration (file path, dict, or JSON string)
            name: Agent name
            instructions: Agent instructions
            raise_guardrail_errors: If True, raise exceptions when guardrails fail to execute.
                If False (default), treat guardrail errors as safe and continue execution.
            block_on_tool_violations: If True, tool guardrail violations raise exceptions (halt execution).
                If False (default), violations use reject_content (agent can continue and explain).
                Note: Agent-level input/output guardrails always block regardless of this setting.
            **agent_kwargs: All other arguments passed to Agent constructor (including tools)

        Returns:
            agents.Agent: A fully configured Agent instance with guardrails

        Raises:
            ImportError: If agents package is not available
            ConfigError: If configuration is invalid
            Exception: If raise_guardrail_errors=True and a guardrail fails to execute
        """
        try:
            from agents import Agent
        except ImportError as e:
            raise ImportError("The 'agents' package is required to use GuardrailAgent. Please install it with: pip install openai-agents") from e

        from .registry import default_spec_registry
        from .runtime import instantiate_guardrails, load_pipeline_bundles

        _ensure_agent_runner_patch()

        # Load and instantiate guardrails from config
        pipeline = load_pipeline_bundles(config)

        stage_guardrails = {}
        for stage_name in ["pre_flight", "input", "output"]:
            bundle = getattr(pipeline, stage_name, None)
            if bundle:
                stage_guardrails[stage_name] = instantiate_guardrails(bundle, default_spec_registry)
            else:
                stage_guardrails[stage_name] = []

        # Separate tool-level from agent-level guardrails in each stage
        preflight_tool, preflight_agent = _separate_tool_level_from_agent_level(stage_guardrails.get("pre_flight", []))
        input_tool, input_agent = _separate_tool_level_from_agent_level(stage_guardrails.get("input", []))
        output_tool, output_agent = _separate_tool_level_from_agent_level(stage_guardrails.get("output", []))

        # Create agent-level INPUT guardrails
        input_guardrails = []

        # Add agent-level guardrails from pre_flight and input stages
        agent_input_stages = []
        if preflight_agent:
            agent_input_stages.append("pre_flight")
        if input_agent:
            agent_input_stages.append("input")

        if agent_input_stages:
            input_guardrails.extend(
                _create_agents_guardrails_from_config(
                    config=config,
                    stages=agent_input_stages,
                    guardrail_type="input",
                    raise_guardrail_errors=raise_guardrail_errors,
                )
            )

        # Create agent-level OUTPUT guardrails
        output_guardrails = []
        if output_agent:
            output_guardrails = _create_agents_guardrails_from_config(
                config=config,
                stages=["output"],
                guardrail_type="output",
                raise_guardrail_errors=raise_guardrail_errors,
            )

        # Apply tool-level guardrails
        tools = agent_kwargs.get("tools", [])

        # Map pipeline stages to tool guardrails:
        # - pre_flight + input stages → tool_input_guardrail (checks BEFORE tool execution)
        # - output stage → tool_output_guardrail (checks AFTER tool execution)
        if tools and (preflight_tool or input_tool or output_tool):
            context = _create_default_tool_context()

            # pre_flight + input stages → tool_input_guardrail
            for guardrail in preflight_tool + input_tool:
                tool_input_gr = _create_tool_guardrail(
                    guardrail=guardrail,
                    guardrail_type="input",
                    context=context,
                    raise_guardrail_errors=raise_guardrail_errors,
                    block_on_violations=block_on_tool_violations,
                )
                _attach_guardrail_to_tools(tools, tool_input_gr, "input")

            # output stage → tool_output_guardrail
            for guardrail in output_tool:
                tool_output_gr = _create_tool_guardrail(
                    guardrail=guardrail,
                    guardrail_type="output",
                    context=context,
                    raise_guardrail_errors=raise_guardrail_errors,
                    block_on_violations=block_on_tool_violations,
                )
                _attach_guardrail_to_tools(tools, tool_output_gr, "output")

        # Create and return a regular Agent instance with guardrails configured
        return Agent(name=name, instructions=instructions, input_guardrails=input_guardrails, output_guardrails=output_guardrails, **agent_kwargs)
