from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Dict
from uuid import UUID, uuid4
from datetime import datetime

# Import schema dan semua router
from modules.users.schema.schemas import User, UserCreate, UserUpdate
from modules.users.routes import createUser, readUser, updateUser, deleteUser

app = FastAPI(title="User Management API")

# =============================================================================
# SEMUA LOGIKA BERSAMA ADA DI SINI
# =============================================================================

# 1. Database In-Memory Sederhana
fake_users_db: Dict[UUID, User] = {}

# 2. Otentikasi Sederhana
API_KEYS = {
    "admin_secret_key": "admin",
    "staff_secret_key": "staff",
}
STAFF_USER_ID = uuid4()

def get_user_role(x_api_key: str = Header(...)):
    role = API_KEYS.get(x_api_key)
    if not role:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return role

def require_admin_role(role: str = Depends(get_user_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return role

# =============================================================================
# Inisialisasi Data Awal
# =============================================================================
@app.on_event("startup")
def startup_event():
    admin_id = uuid4()
    fake_users_db[admin_id] = User(id=admin_id, username="superadmin", email="admin@example.com", role="admin")
    fake_users_db[STAFF_USER_ID] = User(id=STAFF_USER_ID, username="johndoe", email="john.doe@example.com", role="staff")

# =============================================================================
# Menggabungkan Routers
# =============================================================================
app.include_router(createUser.router, tags=["Users"])
app.include_router(readUser.router, tags=["Users"])
app.include_router(updateUser.router, tags=["Users"])
app.include_router(deleteUser.router, tags=["Users"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the User Management API"}