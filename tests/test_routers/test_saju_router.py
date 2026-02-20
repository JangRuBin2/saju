from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoint:
    async def test_health(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
class TestSajuCalculateEndpoint:
    async def test_calculate_solar(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/saju/calculate",
            json={
                "birth": {
                    "year": 1990,
                    "month": 5,
                    "day": 15,
                    "hour": 14,
                    "minute": 30,
                    "gender": "male",
                    "calendar_type": "solar",
                }
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["day_master"] == "庚"
        assert data["day_master_element"] == "金"
        assert data["year_pillar"]["gan"] == "庚"
        assert data["year_pillar"]["zhi"] == "午"
        assert data["time_pillar"] is not None

    async def test_calculate_without_time(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/saju/calculate",
            json={
                "birth": {
                    "year": 1990,
                    "month": 5,
                    "day": 15,
                    "gender": "female",
                    "calendar_type": "solar",
                }
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["time_pillar"] is None
        assert data["birth_time_unknown"] is True

    async def test_calculate_lunar(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/saju/calculate",
            json={
                "birth": {
                    "year": 1990,
                    "month": 4,
                    "day": 21,
                    "hour": 14,
                    "gender": "male",
                    "calendar_type": "lunar",
                }
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["solar_date"] == "1990-05-15"

    async def test_calculate_invalid_date(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/saju/calculate",
            json={
                "birth": {
                    "year": 1990,
                    "month": 13,
                    "day": 15,
                    "gender": "male",
                }
            },
        )
        assert response.status_code == 422

    async def test_calculate_response_has_element_counts(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/saju/calculate",
            json={
                "birth": {
                    "year": 1990,
                    "month": 5,
                    "day": 15,
                    "hour": 14,
                    "gender": "male",
                }
            },
        )
        assert response.status_code == 200
        data = response.json()
        counts = data["element_counts"]
        assert set(counts.keys()) == {"木", "火", "土", "金", "水"}
        assert sum(counts.values()) == 8

    async def test_calculate_response_has_da_yun(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/saju/calculate",
            json={
                "birth": {
                    "year": 1990,
                    "month": 5,
                    "day": 15,
                    "hour": 14,
                    "gender": "male",
                }
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["da_yun_list"]) > 0
        assert "start_age" in data["da_yun_list"][0]
        assert "gan_zhi" in data["da_yun_list"][0]
