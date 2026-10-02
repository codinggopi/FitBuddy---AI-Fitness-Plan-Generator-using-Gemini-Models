from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.database import get_db
from app.models import WorkoutPlan, User

router = APIRouter(tags=["Web Pages"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, db: Session = Depends(get_db)):
    plans = (
        db.query(WorkoutPlan)
        .join(User)
        .order_by(WorkoutPlan.created_at.desc())
        .limit(50)
        .all()
    )
    return templates.TemplateResponse("history.html", {"request": request, "plans": plans})


@router.get("/health")
async def health_check():
    return {"status": "ok", "app": "FitBuddy AI", "version": "3.0.0"}
