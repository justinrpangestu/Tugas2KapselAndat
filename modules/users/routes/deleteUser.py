from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from main import fake_users_db, require_admin_role

router = APIRouter()

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: UUID, admin_role: str = Depends(require_admin_role)):
    """
    Delete a user. Requires admin role. 
    """
    if user_id not in fake_users_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    del fake_users_db[user_id]
    
    return {"message": "User deleted successfully"}