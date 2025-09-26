import sys
import os
import pytest
from httpx import AsyncClient
from fastapi import status

# Menambahkan direktori utama proyek ke dalam path Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import 'app' dan variabel lain dari main.py untuk diuji
from main import app, fake_users_db, STAFF_USER_ID, API_KEYS

@pytest.fixture(scope="module")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Menjalankan startup event secara manual untuk testing
        await app.router.startup()
        yield client
        await app.router.shutdown()

class TestUserRoutes:
    async def test_create_user_success(self, async_client: AsyncClient):
        user_data = {"username": "testuser", "email": "testuser@example.com", "role": "staff", "password": "Password123!"}
        response = await async_client.post("/users", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == user_data["username"]

    async def test_read_users_as_admin(self, async_client: AsyncClient):
        headers = {"X-API-KEY": "admin_secret_key"}
        response = await async_client.get("/users", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) >= 2

    async def test_read_own_data_as_staff(self, async_client: AsyncClient):
        headers = {"X-API-KEY": "staff_secret_key"}
        response = await async_client.get(f"/users/{STAFF_USER_ID}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == str(STAFF_USER_ID)