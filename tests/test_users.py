import sys
import os
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from uuid import uuid4

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database import fake_users_db
from modules.users.schema.schemas import User
from auth import STAFF_USER_ID, API_KEYS

@pytest.fixture(scope="function")
async def async_client():
    # SETUP: Berjalan sebelum SETIAP tes
    fake_users_db.clear()
    admin_id = uuid4()
    fake_users_db[admin_id] = User(id=admin_id, username="superadmin", email="admin@example.com", role="admin")
    fake_users_db[STAFF_USER_ID] = User(id=STAFF_USER_ID, username="johndoe", email="john.doe@example.com", role="staff")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    # TEARDOWN: Berjalan setelah SETIAP tes
    fake_users_db.clear()

@pytest.mark.anyio
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