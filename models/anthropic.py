# models/anthropic.py
import requests
import time
from typing import List, Dict, Any, Optional
from .base import ModelAdapter


class AnthropicAdapter(ModelAdapter):
    """Anthropic API adapter."""

    RETRY_CODES = {429, 500, 502, 503, 529}

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = f"{self.base_url.rstrip('/')}/messages"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 2)

    def chat(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send a chat request to Anthropic API with retry logic."""
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

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(self.url, headers=self.headers, json=payload, timeout=120)
                if response.status_code in self.RETRY_CODES and attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                last_error = e
                if response.status_code in self.RETRY_CODES and attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                raise

        raise last_error

    def get_name(self) -> str:
        return f"Anthropic {self.model}"
