from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

router = APIRouter()

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: UUID, admin_role: str = Depends(lambda: __import__('main').require_admin_role())):
    from main import fake_users_db # <-- Impor Lokal
    
    if user_id not in fake_users_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    del fake_users_db[user_id]
    
    return {"message": "User deleted successfully"}