# mcp_cli/chat/chat_context.py
"""
Clean chat context focused on conversation state and tool coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, AsyncIterator, Optional

from chuk_term.ui import output

from mcp_cli.chat.system_prompt import generate_system_prompt
from mcp_cli.tools.manager import ToolManager
from mcp_cli.tools.models import ToolInfo, ServerInfo
from mcp_cli.model_manager import ModelManager

logger = logging.getLogger(__name__)


class ChatContext:
    """
    Chat context focused on conversation state and tool coordination.

    Responsibilities:
    - Conversation history management
    - Tool discovery and adaptation coordination
    - Session state (exit requests, etc.)

    Model management is completely delegated to ModelManager.
    """

    def __init__(self, tool_manager: ToolManager, model_manager: ModelManager):
        """
        Create chat context with required managers.

        Args:
            tool_manager: Tool management interface
            model_manager: Model configuration and LLM client manager
        """
        self.tool_manager = tool_manager
        self.model_manager = model_manager

        # Conversation state
        self.exit_requested = False
        self.conversation_history: List[Dict[str, Any]] = []
        self.tool_history: List[Dict[str, Any]] = []  # Track tool execution history

        # Tool state (filled during initialization)
        self.tools: List[ToolInfo] = []
        self.internal_tools: List[ToolInfo] = []
        self.server_info: List[ServerInfo] = []
        self.tool_to_server_map: Dict[str, str] = {}
        self.openai_tools: List[
            Dict[str, Any]
        ] = []  # These remain dicts for OpenAI API
        self.tool_name_mapping: Dict[str, str] = {}

        logger.debug(f"ChatContext created with {self.provider}/{self.model}")

    @classmethod
    def create(
        cls,
        tool_manager: ToolManager,
        provider: str | None = None,
        model: str | None = None,
        api_base: str | None = None,
        api_key: str | None = None,
    ) -> "ChatContext":
        """
        Factory method for convenient creation.

        Args:
            tool_manager: Tool management interface
            provider: Provider to switch to (optional)
            model: Model to switch to (optional)
            api_base: API base URL override (optional)
            api_key: API key override (optional)

        Returns:
            Configured ChatContext instance
        """
        model_manager = ModelManager()

        # Configure provider if API settings provided
        if provider and (api_base or api_key):
            model_manager.configure_provider(
                provider, api_key=api_key, api_base=api_base
            )

        # Switch model if requested
        if provider and model:
            model_manager.switch_model(provider, model)
        elif provider:
            model_manager.switch_provider(provider)
        elif model:
            model_manager.switch_to_model(model)

        return cls(tool_manager, model_manager)

    # ── Properties that delegate to ModelManager ──────────────────────────
    @property
    def client(self) -> Any:
        """Get current LLM client (cached automatically by ModelManager)."""
        return self.model_manager.get_client()

    @property
    def provider(self) -> str:
        """Current provider name."""
        return self.model_manager.get_active_provider()

    @property
    def model(self) -> str:
        """Current model name."""
        return self.model_manager.get_active_model()

    # ── Initialization ────────────────────────────────────────────────────
    async def initialize(self) -> bool:
        """Initialize tools and conversation state."""
        try:
            await self._initialize_tools()
            self._initialize_conversation()

            if not self.tools:
                output.print(
                    "[yellow]No tools available. Chat functionality may be limited.[/yellow]"
                )

            logger.info(
                f"ChatContext ready: {len(self.tools)} tools, {self.provider}/{self.model}"
            )
            return True

        except Exception as exc:
            logger.exception("Error initializing chat context")
            output.print(f"[red]Error initializing chat context: {exc}[/red]")
            return False

    async def _initialize_tools(self) -> None:
        """Initialize tool discovery and adaptation."""
        # Get tools from ToolManager - already returns ToolInfo objects
        self.tools = await self.tool_manager.get_unique_tools()

        # Get server info - already returns ServerInfo objects
        self.server_info = await self.tool_manager.get_server_info()

        # Build tool-to-server mapping using ToolInfo objects
        self.tool_to_server_map = {t.name: t.namespace for t in self.tools}

        # Adapt tools for current provider
        await self._adapt_tools_for_provider()

        # Keep copy for system prompt
        self.internal_tools = list(self.tools)

    def find_tool_by_name(self, name: str) -> Optional[ToolInfo]:
        """Find a tool by its name (handles both simple and namespaced names)."""
        # First try exact match
        for tool in self.tools:
            if tool.name == name or tool.fully_qualified_name == name:
                return tool

        # Try partial match (just the tool name without namespace)
        simple_name = name.split(".")[-1] if "." in name else name
        for tool in self.tools:
            if tool.name == simple_name:
                return tool

        return None

    def find_server_by_name(self, name: str) -> Optional[ServerInfo]:
        """Find a server by its name."""
        for server in self.server_info:
            if server.name == name or server.namespace == name:
                return server
        return None

    async def _adapt_tools_for_provider(self) -> None:
        """Adapt tools for current provider."""
        try:
            if hasattr(self.tool_manager, "get_adapted_tools_for_llm"):
                tools_and_mapping = await self.tool_manager.get_adapted_tools_for_llm(
                    self.provider
                )
                self.openai_tools = tools_and_mapping[0]
                self.tool_name_mapping = tools_and_mapping[1]
                logger.debug(
                    f"Adapted {len(self.openai_tools)} tools for {self.provider}"
                )
            else:
                # Fallback to generic tools
                self.openai_tools = await self.tool_manager.get_tools_for_llm()
                self.tool_name_mapping = {}
        except Exception as exc:
            logger.warning(f"Error adapting tools: {exc}")
            # Final fallback - use the raw tool format
            self.openai_tools = await self.tool_manager.get_tools_for_llm()
            self.tool_name_mapping = {}

    def _initialize_conversation(self) -> None:
        """Initialize conversation with system prompt."""
        # Convert ToolInfo objects to dicts for system prompt generation
        tools_for_prompt = []
        for tool in self.internal_tools:
            if hasattr(tool, "to_openai_format"):
                tools_for_prompt.append(tool.to_openai_format())
            elif isinstance(tool, dict):
                tools_for_prompt.append(tool)
            else:
                # Fallback - convert to dict
                tools_for_prompt.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name if hasattr(tool, "name") else str(tool),
                            "description": tool.description
                            if hasattr(tool, "description")
                            else "No description",
                            "parameters": tool.parameters
                            if hasattr(tool, "parameters")
                            else {},
                        },
                    }
                )

        system_prompt = generate_system_prompt(tools_for_prompt)
        self.conversation_history = [{"role": "system", "content": system_prompt}]

    # ── Model change handling ─────────────────────────────────────────────
    async def refresh_after_model_change(self) -> None:
        """
        Refresh context after ModelManager changes the model.

        Call this after model_manager.switch_model() to update tools.
        ModelManager handles client refresh automatically.
        """
        await self._adapt_tools_for_provider()
        logger.debug(f"ChatContext refreshed for {self.provider}/{self.model}")

    # ── Tool execution (delegate to ToolManager) ──────────────────────────
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool."""
        return await self.tool_manager.execute_tool(tool_name, arguments)

    async def stream_execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> AsyncIterator[Any]:
        """Execute a tool with streaming."""
        async for result in self.tool_manager.stream_execute_tool(tool_name, arguments):
            yield result

    async def get_server_for_tool(self, tool_name: str) -> str:
        """Get server for tool."""
        return await self.tool_manager.get_server_for_tool(tool_name) or "Unknown"

    # ── Conversation management ───────────────────────────────────────────
    def add_user_message(self, content: str) -> None:
        """Add user message to conversation."""
        self.conversation_history.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        """Add assistant message to conversation."""
        self.conversation_history.append({"role": "assistant", "content": content})

    def get_conversation_length(self) -> int:
        """Get conversation length (excluding system prompt)."""
        return max(0, len(self.conversation_history) - 1)

    def clear_conversation_history(self, keep_system_prompt: bool = True) -> None:
        """Clear conversation history."""
        if (
            keep_system_prompt
            and self.conversation_history
            and self.conversation_history[0].get("role") == "system"
        ):
            system_prompt = self.conversation_history[0]
            self.conversation_history = [system_prompt]
        else:
            self.conversation_history = []

    def regenerate_system_prompt(self) -> None:
        """Regenerate system prompt with current tools."""
        system_prompt = generate_system_prompt(self.internal_tools)
        if (
            self.conversation_history
            and self.conversation_history[0].get("role") == "system"
        ):
            self.conversation_history[0]["content"] = system_prompt
        else:
            self.conversation_history.insert(
                0, {"role": "system", "content": system_prompt}
            )

    # ── Simple getters ────────────────────────────────────────────────────
    def get_tool_count(self) -> int:
        """Get number of available tools."""
        return len(self.tools)

    def get_server_count(self) -> int:
        """Get number of connected servers."""
        return len(self.server_info)

    @staticmethod
    def get_display_name_for_tool(namespaced_tool_name: str) -> str:
        """Get display name for tool."""
        return namespaced_tool_name

    # ── Serialization (simplified) ────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        """Export context for command handlers."""
        return {
            "conversation_history": self.conversation_history,
            "tools": self.tools,
            "internal_tools": self.internal_tools,
            "client": self.client,
            "provider": self.provider,
            "model": self.model,
            "model_manager": self.model_manager,
            "server_info": self.server_info,
            "openai_tools": self.openai_tools,
            "tool_name_mapping": self.tool_name_mapping,
            "exit_requested": self.exit_requested,
            "tool_to_server_map": self.tool_to_server_map,
            "tool_manager": self.tool_manager,
        }

    def update_from_dict(self, context_dict: Dict[str, Any]) -> None:
        """Update context from dictionary (simplified)."""
        # Core state updates
        if "exit_requested" in context_dict:
            self.exit_requested = context_dict["exit_requested"]

        if "conversation_history" in context_dict:
            self.conversation_history = context_dict["conversation_history"]

        if "model_manager" in context_dict:
            self.model_manager = context_dict["model_manager"]

        # Tool state updates (for command handlers that modify tools)
        for key in [
            "tools",
            "internal_tools",
            "server_info",
            "tool_to_server_map",
            "openai_tools",
            "tool_name_mapping",
        ]:
            if key in context_dict:
                setattr(self, key, context_dict[key])

    # ── Context manager ───────────────────────────────────────────────────
    async def __aenter__(self):
        """Async context manager entry."""
        if not await self.initialize():
            raise RuntimeError("Failed to initialize ChatContext")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        pass  # ModelManager handles its own persistence

    # ── Debug info ────────────────────────────────────────────────────────
    def get_status_summary(self) -> Dict[str, Any]:
        """Get status summary for debugging."""
        return {
            "provider": self.provider,
            "model": self.model,
            "tool_count": len(self.tools),
            "server_count": len(self.server_info),
            "conversation_length": self.get_conversation_length(),
            "tools_adapted": bool(self.openai_tools),
            "exit_requested": self.exit_requested,
        }

    def __repr__(self) -> str:
        return (
            f"ChatContext(provider='{self.provider}', model='{self.model}', "
            f"tools={len(self.tools)}, messages={self.get_conversation_length()})"
        )

    def __str__(self) -> str:
        return f"Chat session with {self.provider}/{self.model} ({len(self.tools)} tools, {self.get_conversation_length()} messages)"


# ═══════════════════════════════════════════════════════════════════════════════════
# For testing - separate class to keep main ChatContext clean
# ═══════════════════════════════════════════════════════════════════════════════════


class TestChatContext(ChatContext):
    """
    Test-specific ChatContext that works with stream_manager instead of ToolManager.

    Separated from main ChatContext to keep it clean.
    """

    def __init__(self, stream_manager: Any, model_manager: ModelManager):
        """Create test context with stream_manager."""
        # Initialize base attributes without calling super().__init__
        self.tool_manager = None  # type: ignore[assignment]  # Tests don't use ToolManager
        self.stream_manager = stream_manager
        self.model_manager = model_manager

        # Conversation state
        self.exit_requested = False
        self.conversation_history = []

        # Tool state
        self.tools = []
        self.internal_tools = []
        self.server_info = []
        self.tool_to_server_map = {}
        self.openai_tools = []
        self.tool_name_mapping = {}

        logger.debug(f"TestChatContext created with {self.provider}/{self.model}")

    @classmethod
    def create_for_testing(
        cls,
        stream_manager: Any,
        provider: str | None = None,
        model: str | None = None,
    ) -> "TestChatContext":
        """Factory for test contexts."""
        model_manager = ModelManager()

        if provider and model:
            model_manager.switch_model(provider, model)
        elif provider:
            model_manager.switch_provider(provider)
        elif model:
            model_manager.switch_to_model(model)

        return cls(stream_manager, model_manager)

    async def _initialize_tools(self) -> None:
        """Test-specific tool initialization."""
        # Get tools from stream_manager
        if hasattr(self.stream_manager, "get_internal_tools"):
            self.tools = list(self.stream_manager.get_internal_tools())
        else:
            self.tools = list(self.stream_manager.get_all_tools())

        # Get server info
        self.server_info = list(self.stream_manager.get_server_info())

        # Build mappings
        self.tool_to_server_map = {
            (
                t["name"] if isinstance(t, dict) else t.name
            ): self.stream_manager.get_server_for_tool(
                t["name"] if isinstance(t, dict) else t.name
            )
            for t in self.tools
        }

        # Convert tools to OpenAI format for tests
        self.openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": t.get("name", "unknown") if isinstance(t, dict) else t.name,
                    "description": t.get("description", "")
                    if isinstance(t, dict)
                    else t.description,
                    "parameters": t.get("parameters", {})
                    if isinstance(t, dict)
                    else t.parameters,
                },
            }
            for t in self.tools
        ]
        self.tool_name_mapping = {}

        # Copy for system prompt
        self.internal_tools = list(self.tools)

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute tool via stream_manager."""
        if hasattr(self.stream_manager, "call_tool"):
            return await self.stream_manager.call_tool(tool_name, arguments)
        else:
            raise ValueError("Stream manager doesn't support tool execution")

    async def get_server_for_tool(self, tool_name: str) -> str:
        """Get server for tool from stream_manager."""
        return self.stream_manager.get_server_for_tool(tool_name) or "Unknown"
