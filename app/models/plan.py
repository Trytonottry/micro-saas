from sqlalchemy import String, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    monthly_limit: Mapped[int] = mapped_column(Integer)
    price_rub: Mapped[float] = mapped_column(Numeric(10, 2))

    users = relationship("User", back_populates="plan")
