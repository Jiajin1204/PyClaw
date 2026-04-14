# tools/write.py
import os
from typing import Dict, Any
from .base import Tool, ToolResult


class WriteTool(Tool):
    """Tool for writing files."""

    @property
    def name(self) -> str:
        return "write"

    @property
    def description(self) -> str:
        return "Write content to a file. Creates the file if it doesn't exist, overwrites if it does."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }

    def execute(self, file_path: str, content: str) -> ToolResult:
        """Write content to file."""
        try:
            file_path = os.path.expanduser(file_path)
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return ToolResult(True, f"Successfully wrote to {file_path}")
        except Exception as e:
            return ToolResult(False, "", str(e))
