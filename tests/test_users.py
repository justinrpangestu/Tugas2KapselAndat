import pytest
from httpx import AsyncClient
from fastapi import status
from uuid import uuid4

# Import 'app' dari main.py untuk diuji
# Pastikan Python bisa menemukan file main.py
# (Mungkin perlu menambahkan __init__.py di beberapa folder)
from main import app, fake_users_db, STAFF_USER_ID, API_KEYS

# --- Fixtures untuk Setup Testing ---

@pytest.fixture(scope="module")
async def async_client():
    """Membuat client HTTPX untuk melakukan request ke aplikasi."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# --- Kumpulan Test untuk Users Module ---

class TestUserRoutes:
    """Group tests for user-related endpoints."""

    # 1. Test Create User (POST /users)
    async def test_create_user_success(self, async_client: AsyncClient):
        """
        Test 🧪: Berhasil membuat user baru dengan data yang valid.
        Ekspektasi: HTTP Status 201 CREATED dan data user dikembalikan.
        """
        user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "role": "staff",
            "password": "Password123!"
        }
        response = await async_client.post("/users", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data

    async def test_create_user_duplicate_username(self, async_client: AsyncClient):
        """
        Test 🧪: Gagal membuat user karena username sudah ada.
        Ekspektasi: HTTP Status 400 BAD REQUEST.
        """
        # User "johndoe" sudah dibuat saat startup aplikasi
        user_data = {
            "username": "johndoe",
            "email": "another@example.com",
            "role": "staff",
            "password": "Password123!"
        }
        response = await async_client.post("/users", json=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already registered" in response.json()["detail"]

    async def test_create_user_invalid_password(self, async_client: AsyncClient):
        """
        Test 🧪: Gagal membuat user karena password tidak valid.
        Ekspektasi: HTTP Status 422 UNPROCESSABLE ENTITY.
        """
        user_data = {
            "username": "invalidpass",
            "email": "invalid@example.com",
            "role": "staff",
            "password": "weak" # Password tidak memenuhi kriteria
        }
        response = await async_client.post("/users", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # 2. Test Read Users (GET /users)
    async def test_read_users_as_admin(self, async_client: AsyncClient):
        """
        Test 🧪: Admin berhasil mendapatkan semua data user.
        Ekspektasi: HTTP Status 200 OK dan mengembalikan list of users.
        """
        headers = {"X-API-KEY": "admin_secret_key"}
        response = await async_client.get("/users", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        # Harusnya ada lebih dari 1 user (admin & staff default)
        assert len(response.json()) >= 2

    async def test_read_users_as_staff_forbidden(self, async_client: AsyncClient):
        """
        Test 🧪: Staff gagal mendapatkan semua data user.
        Ekspektasi: HTTP Status 403 FORBIDDEN.
        """
        headers = {"X-API-KEY": "staff_secret_key"}
        response = await async_client.get("/users", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # 3. Test Read User by ID (GET /users/{user_id})
    async def test_read_own_data_as_staff(self, async_client: AsyncClient):
        """
        Test 🧪: Staff berhasil mendapatkan data miliknya sendiri.
        Ekspektasi: HTTP Status 200 OK.
        """
        headers = {"X-API-KEY": "staff_secret_key"}
        response = await async_client.get(f"/users/{STAFF_USER_ID}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == str(STAFF_USER_ID)

    async def test_read_other_data_as_staff_forbidden(self, async_client: AsyncClient):
        """
        Test 🧪: Staff gagal mendapatkan data user lain.
        Ekspektasi: HTTP Status 403 FORBIDDEN.
        """
        # Mencari ID admin untuk diakses
        admin_id = None
        for user in fake_users_db.values():
            if user.role == "admin":
                admin_id = user.id
                break
        
        headers = {"X-API-KEY": "staff_secret_key"}
        response = await async_client.get(f"/users/{admin_id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # 4. Test Update User (PUT /users/{user_id})
    async def test_update_user_as_admin(self, async_client: AsyncClient):
        """
        Test 🧪: Admin berhasil memperbarui data user.
        Ekspektasi: HTTP Status 200 OK.
        """
        update_data = {"username": "updatedjohndoe"}
        headers = {"X-API-KEY": "admin_secret_key"}
        response = await async_client.put(f"/users/{STAFF_USER_ID}", json=update_data, headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == "updatedjohndoe"

    # 5. Test Delete User (DELETE /users/{user_id})
    async def test_delete_user_as_admin(self, async_client: AsyncClient):
        """
        Test 🧪: Admin berhasil menghapus user.
        Ekspektasi: HTTP Status 200 OK.
        """
        # Buat user baru untuk dihapus agar tidak mengganggu tes lain
        temp_user_data = {
            "username": "todelete",
            "email": "todelete@example.com",
            "role": "staff",
            "password": "Password123!"
        }
        res_create = await async_client.post("/users", json=temp_user_data)
        user_id_to_delete = res_create.json()["id"]
        
        headers = {"X-API-KEY": "admin_secret_key"}
        response = await async_client.delete(f"/users/{user_id_to_delete}", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Pastikan user sudah tidak ada
        res_get = await async_client.get(f"/users/{user_id_to_delete}", headers=headers)
        assert res_get.status_code == status.HTTP_404_NOT_FOUND