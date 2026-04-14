# models/anthropic.py
import requests
from typing import List, Dict, Any, Optional
from .base import ModelAdapter


class AnthropicAdapter(ModelAdapter):
    """Anthropic API adapter."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = f"{self.base_url.rstrip('/')}/messages"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send a chat request to Anthropic API."""
        system_msg = ""
        filtered_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                system_msg = msg.get("content", "")
            else:
                filtered_messages.append(msg)

        payload = {
            "model": self.model,
            "messages": filtered_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        if system_msg:
            payload["system"] = system_msg
        if tools:
            payload["tools"] = tools

        response = requests.post(self.url, headers=self.headers, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()

    def get_name(self) -> str:
        return f"Anthropic {self.model}"
