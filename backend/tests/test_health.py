import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient):
    """Verifies that GET /api/v1/health returns 200 OK with valid service payload."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    assert "healthy" in payload["message"].lower()

    data = payload["data"]
    assert data["app_name"] == "CareerLens"
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data
