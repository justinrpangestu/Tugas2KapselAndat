from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from modules.users.schema.schemas import User

router = APIRouter()

@router.get("/users", response_model=List[User])
def read_users(admin_role: str = Depends(lambda: __import__('main').require_admin_role())):
    from main import fake_users_db # <-- Impor Lokal
    return list(fake_users_db.values())

@router.get("/users/{user_id}", response_model=User)
def read_user_by_id(user_id: UUID, role: str = Depends(lambda: __import__('main').get_user_role())):
    from main import fake_users_db, STAFF_USER_ID # <-- Impor Lokal
    
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if role == "admin" or (role == "staff" and user_id == STAFF_USER_ID):
        return user
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")