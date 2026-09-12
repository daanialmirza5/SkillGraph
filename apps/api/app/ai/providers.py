"""Multi-provider AI abstraction. The Mock provider requires no API key and is the
default so the entire application works without credentials. Real providers make
a single raw HTTP call each (no heavyweight SDKs) and are only used if configured.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import httpx

from app.core.config import get_settings

settings = get_settings()


class AIProvider(ABC):
    name = "base"

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError


class MockProvider(AIProvider):
    """Deterministic, template-based provider. Formats the already-grounded
    evidence package into natural language without calling any external service.
    This is what runs the whole demo when no API keys are configured."""

    name = "mock"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return (
            "[Mock AI Analyst — no external model called]\n\n"
            f"{user_prompt}\n\n"
            "This response was generated deterministically from the structured evidence "
            "package above, without inventing any skill, project, or score not present in it."
        )


class AnthropicProvider(AIProvider):
    name = "anthropic"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-5",
                "max_tokens": 800,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return "".join(block.get("text", "") for block in data.get("content", []))


class OpenAIProvider(AIProvider):
    name = "openai"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}", "content-type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


class GoogleProvider(AIProvider):
    name = "google"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not settings.google_api_key:
            raise RuntimeError("GOOGLE_API_KEY is not configured")
        resp = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.google_api_key}",
            json={
                "systemInstruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"parts": [{"text": user_prompt}]}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


def get_provider(name: str | None = None) -> AIProvider:
    provider_name = (name or settings.ai_provider or "mock").lower()
    providers: dict[str, type[AIProvider]] = {
        "mock": MockProvider,
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "google": GoogleProvider,
    }
    provider_cls = providers.get(provider_name, MockProvider)
    return provider_cls()
