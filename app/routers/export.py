import json
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import WorkoutPlan
from app.services import generate_ics_calendar

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.get("/{plan_id}/calendar")
async def export_calendar(plan_id: int, db: Session = Depends(get_db)):
    """Downloads an RFC 5545 compliant .ics calendar schedule for the workout routine."""
    plan_record = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan_record:
        raise HTTPException(status_code=404, detail="Plan not found")

    try:
        plan_dict = json.loads(plan_record.plan_json)
    except Exception:
        raise HTTPException(status_code=500, detail="Corrupted plan data")

    user_name = plan_record.user.name if plan_record.user else "Athlete"
    ics_content = generate_ics_calendar(plan_dict, user_name)

    filename = f"FitBuddy_Routine_{plan_id}.ics"
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/{plan_id}/json")
async def export_json(plan_id: int, db: Session = Depends(get_db)):
    """Downloads the full routine and nutrition profile as raw JSON."""
    plan_record = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan_record:
        raise HTTPException(status_code=404, detail="Plan not found")

    data = {
        "plan_id": plan_record.id,
        "athlete": {
            "name": plan_record.user.name,
            "goal": plan_record.user.goal,
            "intensity": plan_record.user.intensity,
            "equipment": plan_record.user.equipment
        } if plan_record.user else None,
        "routine": json.loads(plan_record.plan_json),
        "nutrition_tip": plan_record.nutrition_tip,
        "nutrition_targets": json.loads(plan_record.nutrition_json) if plan_record.nutrition_json else None,
        "created_at": plan_record.created_at.isoformat() if plan_record.created_at else None
    }

    content = json.dumps(data, indent=2)
    filename = f"FitBuddy_Plan_{plan_id}.json"
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
