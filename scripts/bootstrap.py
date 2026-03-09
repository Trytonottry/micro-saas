from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.plan import Plan
from app.models.user import User
from app.core.security import hash_password


def ensure_plans(db: Session):
    plans = [
        ("starter", settings.starter_monthly_limit, 490),
        ("growth", settings.growth_monthly_limit, 1490),
        ("pro", settings.pro_monthly_limit, 4990),
    ]
    for name, limit, price in plans:
        exists = db.query(Plan).filter(Plan.name == name).first()
        if not exists:
            db.add(Plan(name=name, monthly_limit=limit, price_rub=price))
    db.commit()


def ensure_admin(db: Session):
    admin = db.query(User).filter(User.email == settings.admin_email).first()
    if admin:
        return
    starter = db.query(Plan).filter(Plan.name == settings.default_plan_name).first()
    db.add(
        User(
            email=settings.admin_email,
            full_name="Platform Admin",
            hashed_password=hash_password(settings.admin_password),
            plan_id=starter.id,
            is_admin=True,
        )
    )
    db.commit()


def main():
    db = SessionLocal()
    try:
        ensure_plans(db)
        ensure_admin(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
