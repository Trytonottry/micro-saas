from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.plan import Plan

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    plans = db.query(Plan).all()
    return templates.TemplateResponse("index.html", {"request": request, "plans": plans})
