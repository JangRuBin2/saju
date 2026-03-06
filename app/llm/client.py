from __future__ import annotations

import logging
from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from app.config import settings
from app.llm.model_router import get_model_for_type
from app.llm.prompts.system import SYSTEM_PROMPT
from app.middleware.error_handler import LLMError

logger = logging.getLogger(__name__)


class LLMClient:
    """Async Anthropic Claude client wrapper."""

    def __init__(self, client: AsyncAnthropic | None = None):
        self._client = client

    @staticmethod
    def _apply_language(prompt: str, language: str) -> str:
        """Prepend a language instruction when language is not Korean."""
        if language == "ko":
            return prompt
        return f"[IMPORTANT: You MUST respond entirely in {language}.]\n\n{prompt}"

    async def generate(
        self,
        user_prompt: str,
        *,
        reading_type: str = "saju_reading",
        language: str = "ko",
    ) -> str:
        """Generate a complete response (non-streaming)."""
        if self._client is None:
            raise LLMError("Anthropic client not configured. Set ANTHROPIC_API_KEY.")

        model = get_model_for_type(reading_type)
        final_prompt = self._apply_language(user_prompt, language)
        try:
            response = await self._client.messages.create(
                model=model,
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": final_prompt}],
            )
            return response.content[0].text
        except LLMError:
            raise
        except Exception as exc:
            logger.error("LLM generation failed", exc_info=True)
            raise LLMError(f"LLM request failed: {exc}") from exc

    async def generate_stream(
        self,
        user_prompt: str,
        *,
        reading_type: str = "saju_reading",
        language: str = "ko",
    ) -> AsyncIterator[str]:
        """Generate a streaming response, yielding text chunks."""
        if self._client is None:
            raise LLMError("Anthropic client not configured. Set ANTHROPIC_API_KEY.")

        model = get_model_for_type(reading_type)
        final_prompt = self._apply_language(user_prompt, language)
        try:
            async with self._client.messages.stream(
                model=model,
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": final_prompt}],
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except LLMError:
            raise
        except Exception as exc:
            logger.error("LLM streaming failed", exc_info=True)
            raise LLMError(f"LLM stream request failed: {exc}") from exc
