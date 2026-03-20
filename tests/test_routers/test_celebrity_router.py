from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCelebritySearchEndpoint:
    async def test_search_by_korean_name(self, client: AsyncClient):
        response = await client.get("/api/v1/celebrity/search", params={"q": "카리나"})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == "karina-aespa"
        assert data["results"][0]["name_ko"] == "카리나"
        assert data["results"][0]["group"] == "aespa"

    async def test_search_by_english_name(self, client: AsyncClient):
        response = await client.get("/api/v1/celebrity/search", params={"q": "Jungkook"})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["id"] == "jungkook-bts"

    async def test_search_by_group(self, client: AsyncClient):
        response = await client.get("/api/v1/celebrity/search", params={"q": "aespa"})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 4

    async def test_search_no_results(self, client: AsyncClient):
        response = await client.get("/api/v1/celebrity/search", params={"q": "nonexistent"})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    async def test_search_missing_query(self, client: AsyncClient):
        response = await client.get("/api/v1/celebrity/search")
        assert response.status_code == 422


@pytest.mark.asyncio
class TestCelebrityCompatibilityEndpoint:
    """Integration tests for celebrity compatibility endpoint.

    LLM client is mocked since it's unavailable in test environment.
    """

    @patch("app.llm.client.LLMClient.generate", new_callable=AsyncMock)
    async def test_compatibility_returns_calculation(
        self, mock_generate: AsyncMock, client: AsyncClient,
    ):
        """Compatibility should return saju data for both user and celebrity."""
        mock_generate.return_value = "Mock interpretation"
        response = await client.post(
            "/api/v1/celebrity/compatibility",
            json={
                "birth": {
                    "year": 1995,
                    "month": 5,
                    "day": 15,
                    "hour": 14,
                    "gender": "male",
                },
                "celebrity_id": "karina-aespa",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # User saju should have time pillar (hour provided)
        assert data["user"]["time_pillar"] is not None
        # Celebrity saju should NOT have time pillar (hour unknown)
        assert data["celebrity"]["time_pillar"] is None
        assert data["celebrity"]["birth_time_unknown"] is True

    @patch("app.llm.client.LLMClient.generate", new_callable=AsyncMock)
    async def test_compatibility_returns_celebrity_info(
        self, mock_generate: AsyncMock, client: AsyncClient,
    ):
        mock_generate.return_value = "Mock interpretation"
        response = await client.post(
            "/api/v1/celebrity/compatibility",
            json={
                "birth": {
                    "year": 1995,
                    "month": 5,
                    "day": 15,
                    "gender": "male",
                },
                "celebrity_id": "karina-aespa",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["celebrity_info"]["id"] == "karina-aespa"
        assert data["celebrity_info"]["name_ko"] == "카리나"
        assert data["celebrity_info"]["name_en"] == "Karina"
        assert data["celebrity_info"]["group"] == "aespa"

    @patch("app.llm.client.LLMClient.generate", new_callable=AsyncMock)
    async def test_compatibility_has_disclaimer(
        self, mock_generate: AsyncMock, client: AsyncClient,
    ):
        mock_generate.return_value = "Mock interpretation"
        response = await client.post(
            "/api/v1/celebrity/compatibility",
            json={
                "birth": {
                    "year": 1995,
                    "month": 5,
                    "day": 15,
                    "gender": "male",
                },
                "celebrity_id": "karina-aespa",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "disclaimer" in data
        assert len(data["disclaimer"]) > 0

    @patch("app.llm.client.LLMClient.generate", new_callable=AsyncMock)
    async def test_compatibility_interpretation_from_llm(
        self, mock_generate: AsyncMock, client: AsyncClient,
    ):
        mock_generate.return_value = "Test celebrity compatibility interpretation"
        response = await client.post(
            "/api/v1/celebrity/compatibility",
            json={
                "birth": {
                    "year": 1995,
                    "month": 5,
                    "day": 15,
                    "gender": "male",
                },
                "celebrity_id": "karina-aespa",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["interpretation"]["summary"] == "Test celebrity compatibility interpretation"
        mock_generate.assert_called_once()

    async def test_compatibility_invalid_celebrity_id(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/celebrity/compatibility",
            json={
                "birth": {
                    "year": 1995,
                    "month": 5,
                    "day": 15,
                    "gender": "male",
                },
                "celebrity_id": "nonexistent-idol",
            },
        )
        assert response.status_code == 404

    async def test_compatibility_missing_birth(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/celebrity/compatibility",
            json={"celebrity_id": "karina-aespa"},
        )
        assert response.status_code == 422

    async def test_compatibility_missing_celebrity_id(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/celebrity/compatibility",
            json={
                "birth": {
                    "year": 1995,
                    "month": 5,
                    "day": 15,
                    "gender": "male",
                },
            },
        )
        assert response.status_code == 422
