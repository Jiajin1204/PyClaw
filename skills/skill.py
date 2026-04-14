# skills/skill.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class Skill(ABC):
    """Base class for skills."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the skill."""
        pass

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return tools provided by this skill."""
        return []


class SkillRegistry:
    """Registry for managing skills."""

    def __init__(self):
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill:
        return self._skills.get(name)

    def list(self) -> List[str]:
        return list(self._skills.keys())

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all tools from all skills."""
        tools = []
        for skill in self._skills.values():
            tools.extend(skill.get_tools())
        return tools
