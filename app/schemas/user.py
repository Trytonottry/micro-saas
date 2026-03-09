from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_admin: bool
    plan_name: str
    created_at: datetime

    class Config:
        from_attributes = True
