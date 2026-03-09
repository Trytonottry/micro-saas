from datetime import datetime
from pydantic import BaseModel, EmailStr


class CreateTaskRequest(BaseModel):
    destination: EmailStr
    message: str


class TaskResponse(BaseModel):
    id: int
    destination: str
    message: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
