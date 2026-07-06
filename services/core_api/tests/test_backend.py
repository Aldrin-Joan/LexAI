import pytest
from httpx import AsyncClient
from app.main import app
import json

@pytest.mark.asyncio
async def test_health_check():
    import httpx
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_signup_mock():
    import httpx
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        user_data = {
            "email": "test@legal.com",
            "full_name": "Test User",
            "role": "client",
            "password": "securepassword"
        }
        response = await ac.post("/auth/signup", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == "test@legal.com"
    assert response.json()["role"] == "client"

@pytest.mark.asyncio
async def test_ai_chat_response():
    import httpx
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        query = {"message": "What is Section 420?"}
        response = await ac.post("/legal/ai-chat", json=query)
    assert response.status_code == 200
    assert "response" in response.json()
    assert isinstance(response.json()["response"], str)

@pytest.mark.asyncio
async def test_lawyer_discovery():
    import httpx
    async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/legal/lawyers")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert "name" in response.json()[0]
