from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

# Import dependencies, database, dan schema
from main import fake_users_db, get_user_role, require_admin_role, STAFF_USER_ID
from modules.users.schema.schemas import User

router = APIRouter()

@router.get("/users", response_model=List[User])
def read_users(admin_role: str = Depends(require_admin_role)):
    """
    Retrieve all users. Requires admin role. 
    """
    return list(fake_users_db.values())


@router.get("/users/{user_id}", response_model=User)
def read_user_by_id(user_id: UUID, role: str = Depends(get_user_role)):
    """
    Retrieve a single user by ID.
    - Admins can retrieve any user. 
    - Staff can only retrieve their own data. 
    """
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if role == "admin":
        return user
    
    # Untuk staff, cek apakah ID yang diminta adalah ID miliknya
    if role == "staff" and user_id == STAFF_USER_ID:
        return user
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this user's data")