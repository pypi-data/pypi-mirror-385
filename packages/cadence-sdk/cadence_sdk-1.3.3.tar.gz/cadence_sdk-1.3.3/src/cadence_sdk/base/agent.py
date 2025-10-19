"""Base agent interface for Cadence plugin agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.tools import Tool

from ..decorators import AgentTool
from ..types.state import AgentStateFields, PluginContextFields, RoutingHelpers, StateHelpers
from .loggable import Loggable
from .metadata import PluginMetadata


class BaseAgent(ABC, Loggable):
    """Base class for plugin agents used as LangGraph nodes"""

    def __init__(self, metadata: PluginMetadata, parallel_tool_calls: bool = True):
        """Initialize the plugin agent.

        Args:
            metadata: Plugin metadata containing configuration
            parallel_tool_calls: Whether to enable parallel tool execution
        """
        super().__init__()
        self.metadata = metadata
        self.parallel_tool_calls = parallel_tool_calls
        self._tools = None
        self._bound_model = None
        self._initialized = False

    @abstractmethod
    def get_tools(self) -> List[AgentTool]:
        """Return the tools that this agent exposes.

        Returns:
            List[Tool]: Tools to be bound to the LLM
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent.

        Returns:
            str: System prompt for the LLM
        """
        pass

    def initialize(self) -> None:
        """Initialize agent resources (e.g., cache tools).

        Override this method to perform any setup required by your agent,
        such as loading models, connecting to databases, etc.
        """
        self._tools = self.get_tools()
        self._initialized = True

    def cleanup(self) -> None:
        """Cleanup agent resources.

        Override this method to clean up resources when the agent
        is being shut down or reloaded.
        """
        pass

    def bind_model(self, model: BaseChatModel, callbacks: List = None) -> BaseChatModel:
        """Bind the agent's tools to the provided chat model.

        Args:
            model: Base chat model to be specialized
            callbacks: Optional list of callbacks for tool tracking

        Returns:
            BaseChatModel: Tool-bound chat model
        """
        tools = self.get_tools()
        if callbacks:
            self._bound_model = model.bind_tools(
                tools, callbacks=callbacks, parallel_tool_calls=self.parallel_tool_calls
            )
        else:
            self._bound_model = model.bind_tools(tools, parallel_tool_calls=self.parallel_tool_calls)
        return self._bound_model

    @staticmethod
    def should_continue(state: Dict[str, Any]) -> str:
        """Decide whether to call tools or return to the coordinator.

        This method implements the standard Cadence pattern for agent
        decision-making in the LangGraph workflow.

        Args:
            state: Current graph state (expects a 'messages' list)

        Returns:
            str: "continue" to call tools, "back" to return to coordinator
        """
        messages = StateHelpers.safe_get_messages(state)
        last_msg = messages[-1] if messages else None
        if not last_msg:
            return "back"

        tool_calls = getattr(last_msg, "tool_calls", None)
        return "continue" if tool_calls else "back"

    def create_agent_node(self):
        """Create the callable used as this plugin's agent node.

        Returns:
            callable: Function with signature fn(state: Dict[str, Any]) -> Dict[str, Any]
        """
        return self._create_agent_node_function()

    def _create_agent_node_function(self):
        """Create the agent node function for LangGraph integration."""

        def agent_node(state):
            """Process agent state and return updated state."""
            try:
                bound_model = self._get_bound_model()
                system_prompt = self._build_system_prompt()
                response = self._invoke_model(bound_model, system_prompt, state)
                updated_state = self._update_plugin_context(state, response)

                return StateHelpers.create_state_update(
                    response,
                    StateHelpers.safe_get_agent_hops(state),
                    {**updated_state, AgentStateFields.CURRENT_AGENT: self.metadata.name},
                )
            except Exception as e:
                raise RuntimeError(f"Error in agent node for {self.metadata.name}: {e}") from e

        return agent_node

    def _get_bound_model(self):
        """Get the bound model or raise an error if not available."""
        if not hasattr(self, "_bound_model") or self._bound_model is None:
            raise RuntimeError(f"No bound model for agent {self.metadata.name}")
        return self._bound_model

    def _build_system_prompt(self):
        """Build the complete system prompt for the agent."""
        current_time = datetime.now(timezone.utc).isoformat()
        system_header = f"**SYSTEM STATE**:\n- Current Time (UTC): {current_time}\n\n"
        return (
            system_header
            + self.get_system_prompt()
            + "\n**Principle**: Route first, answer briefly only to facilitate handoffs to better tools"
        )

    def _invoke_model(self, bound_model, system_prompt, state):
        """Invoke the model with the prepared messages."""
        request_messages = [SystemMessage(content=system_prompt)] + state[AgentStateFields.MESSAGES]
        return bound_model.invoke(request_messages)

    def _update_plugin_context(self, state, response):
        """Update the plugin context with routing information and response schema."""
        plugin_context = RoutingHelpers.add_to_routing_history(
            StateHelpers.get_plugin_context(state), self.metadata.name
        )
        plugin_context[PluginContextFields.LAST_PLUGIN] = self.metadata.name

        if hasattr(self.metadata, "response_schema") and self.metadata.response_schema:
            self._add_plugin_to_response_schemas(plugin_context)

        return StateHelpers.update_plugin_context(state, **plugin_context)

    def _add_plugin_to_response_schemas(self, plugin_context):
        """Add this plugin to the list of plugins with response schemas."""
        plugins_with_schemas = list(plugin_context.get(PluginContextFields.PLUGINS_WITH_SCHEMAS, []))
        if self.metadata.name not in plugins_with_schemas:
            plugins_with_schemas.append(self.metadata.name)
            plugin_context[PluginContextFields.PLUGINS_WITH_SCHEMAS] = plugins_with_schemas
