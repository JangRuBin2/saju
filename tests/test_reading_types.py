"""Tests for reading-type prompt selection and token validation changes."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.llm.prompts.reading_types import (
    FRIENDSHIP_READING_PROMPT,
    LOVE_READING_PROMPT,
    MARRIAGE_READING_PROMPT,
    SINSAL_READING_PROMPT,
    get_prompt_for_type,
)
from app.llm.prompts.saju_reading import SAJU_READING_PROMPT


class TestGetPromptForType:
    def test_saju_reading_returns_default_prompt(self):
        result = get_prompt_for_type("saju_reading")
        assert result is SAJU_READING_PROMPT

    def test_love_reading_prompt(self):
        result = get_prompt_for_type("love_reading")
        assert result is LOVE_READING_PROMPT

    def test_friendship_reading_prompt(self):
        result = get_prompt_for_type("friendship_reading")
        assert result is FRIENDSHIP_READING_PROMPT

    def test_marriage_reading_prompt(self):
        result = get_prompt_for_type("marriage_reading")
        assert result is MARRIAGE_READING_PROMPT

    def test_sinsal_prompt(self):
        result = get_prompt_for_type("sinsal")
        assert result is SINSAL_READING_PROMPT

    def test_unknown_type_falls_back_to_saju_reading(self):
        result = get_prompt_for_type("unknown_type")
        assert result is SAJU_READING_PROMPT

    def test_empty_string_falls_back_to_saju_reading(self):
        result = get_prompt_for_type("")
        assert result is SAJU_READING_PROMPT

    def test_all_prompts_have_saju_data_placeholder(self):
        for reading_type in ("saju_reading", "love_reading", "friendship_reading",
                             "marriage_reading", "sinsal"):
            prompt = get_prompt_for_type(reading_type)
            assert "{saju_data}" in prompt, f"{reading_type} prompt missing {{saju_data}}"


def _make_service_token(
    user_id: str,
    reading_type: str,
    secret_key: str,
    timestamp: int | None = None,
) -> str:
    """Create a valid HMAC service token for testing."""
    ts = timestamp if timestamp is not None else int(time.time())
    payload = {
        "user_id": user_id,
        "reading_type": reading_type,
        "timestamp": ts,
        "nonce": "test-nonce",
    }
    message = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    signature = hmac.new(
        secret_key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    payload["signature"] = signature
    return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")


@pytest.mark.asyncio
class TestTokenValidatorWithReadingType:
    @pytest.fixture
    async def token_client(self):
        from app.main import app
        from app import dependencies
        from app.engine.calculator import SajuCalculator
        from app.llm.client import LLMClient
        from app.services.cache_service import CacheService
        from app.services.saju_service import SajuService
        from app.services.compatibility_service import CompatibilityService
        from app.services.fortune_service import FortuneService

        original_require = settings.require_service_token
        original_key = settings.api_secret_key
        settings.require_service_token = True
        settings.api_secret_key = "test-secret-key"

        dependencies._calculator = SajuCalculator()
        dependencies._llm_client = LLMClient(None)
        dependencies._cache_service = CacheService(None)
        dependencies._saju_service = SajuService(
            dependencies._calculator,
            dependencies._llm_client,
            dependencies._cache_service,
        )
        dependencies._compatibility_service = CompatibilityService(
            dependencies._calculator,
            dependencies._llm_client,
            dependencies._cache_service,
        )
        dependencies._fortune_service = FortuneService(
            dependencies._calculator,
            dependencies._llm_client,
            dependencies._cache_service,
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

        settings.require_service_token = original_require
        settings.api_secret_key = original_key

    async def test_request_without_token_returns_401(self, token_client: AsyncClient):
        response = await token_client.post(
            "/api/v1/saju/calculate",
            json={
                "birth": {
                    "year": 1990, "month": 5, "day": 15,
                    "hour": 14, "gender": "male",
                }
            },
        )
        assert response.status_code == 401

    async def test_valid_token_with_reading_type(self, token_client: AsyncClient):
        token = _make_service_token("user-1", "love_reading", "test-secret-key")
        response = await token_client.post(
            "/api/v1/saju/calculate",
            json={
                "birth": {
                    "year": 1990, "month": 5, "day": 15,
                    "hour": 14, "gender": "male",
                }
            },
            headers={"X-Service-Token": token},
        )
        assert response.status_code == 200

    async def test_expired_token_returns_401(self, token_client: AsyncClient):
        old_timestamp = int(time.time()) - 600  # 10 minutes ago
        token = _make_service_token(
            "user-1", "saju_reading", "test-secret-key", timestamp=old_timestamp
        )
        response = await token_client.post(
            "/api/v1/saju/calculate",
            json={
                "birth": {
                    "year": 1990, "month": 5, "day": 15,
                    "hour": 14, "gender": "male",
                }
            },
            headers={"X-Service-Token": token},
        )
        assert response.status_code == 401

    async def test_invalid_signature_returns_401(self, token_client: AsyncClient):
        token = _make_service_token("user-1", "saju_reading", "wrong-secret-key")
        response = await token_client.post(
            "/api/v1/saju/calculate",
            json={
                "birth": {
                    "year": 1990, "month": 5, "day": 15,
                    "hour": 14, "gender": "male",
                }
            },
            headers={"X-Service-Token": token},
        )
        assert response.status_code == 401

    async def test_health_endpoint_skips_token_validation(self, token_client: AsyncClient):
        response = await token_client.get("/health")
        assert response.status_code == 200
