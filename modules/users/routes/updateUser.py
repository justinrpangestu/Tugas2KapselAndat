from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from datetime import datetime
from modules.users.schema.schemas import User, UserUpdate

router = APIRouter()

@router.put("/users/{user_id}", response_model=User)
def update_user(user_id: UUID, user_update: UserUpdate, admin_role: str = Depends(lambda: __import__('main').require_admin_role())):
    from main import fake_users_db # <-- Impor Lokal
    
    db_user = fake_users_db.get(user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db_user.updated_at = datetime.utcnow()
    fake_users_db[user_id] = db_user
    
    return db_user