"""Ollama LLM provider for local models."""

import json
from typing import Any

from ollama import AsyncClient

from codecourt.config import settings
from codecourt.providers.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Provider for local models via Ollama (Llama 3, Mistral, etc.)."""

    def __init__(self, host: str | None = None) -> None:
        self._host = host or settings.ollama_host
        self._client = AsyncClient(host=self._host)
        self._default_model = "llama3"

    @property
    def name(self) -> str:
        return "ollama"

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> str:
        response = await self._client.chat(
            model=model or self._default_model,
            messages=messages,  # type: ignore
            options={"temperature": temperature, "num_predict": max_tokens},
            **kwargs,
        )
        return response["message"]["content"]

    async def complete_json(
        self,
        messages: list[dict[str, str]],
        schema: dict[str, Any],
        model: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        json_instruction = f"\n\nRespond with ONLY valid JSON matching: {json.dumps(schema)}"
        modified_messages = messages.copy()
        if modified_messages:
            last_msg = modified_messages[-1].copy()
            last_msg["content"] += json_instruction
            modified_messages[-1] = last_msg

        response = await self._client.chat(
            model=model or self._default_model,
            messages=modified_messages,  # type: ignore
            format="json",
            **kwargs,
        )
        content = response["message"]["content"]
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            return {}

    async def list_models(self) -> list[str]:
        """List available local models."""
        response = await self._client.list()
        # Ollama returns typed objects, not dicts
        return [model.model for model in response.models]

    async def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            await self._client.list()
            return True
        except Exception:
            return False
