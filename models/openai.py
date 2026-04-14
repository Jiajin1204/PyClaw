# models/openai.py
import requests
from typing import List, Dict, Any, Optional
from .base import ModelAdapter


class OpenAIAdapter(ModelAdapter):
    """OpenAI API adapter."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = f"{self.base_url.rstrip('/')}/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send a chat request to OpenAI API."""
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = requests.post(self.url, headers=self.headers, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()

    def get_name(self) -> str:
        return f"OpenAI {self.model}"
