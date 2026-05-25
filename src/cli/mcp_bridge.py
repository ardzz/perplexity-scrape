"""
MCP Tool Bridge

Connects to external MCP servers (BurpSuite, filesystem, custom, etc.)
and exposes their tools to the CLI's agentic loop.

Supports stdio-based MCP servers loaded from a JSON config file.
"""

import asyncio
import json
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    HAS_MCP = True
except ImportError:
    HAS_MCP = False


class MCPServer:
    """Represents a connected MCP server with its available tools."""

    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self.tools: list[dict] = []
        self.session: Any = None
        self._client_ctx: Any = None
        self._session_ctx: Any = None
        self.connected = False

    async def connect(self) -> bool:
        """Connect to the MCP server via stdio."""
        if not HAS_MCP:
            return False

        try:
            command = self.config.get("command", "")
            args = self.config.get("args", [])
            env = self.config.get("env", None)

            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env,
            )

            self._client_ctx = stdio_client(server_params)
            read, write = await self._client_ctx.__aenter__()

            self._session_ctx = ClientSession(read, write)
            self.session = await self._session_ctx.__aenter__()

            await self.session.initialize()

            # Fetch available tools
            tools_result = await self.session.list_tools()
            self.tools = [
                {
                    "name": t.name,
                    "server": self.name,
                    "full_name": f"{self.name}.{t.name}",
                    "description": t.description or "",
                    "input_schema": t.inputSchema or {},
                }
                for t in tools_result.tools
            ]
            self.connected = True
            return True

        except Exception as e:
            self.connected = False
            raise ConnectionError(f"Failed to connect to MCP server '{self.name}': {e}")

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool on this MCP server."""
        if not self.session:
            raise RuntimeError(f"Not connected to server '{self.name}'")

        result = await self.session.call_tool(tool_name, arguments)

        # Extract text content from result
        if result.content:
            parts = []
            for item in result.content:
                if hasattr(item, "text"):
                    parts.append(item.text)
                elif hasattr(item, "data"):
                    parts.append(f"[binary data: {len(item.data)} bytes]")
                else:
                    parts.append(str(item))
            return "\n".join(parts)

        return "(empty result)"

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        try:
            if self._session_ctx:
                await self._session_ctx.__aexit__(None, None, None)
            if self._client_ctx:
                await self._client_ctx.__aexit__(None, None, None)
        except Exception:
            pass
        self.connected = False


class MCPToolBridge:
    """
    Manages connections to multiple MCP servers and provides
    a unified interface for listing and calling tools.
    """

    def __init__(self):
        self.servers: dict[str, MCPServer] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

    def _start_loop(self) -> None:
        """Start the background event loop in a daemon thread if not already running."""
        import threading
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def _run_loop(self) -> None:
        """Background thread target to run the event loop forever."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def load_config(self, config_path: str) -> list[str]:
        """
        Load MCP server configs from a JSON file.
        Returns list of server names that were loaded.
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(path) as f:
            config = json.load(f)

        servers_config = config.get("mcpServers", {})
        loaded = []

        for name, server_cfg in servers_config.items():
            self.servers[name] = MCPServer(name, server_cfg)
            loaded.append(name)

        return loaded

    def connect_all(self) -> dict[str, bool]:
        """Connect to all configured servers thread-safely. Returns {name: success} map."""
        if not self.servers:
            return {}

        self._start_loop()
        results = {}

        for name, server in self.servers.items():
            try:
                # Dispatch connect asynchronously to background thread loop
                future = asyncio.run_coroutine_threadsafe(server.connect(), self._loop)
                # Wait up to 10 seconds for connection to succeed
                success = future.result(timeout=10)
                results[name] = success
            except Exception as e:
                results[name] = False
                server.last_error = str(e)

        return results

    def connect_server(self, name: str) -> bool:
        """Connect to a specific server by name thread-safely."""
        if name not in self.servers:
            raise KeyError(f"No server named '{name}'")

        self._start_loop()
        future = asyncio.run_coroutine_threadsafe(self.servers[name].connect(), self._loop)
        return future.result(timeout=10)

    def get_all_tools(self) -> list[dict]:
        """Return all tools from all connected servers."""
        tools = []
        for server in self.servers.values():
            if server.connected:
                tools.extend(server.tools)
        return tools

    def find_tool(self, full_name: str) -> Optional[tuple[MCPServer, str]]:
        """
        Find a server and tool name from a full_name like 'burpsuite.scan'.
        Returns (server, tool_name) or None.
        """
        if "." in full_name:
            server_name, tool_name = full_name.split(".", 1)
            if server_name in self.servers and self.servers[server_name].connected:
                return self.servers[server_name], tool_name
        else:
            # Search by tool name across all servers
            for server in self.servers.values():
                if server.connected:
                    for tool in server.tools:
                        if tool["name"] == full_name:
                            return server, full_name
        return None

    def call_tool(self, full_name: str, arguments: dict) -> tuple[str, float]:
        """
        Call a tool by full name (e.g. 'burpsuite.active_scan') thread-safely.
        Returns (result, elapsed_seconds).
        """
        found = self.find_tool(full_name)
        if not found:
            raise KeyError(f"Tool '{full_name}' not found in any connected server")

        server, tool_name = found
        self._start_loop()

        start = time.time()
        # Dispatch execution asynchronously to background thread loop
        future = asyncio.run_coroutine_threadsafe(
            server.call_tool(tool_name, arguments), self._loop
        )
        try:
            # Force 30 second timeout on tool execution to prevent freezes
            result = future.result(timeout=30)
        except Exception as e:
            result = f"Error: Tool call timed out or failed: {e}"
            
        elapsed = time.time() - start
        return result, elapsed

    def parse_tool_args(self, args_str: str) -> dict:
        """
        Parse tool arguments from CLI string.
        Supports: key=value pairs OR raw JSON string.

        Examples:
            url=https://example.com scan_type=full
            {"url": "https://example.com", "scan_type": "full"}
        """
        args_str = args_str.strip()
        if not args_str:
            return {}

        # Try JSON first
        if args_str.startswith("{"):
            try:
                return json.loads(args_str)
            except json.JSONDecodeError:
                pass

        # Parse key=value pairs
        result = {}
        parts = args_str.split()
        for part in parts:
            if "=" in part:
                key, _, value = part.partition("=")
                # Try to cast to int/float/bool
                if value.lower() == "true":
                    result[key] = True
                elif value.lower() == "false":
                    result[key] = False
                else:
                    try:
                        result[key] = int(value)
                    except ValueError:
                        try:
                            result[key] = float(value)
                        except ValueError:
                            result[key] = value
            else:
                # Positional arg
                result[f"arg_{len(result)}"] = part

        return result

    def get_tools_as_openai_format(self) -> list[dict]:
        """
        Return all tools in OpenAI function-calling format.
        Useful for injecting into LLM context.
        """
        tools = []
        for tool in self.get_all_tools():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool["full_name"].replace(".", "__"),
                    "description": tool["description"],
                    "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
                },
            })
        return tools

    def disconnect_all(self) -> None:
        """Disconnect from all servers thread-safely and shut down loop."""
        if self._loop and not self._loop.is_closed():
            for server in self.servers.values():
                try:
                    future = asyncio.run_coroutine_threadsafe(server.disconnect(), self._loop)
                    future.result(timeout=3)
                except Exception:
                    pass
            try:
                self._loop.call_soon_threadsafe(self._loop.stop)
            except Exception:
                pass

    @property
    def has_tools(self) -> bool:
        return bool(self.get_all_tools())

    @property
    def connected_servers(self) -> list[str]:
        return [n for n, s in self.servers.items() if s.connected]
