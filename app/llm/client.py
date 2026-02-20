from __future__ import annotations

import logging
from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from app.config import settings
from app.llm.prompts.system import SYSTEM_PROMPT
from app.middleware.error_handler import LLMError

logger = logging.getLogger(__name__)


class LLMClient:
    """Async Anthropic Claude client wrapper."""

    def __init__(self, client: AsyncAnthropic | None = None):
        self._client = client

    async def generate(self, user_prompt: str) -> str:
        """Generate a complete response (non-streaming)."""
        if self._client is None:
            raise LLMError("Anthropic client not configured. Set ANTHROPIC_API_KEY.")

        try:
            response = await self._client.messages.create(
                model=settings.llm_model,
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text
        except LLMError:
            raise
        except Exception as exc:
            logger.error("LLM generation failed", exc_info=True)
            raise LLMError(f"LLM request failed: {exc}") from exc

    async def generate_stream(self, user_prompt: str) -> AsyncIterator[str]:
        """Generate a streaming response, yielding text chunks."""
        if self._client is None:
            raise LLMError("Anthropic client not configured. Set ANTHROPIC_API_KEY.")

        try:
            async with self._client.messages.stream(
                model=settings.llm_model,
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": user_prompt}],
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except LLMError:
            raise
        except Exception as exc:
            logger.error("LLM streaming failed", exc_info=True)
            raise LLMError(f"LLM stream request failed: {exc}") from exc
