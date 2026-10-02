from typing import Optional, Dict
from pydantic import BaseModel, Field


class NutritionCalculateRequest(BaseModel):
    weight: float = Field(..., ge=30, le=300)
    height: Optional[float] = Field(175.0, ge=100, le=250)
    age: int = Field(..., ge=12, le=100)
    gender: Optional[str] = Field("other", pattern="^(male|female|other)$")
    goal: str = Field(..., min_length=2)
    intensity: str = Field("medium", pattern="^(low|medium|high)$")


class MacroRatio(BaseModel):
    protein_pct: int
    carbs_pct: int
    fat_pct: int


class NutritionTargetResponse(BaseModel):
    bmr: int
    tdee: int
    target_calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    goal_type: str
    macro_split: MacroRatio
    hydration_liters: float
