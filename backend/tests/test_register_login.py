import pytest
import pytest_asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import hash_password

@pytest.mark.asyncio
async def test_register_user(client, register_payload):
    resp = await client.post("/auth/register", json=register_payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data.get("message") == "Użytkownik utworzony pomyślnie"

@pytest.mark.asyncio
async def test_login_user(client, register_payload):
    await client.post("/auth/register", json=register_payload)

    payload = {
            "email": "user@example.com",
            "password": "string123",
            }
    resp = await client.post("/auth/login", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
