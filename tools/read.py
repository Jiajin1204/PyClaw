# tools/read.py
import os
from typing import Dict, Any
from .base import Tool, ToolResult


class ReadTool(Tool):
    """Tool for reading files."""

    @property
    def name(self) -> str:
        return "read"

    @property
    def description(self) -> str:
        return "Read the contents of a file. Returns the file content as a string."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["file_path"]
        }

    def execute(self, file_path: str) -> ToolResult:
        """Read file contents."""
        try:
            file_path = os.path.expanduser(file_path)
            if not os.path.exists(file_path):
                return ToolResult(False, "", f"File not found: {file_path}")
            if not os.path.isfile(file_path):
                return ToolResult(False, "", f"Not a file: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return ToolResult(True, content)
        except Exception as e:
            return ToolResult(False, "", str(e))
