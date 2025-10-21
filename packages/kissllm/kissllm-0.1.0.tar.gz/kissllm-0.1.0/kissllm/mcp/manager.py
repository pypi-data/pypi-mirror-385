import logging
from contextlib import AsyncExitStack
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from mcp import ClientSession, McpError

from . import MCPConfig

logger = logging.getLogger(__name__)


class MCPConnection:
    """Manages a single MCP server connection and its tools."""

    def __init__(self, config: MCPConfig):
        self.config = config
        self.session: Optional[ClientSession] = None
        self.exit_stack: Optional[AsyncExitStack] = None
        self.tools: List[Any] = []

    @staticmethod
    def ensure_session(retries: int = 3):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(self, *args, **kwargs) -> Any:
                for attempt in range(retries + 1):
                    try:
                        if not self.session:
                            await self.connect()

                        return await func(self, *args, **kwargs)
                    except McpError as e:
                        logging.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}"
                        )
                        await self.cleanup()
                        if attempt == retries:
                            raise

            return wrapper

        return decorator

    async def connect(self):
        """Connect to the MCP server based on the configuration."""
        name = self.config.name
        await self.cleanup()
        logger.info(
            f"Attempting to connect to MCP server '{name}' using {self.config.transport_type} transport."
        )
        self.exit_stack = AsyncExitStack()

        read_stream, write_stream = await self.exit_stack.enter_async_context(
            self.config.create_transport()
        )

        # Initialize session
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self.session.initialize()
        logger.info(f"MCP session initialized for '{name}'.")

    async def cleanup(self):
        if self.exit_stack:
            await self.exit_stack.aclose()
        self.exit_stack = None
        self.session = None
        self.tools = []

    async def __aenter__(self):
        return await self.connect()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    @ensure_session()
    async def get_tool_specs(self) -> List[Dict[str, Any]]:
        """Get all registered tool specifications for this session."""

        if not self.tools:
            name = self.config.name
            response = await self.session.list_tools()
            logger.debug(f"Received tool list response for '{name}'.")
            self.tools = response.tools
        return self.tools

    @ensure_session()
    async def execute_tool(self, tool_name: str, args: Dict) -> Any:
        """Execute an MCP tool call."""
        result = await self.session.call_tool(tool_name, args)
        return result.content

    def is_tool_registered(self, tool_id: str) -> bool:
        """Check if a tool ID is registered in this session."""
        return tool_id in self.tool_registry


class MCPManager:
    """
    Manages connections and tool interactions with MCP servers.
    Acts as an async context manager to handle server lifecycle.
    """

    def __init__(self, mcp_configs: Optional[List[MCPConfig]] = None):
        self._mcp_configs = mcp_configs or []
        self.mcp_connections: Dict[str, MCPConnection] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}

    async def __aenter__(self):
        return await self.register_all()

    async def register_all(self):
        """Connect to all configured MCP servers."""
        for config in self._mcp_configs:
            await self._register_and_connect_server(config)
        return self

    async def _register_and_connect_server(self, config: MCPConfig):
        """Register and connect to a single MCP server configuration."""
        name = config.name
        if name in self.mcp_connections:
            logger.warning(f"MCP server name '{name}' already registered. Skipping.")
            return name

        connection = MCPConnection(config=config)
        self.mcp_connections[name] = connection
        await connection.connect()
        return name

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Disconnect from all MCP servers."""
        await self.unregister_all()

    async def unregister_all(self):
        """Disconnect from all connected MCP servers and clear resources."""
        logger.info("Unregistering all MCP servers...")
        for connection in self.mcp_connections.values():
            await connection.cleanup()

        self.mcp_connections.clear()
        self.mcp_tools.clear()

    async def get_tool_specs(self) -> List[Dict[str, Any]]:
        """Get all registered MCP tool specifications"""
        if not self.mcp_tools:
            for name, connection in self.mcp_connections.items():
                for tool in await connection.get_tool_specs():
                    # Create unique tool ID using server name and tool name
                    tool_id = f"{name}_{tool.name}".replace(".", "_").replace("-", "_")
                    self.mcp_tools[tool_id] = {
                        "server_name": name,  # Store the server name this tool belongs to
                        "original_name": tool.name,  # Original MCP tool name
                        "description": tool.description,
                        "spec": {
                            "type": "function",
                            "function": {
                                "name": tool_id,  # Unique name for LLM
                                "description": tool.description,
                                "parameters": tool.inputSchema,
                            },
                        },
                    }

        return [tool["spec"] for tool in self.mcp_tools.values()]

    async def execute_tool(self, function_name: str, args: Dict) -> Any:
        """Execute an MCP tool call using the appropriate server connection."""
        if function_name not in self.mcp_tools:
            raise ValueError(f"MCP tool '{function_name}' not found in registry.")

        mcp_tool_info = self.mcp_tools[function_name]
        server_name = mcp_tool_info["server_name"]
        original_tool_name = mcp_tool_info["original_name"]  # MCP tool name

        if server_name not in self.mcp_connections:
            raise ValueError(
                f"MCP server '{server_name}' for tool '{function_name}' not registered or disconnected."
            )

        session = self.mcp_connections[server_name]
        return await session.execute_tool(original_tool_name, args)

    def is_mcp_tool(self, function_name: str) -> bool:
        """Check if a function name corresponds to a registered MCP tool."""
        return function_name in self.mcp_tools
