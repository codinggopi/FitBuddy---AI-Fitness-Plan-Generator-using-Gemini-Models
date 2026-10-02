from fastapi import APIRouter
from app.schemas import NutritionCalculateRequest, NutritionTargetResponse
from app.services import calculate_nutrition_targets, get_nutrition_tip

router = APIRouter(prefix="", tags=["Nutrition & Macros"])


@router.post("/api/nutrition/calculate", response_model=NutritionTargetResponse)
async def calculate_macros(payload: NutritionCalculateRequest):
    """Calculates BMR, TDEE, goal-specific calories, and macro breakdown."""
    data = calculate_nutrition_targets(
        weight=payload.weight,
        height=payload.height,
        age=payload.age,
        goal=payload.goal,
        intensity=payload.intensity,
        gender=payload.gender
    )
    return NutritionTargetResponse(**data)


@router.get("/api/nutrition/tip/{goal}")
@router.get("/tip/{goal}", include_in_schema=False)
async def get_goal_tip(goal: str, dietary: str = "Standard / Balanced"):
    """Fetches a concise science-backed recovery tip for a goal."""
    tip_text = await get_nutrition_tip(goal, dietary)
    return {"goal": goal, "tip": tip_text}


from pydantic import BaseModel, Field
from typing import Optional
from app.services import calculate_bmi_details

class BmiCalculateRequest(BaseModel):
    weight: float = Field(..., ge=20, le=400)
    height: float = Field(..., ge=80, le=260)
    age: Optional[int] = Field(25, ge=10, le=120)
    gender: Optional[str] = Field("other")


@router.post("/api/nutrition/bmi")
async def calculate_bmi_endpoint(payload: BmiCalculateRequest):
    """Calculates BMI, WHO category, healthy weight range, and estimated body fat %."""
    return calculate_bmi_details(
        weight=payload.weight,
        height=payload.height,
        age=payload.age,
        gender=payload.gender
    )
