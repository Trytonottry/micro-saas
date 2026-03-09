from datetime import datetime
from sqlalchemy import extract, func
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.usage import UsageEvent
from app.models.user import User


def get_month_usage(db: Session, user_id: int) -> int:
    now = datetime.utcnow()
    used = db.query(func.coalesce(func.sum(UsageEvent.units), 0)).filter(
        UsageEvent.user_id == user_id,
        extract("year", UsageEvent.created_at) == now.year,
        extract("month", UsageEvent.created_at) == now.month,
    ).scalar()
    return int(used or 0)


def enforce_usage_limit(db: Session, user: User) -> None:
    used = get_month_usage(db, user.id)
    if used >= user.plan.monthly_limit:
        raise HTTPException(status_code=402, detail="Monthly plan limit exceeded")


def record_usage(db: Session, user_id: int, units: int = 1, event_type: str = "notification") -> None:
    event = UsageEvent(user_id=user_id, units=units, event_type=event_type)
    db.add(event)
    db.commit()
