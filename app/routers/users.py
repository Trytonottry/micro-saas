from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.deps import get_current_user
from app.services.usage_service import get_month_usage

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_admin=user.is_admin,
        plan_name=user.plan.name,
        created_at=user.created_at,
    )


@router.get("/me/usage")
def my_usage(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    used = get_month_usage(db, user.id)
    return {
        "used": used,
        "limit": user.plan.monthly_limit,
        "remaining": max(user.plan.monthly_limit - used, 0),
    }
