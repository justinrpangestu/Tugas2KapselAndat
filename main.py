from fastapi import FastAPI
from contextlib import asynccontextmanager
from uuid import uuid4
from database import fake_users_db
from auth import STAFF_USER_ID
from modules.users.schema.schemas import User
from modules.users.routes import createUser, readUser, updateUser, deleteUser

@asynccontextmanager
async def lifespan(app: FastAPI):
    admin_id = uuid4()
    fake_users_db[admin_id] = User(id=admin_id, username="superadmin", email="admin@example.com", role="admin")
    fake_users_db[STAFF_USER_ID] = User(id=STAFF_USER_ID, username="johndoe", email="john.doe@example.com", role="staff")
    yield

app = FastAPI(title="User Management API", lifespan=lifespan)

app.include_router(createUser.router, tags=["Users"])
app.include_router(readUser.router, tags=["Users"])
app.include_router(updateUser.router, tags=["Users"])
app.include_router(deleteUser.router, tags=["Users"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the User Management API"}