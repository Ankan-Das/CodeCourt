"""Ollama LLM provider implementation for local models."""

import json
from typing import Any

from ollama import AsyncClient

from codecourt.config import settings
from codecourt.providers.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Provider for local models via Ollama (Llama 3, Mistral, CodeLlama, etc.)."""

    def __init__(self, host: str | None = None) -> None:
        """
        Initialize the Ollama provider.

        Args:
            host: Ollama server URL. Default: http://localhost:11434
        """
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
        """
        Generate a completion from a local Ollama model.

        Args:
            messages: List of messages [{"role": "user", "content": "..."}]
            model: Model to use (default: llama3). Must be pulled first!
            temperature: Randomness (0 = deterministic, 1 = creative)
            max_tokens: Maximum response length (called num_predict in Ollama)

        Returns:
            The model's response as a string.
        """
        response = await self._client.chat(
            model=model or self._default_model,
            messages=messages,  # type: ignore
            options={
                "temperature": temperature,
                "num_predict": max_tokens,
            },
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
        """
        Generate a JSON-structured completion.

        Local models need strong prompting to return valid JSON.
        """
        # Add strong JSON instruction
        json_instruction = f"""

IMPORTANT: You must respond with ONLY valid JSON, no other text.
The JSON must match this exact schema:
{json.dumps(schema, indent=2)}

Do not include markdown code blocks, explanations, or any other text.
Just the raw JSON object."""

        modified_messages = messages.copy()
        if modified_messages:
            last_msg = modified_messages[-1].copy()
            last_msg["content"] += json_instruction
            modified_messages[-1] = last_msg

        # Use format parameter if available (newer Ollama versions)
        response = await self._client.chat(
            model=model or self._default_model,
            messages=modified_messages,  # type: ignore
            format="json",  # Ollama's JSON mode
            **kwargs,
        )

        content = response["message"]["content"]

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            # Try to extract JSON from response
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                try:
                    return json.loads(content[start:end])
                except json.JSONDecodeError:
                    pass
            return {}

    async def list_models(self) -> list[str]:
        """List all models available locally."""
        response = await self._client.list()
        return [model["name"] for model in response["models"]]

    async def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            await self._client.list()
            return True
        except Exception:
            return False
