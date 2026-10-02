from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, example="Alex Miller")
    age: int = Field(..., ge=12, le=100, example=28)
    weight: float = Field(..., ge=30, le=300, example=75.0)
    height: Optional[float] = Field(175.0, ge=100, le=250, example=178.0)
    gender: Optional[str] = Field("other", pattern="^(male|female|other)$")
    goal: str = Field(..., min_length=2, max_length=100)
    intensity: str = Field("medium", pattern="^(low|medium|high)$")
    equipment: Optional[str] = Field("Full Commercial Gym")
    dietary_preference: Optional[str] = Field("Standard / Balanced")
    injuries: Optional[str] = Field("None")


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
