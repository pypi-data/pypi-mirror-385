import pytest
from fastapi import status

from market_data_core.services.api import app


@pytest.mark.asyncio  # type: ignore[misc]
async def test_health() -> None:
    from fastapi.testclient import TestClient

    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == status.HTTP_200_OK
    # When IBKR is not running, status should be "disconnected"
    health_data = r.json()
    assert health_data["status"] in ["ok", "disconnected"]
