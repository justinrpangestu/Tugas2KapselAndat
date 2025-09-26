from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Dict, List
from uuid import UUID, uuid4
from datetime import datetime

# Import schema dan router
from modules.users.schema.schemas import User, UserCreate, UserUpdate
from modules.users.routes import createUser, readUser, updateUser, deleteUser

app = FastAPI(title="User Management API")

# =============================================================================
# Database In-Memory Sederhana
# =============================================================================
# Kita gunakan dictionary sebagai database sementara.
# Key: user_id (UUID), Value: User object
fake_users_db: Dict[UUID, User] = {}

# =============================================================================
# Otentikasi Sederhana (Tanpa JWT) [cite: 22]
# =============================================================================
# Simulasikan API keys dan rolenya
API_KEYS = {
    "admin_secret_key": "admin",
    "staff_secret_key": "staff",
}

# Simulasikan user ID yang terhubung dengan API key staff
STAFF_USER_ID = uuid4() # ID ini akan kita gunakan untuk user staff pertama

def get_user_role(x_api_key: str = Header(...)):
    """Dependency untuk mendapatkan role dari API Key."""
    role = API_KEYS.get(x_api_key)
    if not role:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return role

def require_admin_role(role: str = Depends(get_user_role)):
    """Dependency untuk memastikan user adalah admin."""
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required") [cite: 20]
    return role

# =============================================================================
# Inisialisasi Data Awal (untuk testing)
# =============================================================================
@app.on_event("startup")
def startup_event():
    # Buat user admin
    admin_id = uuid4()
    fake_users_db[admin_id] = User(
        id=admin_id,
        username="superadmin",
        email="admin@example.com",
        role="admin",
    )
    # Buat user staff yang terhubung dengan staff_secret_key
    fake_users_db[STAFF_USER_ID] = User(
        id=STAFF_USER_ID,
        username="johndoe",
        email="john.doe@example.com",
        role="staff",
    )
    print("--- Server Started ---")
    print("Admin API Key: admin_secret_key")
    print(f"Admin User ID: {admin_id}")
    print("Staff API Key: staff_secret_key")
    print(f"Staff User ID: {STAFF_USER_ID}")
    print("----------------------")


# =============================================================================
# Menggabungkan Routers
# =============================================================================
# Kita akan membuat file-file ini selanjutnya
app.include_router(createUser.router, tags=["Users"])
app.include_router(readUser.router, tags=["Users"])
app.include_router(updateUser.router, tags=["Users"])
app.include_router(deleteUser.router, tags=["Users"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the User Management API"}