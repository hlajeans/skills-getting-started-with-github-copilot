
import pytest
import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from app import app
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_activities():
    # Arrange
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act
        response = await ac.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


@pytest.mark.asyncio
async def test_signup_and_remove_participant():
    # Arrange
    test_email = "testuser@mergington.edu"
    activity = "Art Club"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act: signup
        signup_resp = await ac.post(f"/activities/{activity}/signup", params={"email": test_email})
        # Assert signup
        assert signup_resp.status_code == 200
        assert f"Signed up {test_email}" in signup_resp.json()["message"]
        # Act: remove
        remove_resp = await ac.delete(f"/activities/{activity}/participant", params={"email": test_email})
        # Assert remove
        assert remove_resp.status_code == 200
        assert f"Removed {test_email}" in remove_resp.json()["message"]


@pytest.mark.asyncio
async def test_signup_duplicate_participant():
    # Arrange
    test_email = "duplicate@mergington.edu"
    activity = "Drama Club"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act: signup first time
        resp1 = await ac.post(f"/activities/{activity}/signup", params={"email": test_email})
        # Assert first signup
        assert resp1.status_code == 200
        # Act: signup again (should fail)
        resp2 = await ac.post(f"/activities/{activity}/signup", params={"email": test_email})
        # Assert duplicate
        assert resp2.status_code == 400
        assert "already signed up" in resp2.json()["detail"].lower()
        # Cleanup
        await ac.delete(f"/activities/{activity}/participant", params={"email": test_email})

@pytest.mark.asyncio
async def test_remove_nonexistent_participant():
    # Arrange
    test_email = "notfound@mergington.edu"
    activity = "Science Club"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Act
        resp = await ac.delete(f"/activities/{activity}/participant", params={"email": test_email})
        # Assert
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()
