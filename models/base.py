# models/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class ModelAdapter(ABC):
    """Base class for model adapters."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get("model", "gpt-4")
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "")
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = config.get("temperature", 0.7)

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send a chat request to the model."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the model name."""
        pass
