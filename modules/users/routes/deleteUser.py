from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

# Impor dependensi dari file yang benar
from database import fake_users_db
from auth import require_admin_role

router = APIRouter()

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: UUID, admin_role: str = Depends(require_admin_role)):
    """
    Menghapus user. Hanya untuk admin.
    """
    if user_id not in fake_users_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    del fake_users_db[user_id]
    
    return {"message": "User deleted successfully"}