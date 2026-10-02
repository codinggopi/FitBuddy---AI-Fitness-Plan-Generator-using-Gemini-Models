import os
import json
import re
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from google import genai

from database import engine, get_db, Base
import models

# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")

# ✅ NEW SDK CLIENT (CORRECT WAY)
client = genai.Client(api_key=GEMINI_API_KEY)

# ✅ USE SAFE MODEL (WORKS 100%)
MODEL = "gemini-2.0-flash-lite"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="FitBuddy", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class GenerateRequest(BaseModel):
    name: str
    age: int
    weight: float
    goal: str
    intensity: str


class RefineRequest(BaseModel):
    plan_id: int
    feedback: str


# ---------------------------------------------------------------------------
# Gemini Helpers
# ---------------------------------------------------------------------------
def _extract_json(text: str) -> dict:
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        return json.loads(clean)
    except:
        pass

    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        return json.loads(match.group())

    raise ValueError("Could not parse JSON")


def generate_plan_from_gemini(name, age, weight, goal, intensity):
    prompt = f"""
Create a 7-day workout plan.

Name: {name}
Age: {age}
Weight: {weight}
Goal: {goal}
Intensity: {intensity}

Return ONLY JSON like:
{{
 "Day 1": {{"focus": "", "exercises": [{{"name": "", "sets": 3, "reps": "10"}}]}}
}}
"""
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return _extract_json(response.text)
    except Exception as e:
        raise HTTPException(502, f"Gemini error: {e}")


def refine_plan_from_gemini(current_plan, feedback):
    prompt = f"""
Modify this plan based on feedback:

{json.dumps(current_plan)}

Feedback: {feedback}

Return ONLY JSON.
"""
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return _extract_json(response.text)
    except Exception as e:
        raise HTTPException(502, f"Gemini error: {e}")


def get_tip_from_gemini(goal):
    prompt = f"Give one short fitness tip for: {goal}"
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        raise HTTPException(502, f"Gemini error: {e}")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate")
async def generate(payload: GenerateRequest, db: Session = Depends(get_db)):

    user = models.User(
        name=payload.name,
        age=payload.age,
        weight=payload.weight,
        goal=payload.goal,
        intensity=payload.intensity,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    plan = generate_plan_from_gemini(
        payload.name, payload.age, payload.weight,
        payload.goal, payload.intensity
    )

    tip = get_tip_from_gemini(payload.goal)

    db_plan = models.WorkoutPlan(
        user_id=user.id,
        plan_json=json.dumps(plan),
        nutrition_tip=tip
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    return {
        "plan": plan,
        "tip": tip
    }


@app.post("/refine")
async def refine(payload: RefineRequest, db: Session = Depends(get_db)):

    plan = db.query(models.WorkoutPlan).filter_by(id=payload.plan_id).first()
    if not plan:
        raise HTTPException(404, "Plan not found")

    updated = refine_plan_from_gemini(
        json.loads(plan.plan_json),
        payload.feedback
    )

    plan.plan_json = json.dumps(updated)
    plan.updated_at = datetime.utcnow()

    db.commit()

    return {"plan": updated}


@app.get("/tip/{goal}")
async def tip(goal: str):
    return {"tip": get_tip_from_gemini(goal)}