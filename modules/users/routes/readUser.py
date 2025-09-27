from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from modules.users.schema.schemas import User

# Impor dependensi dari file yang benar (bukan lagi 'main')
from database import fake_users_db
from auth import get_user_role, require_admin_role, STAFF_USER_ID

router = APIRouter()

@router.get("/users", response_model=List[User])
def read_users(admin_role: str = Depends(require_admin_role)):
    """
    Mengambil semua data user. Hanya untuk admin.
    """
    return list(fake_users_db.values())


@router.get("/users/{user_id}", response_model=User)
def read_user_by_id(user_id: UUID, role: str = Depends(get_user_role)):
    """
    Mengambil data satu user berdasarkan ID.
    - Admin bisa mengambil data user mana pun.
    - Staff hanya bisa mengambil datanya sendiri.
    """
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if role == "admin" or (role == "staff" and user_id == STAFF_USER_ID):
        return user
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")