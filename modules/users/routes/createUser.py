from fastapi import APIRouter, HTTPException, status
from uuid import uuid4
from datetime import datetime
from main import fake_users_db # Import database dari main.py
from modules.users.schema.schemas import User, UserCreate

router = APIRouter()

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """
    Create a new user. This endpoint is public.
    """
    # Cek apakah username atau email sudah ada
    for existing_user in fake_users_db.values():
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Username already registered")
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    new_user_id = uuid4()
    # Kita tidak menyimpan password, ini hanya contoh.
    # Di aplikasi nyata, password harus di-hash.
    db_user = User(
        id=new_user_id,
        **user.dict(exclude={"password"}) # Exclude password from the stored data model
    )
    fake_users_db[new_user_id] = db_user
    return db_user