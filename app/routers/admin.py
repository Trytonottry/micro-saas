from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.task import NotificationTask
from app.models.usage import UsageEvent
from app.models.plan import Plan
from app.services.deps import get_admin_user
from sqlalchemy import func

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/stats")
def stats(_: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    users = db.query(func.count(User.id)).scalar() or 0
    tasks = db.query(func.count(NotificationTask.id)).scalar() or 0
    sent = db.query(func.count(NotificationTask.id)).filter(NotificationTask.status == "sent").scalar() or 0
    usage = db.query(func.coalesce(func.sum(UsageEvent.units), 0)).scalar() or 0
    mrr = db.query(func.coalesce(func.sum(Plan.price_rub), 0)).join(User, User.plan_id == Plan.id).scalar() or 0
    return {"users": users, "tasks": tasks, "sent_tasks": sent, "usage_events": usage, "estimated_mrr_rub": float(mrr)}
