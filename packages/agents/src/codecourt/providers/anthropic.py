"""Anthropic LLM provider implementation."""

import json
from typing import Any

from anthropic import AsyncAnthropic

from codecourt.config import settings
from codecourt.providers.base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Provider for Anthropic models (Claude 3.5 Sonnet, etc.)."""

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or settings.anthropic_api_key
        self._client = AsyncAnthropic(api_key=self._api_key)
        self._default_model = "claude-3-5-sonnet-20241022"

    @property
    def name(self) -> str:
        return "anthropic"

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any,
    ) -> str:
        system_content = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                chat_messages.append(msg)

        response = await self._client.messages.create(
            model=model or self._default_model,
            max_tokens=max_tokens,
            system=system_content if system_content else None,  # type: ignore
            messages=chat_messages,  # type: ignore
            temperature=temperature,
            **kwargs,
        )
        return response.content[0].text if response.content else ""

    async def complete_json(
        self,
        messages: list[dict[str, str]],
        schema: dict[str, Any],
        model: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        json_instruction = f"\n\nRespond ONLY with valid JSON matching: {json.dumps(schema)}"
        modified_messages = messages.copy()
        if modified_messages:
            last_msg = modified_messages[-1].copy()
            last_msg["content"] += json_instruction
            modified_messages[-1] = last_msg

        response = await self.complete(modified_messages, model=model, **kwargs)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response.strip())
        except json.JSONDecodeError:
            return {}
