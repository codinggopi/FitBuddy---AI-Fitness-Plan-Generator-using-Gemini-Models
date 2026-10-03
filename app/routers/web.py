from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
import json

from app.database import get_db
from app.models import WorkoutPlan, User

router = APIRouter(tags=["Web Pages"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, db: Session = Depends(get_db)):
    plans = (
        db.query(WorkoutPlan)
        .join(User)
        .order_by(WorkoutPlan.created_at.desc())
        .limit(50)
        .all()
    )
    return templates.TemplateResponse(request, "history.html", {"plans": plans})


@router.get("/view-all-users", response_class=HTMLResponse)
@router.get("/admin", response_class=HTMLResponse)
async def view_all_users_page(request: Request, db: Session = Depends(get_db)):
    orm_users = db.query(User).order_by(User.id.desc()).all()
    users_data = []
    for u in orm_users:
        latest_plan = u.plans[-1] if u.plans else None
        users_data.append({
            "id": u.id,
            "name": u.name,
            "user_id": f"USR-{u.id:04d}",
            "age": u.age,
            "weight": u.weight,
            "goal": u.goal,
            "intensity": u.intensity,
            "original_plan": latest_plan.plan_json if latest_plan else "",
            "updated_plan": "",
            "plan_id": latest_plan.id if latest_plan else None,
        })
    return templates.TemplateResponse(request, "all_users.html", {"users": users_data})


@router.get("/result/{plan_id}", response_class=HTMLResponse)
async def result_page(request: Request, plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    try:
        workout_plan = json.loads(plan.plan_json)
    except Exception:
        workout_plan = {}

    u = plan.user
    return templates.TemplateResponse(request, "result.html", {
        "username": u.name if u else "Athlete",
        "age": u.age if u else "--",
        "weight": u.weight if u else "--",
        "goal": u.goal if u else "Fitness",
        "intensity": u.intensity if u else "moderate",
        "user_id": f"USR-{u.id:04d}" if u else "USR-0001",
        "workout_plan": workout_plan,
        "nutrition_tip": plan.nutrition_tip or "Maintain optimal hydration and nutrient intake.",
        "plan_id": plan.id,
        "is_updated": False,
    })


@router.get("/health")
async def health_check():
    return {"status": "ok", "app": "FitBuddy AI", "version": "3.0.0"}

