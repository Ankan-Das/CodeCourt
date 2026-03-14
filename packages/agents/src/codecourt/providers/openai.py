"""OpenAI LLM provider implementation."""

import json
from typing import Any

from openai import AsyncOpenAI

from codecourt.config import settings
from codecourt.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """Provider for OpenAI models (GPT-4o, GPT-4, etc.)."""

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or settings.openai_api_key
        self._client = AsyncOpenAI(api_key=self._api_key)
        self._default_model = "gpt-4o"

    @property
    def name(self) -> str:
        return "openai"

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> str:
        response = await self._client.chat.completions.create(
            model=model or self._default_model,
            messages=messages,  # type: ignore
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    async def complete_json(
        self,
        messages: list[dict[str, str]],
        schema: dict[str, Any],
        model: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        system_message = {
            "role": "system",
            "content": f"Respond ONLY with valid JSON matching this schema: {json.dumps(schema)}",
        }
        if messages and messages[0].get("role") != "system":
            messages = [system_message] + messages

        response = await self._client.chat.completions.create(
            model=model or self._default_model,
            messages=messages,  # type: ignore
            response_format={"type": "json_object"},
            **kwargs,
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)
