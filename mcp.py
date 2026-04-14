# mcp.py - Model Context Protocol support

import json
import subprocess
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass


@dataclass
class MCPResource:
    name: str
    description: str
    uri: str


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPClient:
    """MCP Client for connecting to MCP servers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.tools: List[MCPTool] = []
        self.resources: List[MCPResource] = []

    def connect(self) -> bool:
        """Connect to MCP server."""
        command = self.config.get("command", "")
        if not command:
            return False

        try:
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self._initialize()
            return True
        except Exception as e:
            print(f"MCP connection failed: {e}")
            return False

    def _initialize(self) -> None:
        """Send initialization request to MCP server."""
        if not self.process:
            return

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {}
            }
        }
        self._send(request)
        response = self._receive()
        if response:
            self._handle_notification(response)

    def _send(self, message: Dict) -> None:
        if self.process and self.process.stdin:
            self.process.stdin.write(json.dumps(message) + "\n")
            self.process.stdin.flush()

    def _receive(self) -> Optional[Dict]:
        if self.process and self.process.stdout:
            line = self.process.stdout.readline()
            if line:
                return json.loads(line)
        return None

    def _handle_notification(self, message: Dict) -> None:
        method = message.get("method", "")
        if method == "notifications/initialized":
            self._list_tools()
            self._list_resources()

    def _list_tools(self) -> None:
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        self._send(request)
        response = self._receive()
        if response and "result" in response:
            for t in response["result"].get("tools", []):
                self.tools.append(MCPTool(
                    name=t["name"],
                    description=t.get("description", ""),
                    input_schema=t.get("inputSchema", {})
                ))

    def _list_resources(self) -> None:
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/list"
        }
        self._send(request)
        response = self._receive()
        if response and "result" in response:
            for r in response["result"].get("resources", []):
                self.resources.append(MCPResource(
                    name=r["name"],
                    description=r.get("description", ""),
                    uri=r["uri"]
                ))

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        self._send(request)
        response = self._receive()
        if response and "result" in response:
            return response["result"]
        return {"error": "No response from MCP server"}

    def disconnect(self) -> None:
        if self.process:
            self.process.terminate()
            self.process = None


class MCPManager:
    """Manager for MCP clients."""

    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}

    def add_server(self, name: str, config: Dict[str, Any]) -> bool:
        client = MCPClient(config)
        if client.connect():
            self.clients[name] = client
            return True
        return False

    def remove_server(self, name: str) -> None:
        if name in self.clients:
            self.clients[name].disconnect()
            del self.clients[name]

    def get_all_tools(self) -> List[Dict[str, Any]]:
        tools = []
        for name, client in self.clients.items():
            for tool in client.tools:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                    "mcp_server": name
                })
        return tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        for client in self.clients.values():
            for tool in client.tools:
                if tool.name == tool_name:
                    return client.call_tool(tool_name, arguments)
        return {"error": f"Tool not found: {tool_name}"}
