"""OpenAI LLM provider implementation."""

import json
from typing import Any

from openai import AsyncOpenAI

from codecourt.config import settings
from codecourt.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """Provider for OpenAI models (GPT-4o, GPT-4, etc.)."""

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize the OpenAI provider.

        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY from env.
        """
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
        """
        Generate a completion from OpenAI.

        Args:
            messages: List of messages [{"role": "user", "content": "..."}]
            model: Model to use (default: gpt-4o)
            temperature: Randomness (0 = deterministic, 1 = creative)
            max_tokens: Maximum response length

        Returns:
            The model's response as a string.
        """
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
        """
        Generate a JSON-structured completion.

        Args:
            messages: List of messages
            schema: JSON schema the response should follow
            model: Model to use

        Returns:
            Parsed JSON response as a dictionary.
        """
        # Add instruction to return JSON
        system_message = {
            "role": "system",
            "content": f"Respond ONLY with valid JSON matching this schema: {json.dumps(schema)}",
        }

        # Prepend system message if not already present
        if messages and messages[0].get("role") != "system":
            messages = [system_message] + messages
        else:
            messages[0]["content"] += f"\n\nRespond with JSON matching: {json.dumps(schema)}"

        response = await self._client.chat.completions.create(
            model=model or self._default_model,
            messages=messages,  # type: ignore
            response_format={"type": "json_object"},
            **kwargs,
        )

        content = response.choices[0].message.content or "{}"
        return json.loads(content)
