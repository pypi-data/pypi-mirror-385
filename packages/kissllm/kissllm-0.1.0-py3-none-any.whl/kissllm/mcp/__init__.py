import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

from kissllm.exceptions import InvalidMCPConfig

logger = logging.getLogger(__name__)


class MCPConfig:
    pass


def parse_mcp_config(server_name, server_conf_dict) -> MCPConfig:
    if "command" in server_conf_dict:
        return StdioMCPConfig(name=server_name, **server_conf_dict)
    elif "url" in server_conf_dict:
        return StreamableHttpMCPConfig(name=server_name, **server_conf_dict)
    else:
        logger.warning(
            f"Skipping MCP server '{server_name}', not supported server type"
        )
        raise InvalidMCPConfig


@dataclass
class StdioMCPConfig(MCPConfig):
    """Configuration for an MCP server connected via stdio."""

    transport_type: Literal["stdio"] = "stdio"

    def __init__(
        self,
        name: str,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
    ) -> None:
        self.name = name
        self.command = command
        self.args = args
        self.env = env

    def create_transport(self):
        """Create transport for this configuration."""
        server_params = StdioServerParameters(
            command=self.command, args=self.args, env=self.env
        )
        transport = stdio_client(server_params)
        return transport


@dataclass
class StreamableHttpMCPConfig(MCPConfig):
    """Configuration for an MCP server connected via Streamable http."""

    transport_type: Literal["streamable-http"] = "streamable-http"

    def __init__(self, name, url) -> None:
        self.name = name
        self.url = url

    @asynccontextmanager
    async def create_transport(self):
        """Create transport for this configuration."""
        async with streamablehttp_client(self.url) as (read_stream, write_stream, _):
            yield read_stream, write_stream


# Example mcp_servers.json structure:
"""
{
  "servers": [
    {
      "name": "My Stdio Server",
      "type": "stdio",
      "command": "python",
      "args": ["/path/to/my_mcp_server.py", "stdio"],
      "env": {"MY_VAR": "value"}
    },
    {
      "name": "My Streamable http Server",
      "type": "streamable-http",
      "url": "http://localhost:8080/mcp"
    },
    {
       // Minimal stdio config
      "command": "another_server_cmd"
    }
  ]
}
"""
