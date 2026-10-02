from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.user_schema import UserCreate, UserResponse
from app.schemas.nutrition_schema import NutritionTargetResponse


class ExerciseItem(BaseModel):
    name: str
    sets: int = Field(..., ge=1, le=10)
    reps: str
    notes: Optional[str] = ""
    rest_sec: Optional[int] = 60


class DayPlan(BaseModel):
    focus: str
    warmup: Optional[str] = ""
    exercises: List[ExerciseItem] = []
    cooldown: Optional[str] = ""


class GeneratePlanRequest(UserCreate):
    days_per_week: Optional[int] = Field(7, ge=3, le=7)
    session_duration: Optional[int] = Field(45, ge=20, le=120)  # minutes


class RefinePlanRequest(BaseModel):
    plan_id: int
    feedback: str = Field(..., min_length=2, max_length=500)


class PlanSummaryResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_goal: str
    intensity: str
    equipment: str
    created_at: datetime
    updated_at: datetime


class PlanDetailResponse(BaseModel):
    plan_id: int
    plan: Dict[str, Any]
    tip: Optional[str] = None
    nutrition: Optional[Dict[str, Any]] = None
    user: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
