from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from datetime import datetime, UTC
from modules.users.schema.schemas import User, UserUpdate

# Impor dependensi dari file yang benar
from database import fake_users_db
from auth import require_admin_role

router = APIRouter()

@router.put("/users/{user_id}", response_model=User)
def update_user(user_id: UUID, user_update: UserUpdate, admin_role: str = Depends(require_admin_role)):
    """
    Memperbarui data user. Hanya untuk admin.
    """
    db_user = fake_users_db.get(user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    # Gunakan .model_dump() untuk Pydantic v2
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    # Gunakan datetime.now(UTC) untuk zona waktu yang benar
    db_user.updated_at = datetime.now(UTC)
    fake_users_db[user_id] = db_user
    
    return db_user