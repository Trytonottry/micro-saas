import logging
from app.core.database import SessionLocal
from app.models.task import NotificationTask

logger = logging.getLogger(__name__)


def send_notification(task_id: int) -> None:
    db = SessionLocal()
    try:
        task = db.query(NotificationTask).filter(NotificationTask.id == task_id).first()
        if not task:
            logger.error("Task not found", extra={"task_id": task_id})
            return

        logger.info(
            "Notification sent",
            extra={"destination": task.destination, "task_id": task.id},
        )
        task.status = "sent"
        db.commit()
    except Exception as exc:
        logger.exception("Failed task", extra={"task_id": task_id, "error": str(exc)})
        if 'task' in locals() and task:
            task.status = "failed"
            db.commit()
        raise
    finally:
        db.close()
