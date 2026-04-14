# agent.py
import os
import re
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from models import ModelAdapter, OpenAIAdapter, AnthropicAdapter
from tools import ToolRegistry, ReadTool, WriteTool, ExecTool, ToolResult
from session import SessionManager, Session, Message
from mcp import MCPManager


class Agent:
    """PyClaw AI Agent."""

    TEXT_TOOL_CALL_PATTERN = re.compile(r'\[TOOL:\s*(\w+)\s*(\{.*?\})\]', re.DOTALL)

    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.model_config = self.config.get("model", {})
        self.system_prompt = self.config.get("system_prompt", "")

        self.model = self._create_model_adapter()
        self.tool_registry = ToolRegistry()
        self._register_core_tools()

        session_dir = self.config.get("session_dir", "sessions")
        self.session_manager = SessionManager(session_dir)

        memory_file = self.config.get("memory_file", "MEMORY.md")
        self.memory = self._load_memory(memory_file)
        self.memory_file = memory_file

        self.console_callback: Optional[Callable] = None

        self.mcp_manager = MCPManager()
        self._init_mcp()

    def _init_mcp(self) -> None:
        mcp_config = self.config.get("mcp", {})
        if mcp_config.get("enabled", False):
            for server in mcp_config.get("servers", []):
                name = server.get("name", "unnamed")
                self.mcp_manager.add_server(name, server)

    def _load_config(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _create_model_adapter(self) -> ModelAdapter:
        provider = self.model_config.get("provider", "openai")
        if provider == "anthropic":
            return AnthropicAdapter(self.model_config)
        return OpenAIAdapter(self.model_config)

    def _register_core_tools(self) -> None:
        tool_configs = self.config.get("tools", {})
        self.tool_registry.register(ReadTool())
        self.tool_registry.register(WriteTool())
        self.tool_registry.register(ExecTool(tool_configs.get("exec", {})))

    def _load_memory(self, path: str) -> str:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def save_memory(self) -> None:
        with open(self.memory_file, "w", encoding="utf-8") as f:
            f.write(self.memory)

    def set_console_callback(self, callback: Callable) -> None:
        self.console_callback = callback

    def _print_console(self, message: str) -> None:
        if self.console_callback:
            self.console_callback(message)

    def _truncate(self, text: str, max_lines: int = 2) -> str:
        lines = text.split("\n")
        if len(lines) > max_lines:
            return "\n".join(lines[:max_lines]) + "..."
        return text

    def think(self, session: Session, user_input: str) -> str:
        """Process user input and return agent response."""
        messages = self._build_messages(session, user_input)

        supports_tools = self.model_config.get("supports_tools", True)
        tools = []
        if supports_tools:
            tools = self.tool_registry.to_openai_format()
            if self.mcp_manager.clients:
                mcp_tools = self.mcp_manager.get_all_tools()
                for mcp_tool in mcp_tools:
                    tools.append({
                        "type": "function",
                        "function": {
                            "name": mcp_tool["name"],
                            "description": mcp_tool["description"],
                            "parameters": mcp_tool.get("input_schema", {})
                        }
                    })

        try:
            response = self.model.chat(messages, tools if tools else None)
            assistant_message = self._process_response(response, session)
            return assistant_message.content
        except Exception as e:
            return f"Error: {str(e)}"

    def _build_messages(self, session: Session, user_input: str) -> List[Dict[str, str]]:
        messages = []

        supports_tools = self.model_config.get("supports_tools", True)

        import platform
        import os
        from datetime import datetime

        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cwd = os.getcwd()

        system_content = self.system_prompt
        system_content += f"\n\n[System Info]\nOS: {os_info}\nCurrent Time: {current_time}\nWorking Directory: {cwd}\n"

        if self.memory:
            system_content += f"\n[Long-term Memory]\n{self.memory}"

        if not supports_tools:
            tool_names = list(self.tool_registry.list_tools())
            system_content += f"""\n\n[Tool Calling Instructions]
When you need to use a tool, respond with the tool call in this exact format:
[TOOL: tool_name {{"arg1": "value1", "arg2": "value2"}}]

Available tools: {', '.join(tool_names)}

IMPORTANT: Windows commands should use Python execution by default (language="python").
For file listing, use: exec {{"command": "import os; print(os.listdir('.'))", "language": "python"}}
For file reading, use: read {{"file_path": "filename"}}
For directory listing on any OS, use Python: exec {{"command": "import os; [print(f) for f in os.listdir('.')]", "language": "python"}}

Example: [TOOL: read {{"file_path": "config.json"}}]
Example: [TOOL: write {{"file_path": "output.txt", "content": "hello"}}]
Example: [TOOL: exec {{"command": "print('Hello from Python!')", "language": "python"}}]

Do not include any other text before the [TOOL:] marker when you need to call a tool."""

        messages.append({"role": "system", "content": system_content})

        for msg in session.messages:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": user_input})
        return messages

    def _process_response(self, response: Dict[str, Any], session: Session) -> Message:
        supports_tools = self.model_config.get("supports_tools", True)

        if "choices" in response:
            choice = response["choices"][0]
            content = choice.get("message", {}).get("content", "")
            tool_calls = choice.get("message", {}).get("tool_calls", [])

            message = Message(
                role="assistant",
                content=content,
                timestamp=datetime.now().isoformat(),
                tool_calls=tool_calls if tool_calls else None
            )

            if tool_calls:
                results = self._execute_tools(tool_calls)
                message.tool_results = results
                content += "\n\n" + self._format_tool_results(results)

            session.add_message(message)
            self.session_manager.save_session(session)
            return message
        elif "content" in response:
            content = response.get("content", [])
            text_content = ""
            for block in content:
                if block.get("type") == "text":
                    text_content += block.get("text", "")

            message = Message(
                role="assistant",
                content=text_content,
                timestamp=datetime.now().isoformat()
            )

            if not supports_tools:
                results = self._parse_and_execute_text_tools(text_content)
                if results:
                    message.tool_results = results
                    text_content += "\n\n" + self._format_tool_results(results)

            session.add_message(message)
            self.session_manager.save_session(session)
            return message

        return Message(role="assistant", content="", timestamp=datetime.now().isoformat())

    def _parse_and_execute_text_tools(self, text: str) -> List[Dict]:
        """Parse text for [TOOL: name {...}] patterns and execute them."""
        results = []
        matches = self.TEXT_TOOL_CALL_PATTERN.findall(text)

        for tool_name, args_str in matches:
            try:
                args = json.loads(args_str)
                self._print_console(f"[TOOL] {tool_name}: {self._truncate(str(args))}")
                tool = self.tool_registry.get(tool_name)
                if tool:
                    result = tool.execute(**args)
                    results.append({
                        "tool": tool_name,
                        "args": args,
                        "result": result.to_dict()
                    })
                else:
                    results.append({
                        "tool": tool_name,
                        "args": args,
                        "result": {"success": False, "content": "", "error": f"Unknown tool: {tool_name}"}
                    })
            except json.JSONDecodeError:
                results.append({
                    "tool": tool_name,
                    "args": args_str,
                    "result": {"success": False, "content": "", "error": "Invalid JSON in tool arguments"}
                })

        return results

    def _execute_tools(self, tool_calls: List[Dict]) -> List[Dict]:
        results = []
        for call in tool_calls:
            tool_name = call.get("function", {}).get("name", "")
            arguments = call.get("function", {}).get("arguments", "{}")

            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except:
                    arguments = {}

            self._print_console(f"[TOOL] {tool_name}: {self._truncate(str(arguments))}")

            tool = self.tool_registry.get(tool_name)
            if tool:
                result = tool.execute(**arguments)
                results.append({
                    "tool": tool_name,
                    "args": arguments,
                    "result": result.to_dict()
                })
            elif self.mcp_manager.clients:
                mcp_result = self.mcp_manager.call_tool(tool_name, arguments)
                if mcp_result and "error" not in mcp_result:
                    results.append({
                        "tool": tool_name,
                        "args": arguments,
                        "result": {"success": True, "content": str(mcp_result), "error": None}
                    })
                else:
                    results.append({
                        "tool": tool_name,
                        "args": arguments,
                        "result": {"success": False, "content": "", "error": mcp_result.get("error", f"MCP tool {tool_name} failed")}
                    })
            else:
                results.append({
                    "tool": tool_name,
                    "args": arguments,
                    "result": {"success": False, "content": "", "error": f"Unknown tool: {tool_name}"}
                })
        return results

    def _format_tool_results(self, results: List[Dict]) -> str:
        formatted = "\n[Tool Results]\n"
        for r in results:
            tool_name = r["tool"]
            result = r["result"]
            if result["success"]:
                content = self._truncate(result["content"])
                formatted += f"- {tool_name}: {content}\n"
            else:
                formatted += f"- {tool_name} (error): {result.get('error', 'Unknown error')}\n"
        return formatted
