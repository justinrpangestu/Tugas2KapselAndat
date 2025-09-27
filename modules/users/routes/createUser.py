from fastapi import APIRouter, HTTPException, status
from uuid import uuid4
from modules.users.schema.schemas import User, UserCreate
from database import fake_users_db

router = APIRouter()

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    for existing_user in fake_users_db.values():
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Username already registered")
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    new_user_id = uuid4()
    db_user = User(id=new_user_id, **user.model_dump(exclude={"password"}))
    fake_users_db[new_user_id] = db_user
    return db_user