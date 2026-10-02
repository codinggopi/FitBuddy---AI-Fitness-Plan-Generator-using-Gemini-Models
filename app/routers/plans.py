import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, WorkoutPlan
from app.schemas import (
    GeneratePlanRequest,
    RefinePlanRequest,
    PlanDetailResponse,
    PlanSummaryResponse
)
from app.services import (
    generate_plan,
    refine_plan,
    get_nutrition_tip,
    calculate_nutrition_targets
)

router = APIRouter(prefix="", tags=["Workout Plans"])


@router.post("/api/plans/generate", response_model=PlanDetailResponse)
@router.post("/generate", response_model=PlanDetailResponse, include_in_schema=False)
async def create_workout_plan(payload: GeneratePlanRequest, db: Session = Depends(get_db)):
    """Creates a user profile, generates an AI routine, calculates macros, and saves to database."""
    try:
        # 1. Create or persist user
        user = User(
            name=payload.name,
            age=payload.age,
            weight=payload.weight,
            height=payload.height or 175.0,
            gender=payload.gender or "other",
            goal=payload.goal,
            intensity=payload.intensity,
            equipment=payload.equipment or "Full Commercial Gym",
            dietary_preference=payload.dietary_preference or "Standard / Balanced",
            injuries=payload.injuries or "None"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # 2. Generate Workout Plan asynchronously
        plan = await generate_plan(
            name=payload.name,
            age=payload.age,
            weight=payload.weight,
            height=payload.height or 175.0,
            gender=payload.gender or "other",
            goal=payload.goal,
            intensity=payload.intensity,
            equipment=payload.equipment or "Full Commercial Gym",
            dietary_preference=payload.dietary_preference or "Standard / Balanced",
            injuries=payload.injuries or "None",
            session_duration=payload.session_duration or 45,
            days_per_week=payload.days_per_week or 7
        )

        # 3. Generate Nutrition Guidance
        tip = await get_nutrition_tip(payload.goal, payload.dietary_preference or "Standard / Balanced")

        # 4. Calculate Precision Nutrition & Macros
        nutrition_data = calculate_nutrition_targets(
            weight=payload.weight,
            height=payload.height,
            age=payload.age,
            goal=payload.goal,
            intensity=payload.intensity,
            gender=payload.gender
        )

        # 5. Persist to Database
        db_plan = WorkoutPlan(
            user_id=user.id,
            plan_json=json.dumps(plan),
            nutrition_tip=tip,
            nutrition_json=json.dumps(nutrition_data)
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)

        return PlanDetailResponse(
            plan_id=db_plan.id,
            plan=plan,
            tip=tip,
            nutrition=nutrition_data,
            user={
                "name": user.name,
                "age": user.age,
                "weight": user.weight,
                "height": user.height,
                "gender": user.gender,
                "goal": user.goal,
                "intensity": user.intensity,
                "equipment": user.equipment,
                "dietary_preference": user.dietary_preference,
                "injuries": user.injuries
            },
            created_at=db_plan.created_at,
            updated_at=db_plan.updated_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workout generation error: {str(e)}"
        )


@router.post("/api/plans/refine")
@router.post("/refine", include_in_schema=False)
async def refine_existing_plan(payload: RefinePlanRequest, db: Session = Depends(get_db)):
    """Refines an existing plan using user feedback."""
    plan_record = db.query(WorkoutPlan).filter(WorkoutPlan.id == payload.plan_id).first()
    if not plan_record:
        raise HTTPException(status_code=404, detail="Workout plan not found.")

    try:
        current_dict = json.loads(plan_record.plan_json)
    except Exception:
        raise HTTPException(status_code=500, detail="Corrupted plan data in database.")

    updated_plan = await refine_plan(current_dict, payload.feedback)

    plan_record.plan_json = json.dumps(updated_plan)
    plan_record.updated_at = datetime.utcnow()
    db.commit()

    nutrition_dict = None
    if plan_record.nutrition_json:
        try:
            nutrition_dict = json.loads(plan_record.nutrition_json)
        except Exception:
            pass

    return {
        "plan_id": plan_record.id,
        "plan": updated_plan,
        "tip": plan_record.nutrition_tip,
        "nutrition": nutrition_dict
    }


@router.get("/api/plans/{plan_id}", response_model=PlanDetailResponse)
@router.get("/plan/{plan_id}", response_model=PlanDetailResponse, include_in_schema=False)
async def get_single_plan(plan_id: int, db: Session = Depends(get_db)):
    """Retrieves a saved workout plan by its ID."""
    plan_record = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan_record:
        raise HTTPException(status_code=404, detail="Plan not found.")

    nutrition_data = None
    if plan_record.nutrition_json:
        try:
            nutrition_data = json.loads(plan_record.nutrition_json)
        except Exception:
            pass

    return PlanDetailResponse(
        plan_id=plan_record.id,
        plan=json.loads(plan_record.plan_json),
        tip=plan_record.nutrition_tip,
        nutrition=nutrition_data,
        user={
            "name": plan_record.user.name,
            "age": plan_record.user.age,
            "weight": plan_record.user.weight,
            "height": plan_record.user.height,
            "gender": plan_record.user.gender,
            "goal": plan_record.user.goal,
            "intensity": plan_record.user.intensity,
            "equipment": plan_record.user.equipment,
            "dietary_preference": plan_record.user.dietary_preference,
            "injuries": plan_record.user.injuries
        },
        created_at=plan_record.created_at,
        updated_at=plan_record.updated_at
    )


@router.get("/api/plans", response_model=List[PlanSummaryResponse])
async def list_saved_plans(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Lists saved workout routines with user metadata for history inspection."""
    records = (
        db.query(WorkoutPlan)
        .join(User)
        .order_by(WorkoutPlan.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    results = []
    for r in records:
        results.append(
            PlanSummaryResponse(
                id=r.id,
                user_id=r.user_id,
                user_name=r.user.name if r.user else "Athlete",
                user_goal=r.user.goal if r.user else "General",
                intensity=r.user.intensity if r.user else "medium",
                equipment=r.user.equipment if r.user else "Full Gym",
                created_at=r.created_at,
                updated_at=r.updated_at or r.created_at
            )
        )
    return results


@router.delete("/api/plans/{plan_id}")
async def delete_saved_plan(plan_id: int, db: Session = Depends(get_db)):
    """Deletes a workout plan by ID."""
    plan_record = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if not plan_record:
        raise HTTPException(status_code=404, detail="Plan not found.")

    db.delete(plan_record)
    db.commit()
    return {"message": "Plan deleted successfully", "plan_id": plan_id}
