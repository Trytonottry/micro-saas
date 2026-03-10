from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.task import NotificationTask
from app.models.user import User
from app.schemas.task import CreateTaskRequest, TaskResponse
from app.services.deps import get_current_user
from app.services.usage_service import enforce_usage_limit, record_usage
from app.services.queue_service import get_queue
from app.workers.jobs import send_notification

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/notify", response_model=TaskResponse)
def create_notification_task(
    payload: CreateTaskRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    enforce_usage_limit(db, user)

    task = NotificationTask(user_id=user.id, destination=payload.destination, message=payload.message)
    db.add(task)
    db.commit()
    db.refresh(task)

    queue = get_queue("notifications")
    queue.enqueue(send_notification, task.id)

    record_usage(db, user.id)
    return task


@router.get("", response_model=list[TaskResponse])
def list_tasks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(NotificationTask)
        .filter(NotificationTask.user_id == user.id)
        .order_by(NotificationTask.created_at.desc())
        .limit(100)
        .all()
    )
