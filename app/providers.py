"""LLM provider abstraction.

Provider modes:
- mock   : canned responses, no external calls (default, useful for local testing)
- hosted : OpenAI-compatible chat completions
- ollama : local Ollama server

Selected via PROVIDER env var.
"""
import json
import os
from typing import Protocol

import requests

from app.config import HOSTED_API_KEY, HOSTED_MODEL, OLLAMA_MODEL, OLLAMA_URL, PROVIDER


class LLMProvider(Protocol):
    def complete(self, system: str, user: str) -> str: ...


class MockProvider:
    def complete(self, system: str, user: str) -> str:
        # not great but useful when there's no API key
        return json.dumps({
            "answer": "Mock answer. Configure PROVIDER=hosted or ollama for real responses.",
            "value": 0.0,
            "citations": [],
        })


class HostedProvider:
    def __init__(self) -> None:
        self.key = HOSTED_API_KEY
        self.model = HOSTED_MODEL
        self.url = "https://api.openai.com/v1/chat/completions"

    def complete(self, system: str, user: str) -> str:
        resp = requests.post(
            self.url,
            headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


class OllamaProvider:
    def __init__(self) -> None:
        self.url = OLLAMA_URL
        self.model = OLLAMA_MODEL

    def complete(self, system: str, user: str) -> str:
        resp = requests.post(
            f"{self.url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]


def get_provider() -> LLMProvider:
    p = os.environ.get("PROVIDER", PROVIDER)
    if p == "hosted":
        return HostedProvider()
    if p == "ollama":
        return OllamaProvider()
    return MockProvider()
