# tools/registry.py
from typing import Dict, List, Optional
from .base import Tool


class ToolRegistry:
    """Registry for managing tools."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def get_all(self) -> Dict[str, Tool]:
        """Get all registered tools."""
        return self._tools.copy()

    def to_openai_format(self) -> List[Dict]:
        """Convert all tools to OpenAI format."""
        return [tool.to_openai_format() for tool in self._tools.values()]

    def to_anthropic_format(self) -> List[Dict]:
        """Convert all tools to Anthropic format."""
        return [tool.to_anthropic_format() for tool in self._tools.values()]

    def clear(self) -> None:
        """Clear all tools."""
        self._tools.clear()
