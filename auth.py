from fastapi import Depends, HTTPException, Header
from uuid import uuid4

API_KEYS = {
    "admin_secret_key": "admin",
    "staff_secret_key": "staff",
}
STAFF_USER_ID = uuid4()

def get_user_role(x_api_key: str = Header(...)):
    role = API_KEYS.get(x_api_key)
    if not role:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return role

def require_admin_role(role: str = Depends(get_user_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return role