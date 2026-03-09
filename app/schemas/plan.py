from pydantic import BaseModel


class PlanResponse(BaseModel):
    id: int
    name: str
    monthly_limit: int
    price_rub: float

    class Config:
        from_attributes = True
