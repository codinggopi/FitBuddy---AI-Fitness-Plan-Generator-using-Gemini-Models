import json
import re
import logging
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

from app.config import settings

logger = logging.getLogger("fitbuddy.gemini")

def get_candidate_models():
    """Returns free-tier models that incur zero cost on Google AI Studio."""
    models = ["gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-flash-lite-latest"]
    seen = set()
    return [m for m in models if m and not (m in seen or seen.add(m))]

# Initialize client if API key is provided
_client: Optional[genai.Client] = None

def get_gemini_client() -> Optional[genai.Client]:
    global _client
    if _client is None and settings.GEMINI_API_KEY:
        try:
            _client = genai.Client(api_key=settings.GEMINI_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
    return _client


def _extract_json(text: str) -> Dict[str, Any]:
    """Safely extracts JSON from markdown-wrapped or raw model output."""
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        return json.loads(clean)
    except Exception:
        pass

    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    raise ValueError("Could not parse JSON response from Gemini model.")


def _get_intelligent_fallback_plan(
    name: str,
    goal: str,
    intensity: str,
    equipment: str,
    injuries: Optional[str] = "None",
    duration: int = 45
) -> Dict[str, Any]:
    """
    Parametric fallback routine tailored to user parameters
    when API limits or network issues occur.
    """
    has_knee = "knee" in (injuries or "").lower()
    has_back = "back" in (injuries or "").lower()
    is_home = "home" in equipment.lower() or "dumbbell" in equipment.lower()
    is_calisthenics = "bodyweight" in equipment.lower()

    squat_exercise = (
        "Glute Bridge & Wall Sit (Low Impact)" if has_knee
        else ("Goblet Squat (Dumbbell)" if is_home else "Barbell Back Squat / Leg Press")
    )
    push_exercise = (
        "Incline Push-Ups" if is_calisthenics
        else ("Dumbbell Floor/Bench Press" if is_home else "Barbell Bench Press / Incline Press")
    )
    pull_exercise = (
        "Inverted Rows or Doorway Rows" if is_calisthenics
        else ("Single-Arm Dumbbell Rows" if is_home else "Cable Lat Pulldown / Barbell Row")
    )
    hinge_exercise = (
        "Bird-Dog & Hip Thrusts" if has_back
        else ("Dumbbell Romanian Deadlift" if is_home else "Barbell Romanian Deadlift")
    )

    return {
        "Day 1": {
            "focus": f"Full Body Strength & Foundation ({equipment})",
            "warmup": "5 min dynamic joint mobility and cat-cow waves",
            "exercises": [
                {"name": squat_exercise, "sets": 3, "reps": "10-12", "notes": "Control tempo 3s down, explode up", "rest_sec": 60},
                {"name": push_exercise, "sets": 3, "reps": "10-12", "notes": "Engage pecs, keep core rigid", "rest_sec": 60},
                {"name": pull_exercise, "sets": 3, "reps": "12 each", "notes": "Retract scapulae fully at top", "rest_sec": 60},
                {"name": "Forearm Plank Hold", "sets": 3, "reps": "35-45 sec", "notes": "Brace core without hip sagging", "rest_sec": 45}
            ],
            "cooldown": f"5 min chest doorway and hamstring stretch ({duration}m session total)"
        },
        "Day 2": {
            "focus": f"Cardio Conditioning & Core Stability ({intensity.capitalize()})",
            "warmup": "3 min light arm circles and brisk pace walk",
            "exercises": [
                {"name": "Steady State Zone 2 Cardio (Bike / Incline Walk)", "sets": 1, "reps": "25-30 min", "notes": f"Maintain conversational aerobic pace matching {intensity} intensity", "rest_sec": 0},
                {"name": "Bicycle Crunches", "sets": 3, "reps": "20 total", "notes": "Slow controlled rotational tempo", "rest_sec": 45},
                {"name": "Deadbugs", "sets": 3, "reps": "12 each side", "notes": "Keep lower spine flat against floor", "rest_sec": 45},
                {"name": "Side Plank Hold", "sets": 3, "reps": "30 sec / side", "notes": "Stack hips and shoulders", "rest_sec": 30}
            ],
            "cooldown": "5 min child's pose and cobra breathing flow"
        },
        "Day 3": {
            "focus": "Lower Body Power & Posterior Chain",
            "warmup": "5 min hip circles, leg swings, and ankle rolls",
            "exercises": [
                {"name": hinge_exercise, "sets": 3, "reps": "10-12", "notes": "Hinge deeply at hips, neutral spine", "rest_sec": 75},
                {"name": "Walking Lunges or Step-Ups", "sets": 3, "reps": "10 / leg", "notes": "Soft knee tap, push through front heel", "rest_sec": 60},
                {"name": "Standing Calf Raises", "sets": 3, "reps": "15-20", "notes": "Full stretch at bottom, 2s peak contraction", "rest_sec": 45},
                {"name": "Hanging Knee Raises or Reverse Crunches", "sets": 3, "reps": "12-15", "notes": "Curl pelvis upward smoothly", "rest_sec": 45}
            ],
            "cooldown": "Deep quad, calf, and hip flexor stretches"
        },
        "Day 4": {
            "focus": "Active Recovery, Mobility & Joint Health",
            "warmup": "None required - gentle flow",
            "exercises": [
                {"name": "Thoracic Spine Book Openers", "sets": 2, "reps": "10 / side", "notes": "Enhances ribcage and upper back rotation", "rest_sec": 30},
                {"name": "World's Greatest Stretch Routine", "sets": 3, "reps": "5 / side", "notes": "Flow through lunge, reach, and hamstring extension", "rest_sec": 30},
                {"name": "Outdoor Walk / Gentle Cycling", "sets": 1, "reps": "25-35 min", "notes": "Low heart rate recovery for oxygenation", "rest_sec": 0}
            ],
            "cooldown": "Diaphragmatic box breathing for 5 minutes"
        },
        "Day 5": {
            "focus": "Upper Body Push & Pull Hypertrophy",
            "warmup": "Band pull-aparts and arm circles 4 min",
            "exercises": [
                {"name": "Dumbbell Overhead Shoulder Press", "sets": 3, "reps": "10-12", "notes": "Press vertically without hyperextending back", "rest_sec": 60},
                {"name": "Lat Pulldown or Assisted Pull-Ups", "sets": 3, "reps": "10-12", "notes": "Drive elbows down to hips", "rest_sec": 60},
                {"name": "Dumbbell Lateral Raises", "sets": 3, "reps": "15", "notes": "Control the descent, slight forward lean", "rest_sec": 45},
                {"name": "Overhead Tricep Extension or Dips", "sets": 3, "reps": "12", "notes": "Keep elbows close to head", "rest_sec": 45},
                {"name": "Incline Dumbbell Bicep Curls", "sets": 3, "reps": "12", "notes": "Full supination at the peak", "rest_sec": 45}
            ],
            "cooldown": "Shoulder, bicep, and neck relaxation stretches"
        },
        "Day 6": {
            "focus": f"Metabolic Conditioning & Core Finisher ({goal})",
            "warmup": "3 min jump rope or jumping jacks",
            "exercises": [
                {"name": "Kettlebell or Dumbbell Swings", "sets": 4, "reps": "15-20", "notes": "Snap hips aggressively", "rest_sec": 45},
                {"name": "Dumbbell Thrusters or Bodyweight Squat Jumps", "sets": 3, "reps": "10-12", "notes": "Coordinated fluid drive from squat to press", "rest_sec": 60},
                {"name": "Mountain Climbers", "sets": 4, "reps": "30 sec", "notes": "Piston knees smoothly with steady tempo", "rest_sec": 30},
                {"name": "Russian Twists with Weight", "sets": 3, "reps": "20 total", "notes": "Keep feet elevated if possible", "rest_sec": 45}
            ],
            "cooldown": "Full body cool-down, rehydration, and mobility"
        },
        "Day 7": {
            "focus": "Full Restoration, Muscle Repair & Prep",
            "warmup": "None",
            "exercises": [
                {"name": "Complete Neuromuscular Rest", "sets": 1, "reps": "All day", "notes": "Prioritize 8+ hours sleep, optimal protein intake, and mental reset", "rest_sec": 0}
            ],
            "cooldown": "15 min relaxing evening walk"
        }
    }


async def generate_plan(
    name: str,
    age: int,
    weight: float,
    height: float,
    gender: str,
    goal: str,
    intensity: str,
    equipment: str,
    dietary_preference: str = "Standard / Balanced",
    injuries: str = "None",
    session_duration: int = 45,
    days_per_week: int = 7
) -> Dict[str, Any]:
    """Generates an intelligent 7-day personalized workout plan using Gemini 2.0 Flash."""
    client = get_gemini_client()

    prompt = f"""
You are an elite sports scientist, Olympic strength coach, and physiotherapist.
Create an individualized, periodized 7-day workout routine for:
- Athlete Name: {name}
- Biological Sex: {gender}
- Age: {age} years
- Weight: {weight} kg | Height: {height} cm
- Primary Goal: {goal}
- Intensity: {intensity} (low = beginner friendly & safe progression, medium = progressive overload, high = intense high-performance)
- Equipment: {equipment}
- Dietary Style: {dietary_preference}
- Physical Limitations / Injuries: {injuries}
- Preferred Session Duration: ~{session_duration} minutes per workout
- Active Days: {days_per_week} days

CRITICAL REQUIREMENTS:
1. Provide a routine covering Day 1 to Day 7.
2. Structure appropriate active recovery / rest days based on intensity and {days_per_week} target training days.
3. Every day MUST have:
   - "focus": Concise, professional title (e.g. "Upper Push & Shoulder Hypertrophy", "Cardio Conditioning & Core", "Rest & Mobility Flow").
   - "warmup": 3-5 minute dynamic routine specific to the target muscle groups.
   - "exercises": List of exercise objects with:
       - "name": Standard exercise name (suitable for gym searching)
       - "sets": Integer (e.g. 3)
       - "reps": String with reps or duration (e.g. "10-12 reps" or "45 sec")
       - "notes": Technical lifting cue and injury prevention tip (strictly respecting {injuries})
       - "rest_sec": Recommended inter-set rest in seconds (integer, e.g. 60 or 90)
   - "cooldown": 3-5 minute static stretch and recovery protocol.
4. Output strictly valid JSON matching this schema:
{{
  "Day 1": {{
    "focus": "...",
    "warmup": "...",
    "exercises": [
      {{"name": "...", "sets": 3, "reps": "...", "notes": "...", "rest_sec": 60}}
    ],
    "cooldown": "..."
  }},
  ...
  "Day 7": {{ ... }}
}}
"""

    if client:
        for model_name in get_candidate_models():
            try:
                # Use non-blocking async client
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.4,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                )
                response = await client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    parsed = _extract_json(response.text)
                    if isinstance(parsed, dict) and "Day 1" in parsed:
                        return parsed
            except Exception as e:
                logger.warning(f"Gemini {model_name} error: {e}")
                continue

    # Graceful fallback
    return _get_intelligent_fallback_plan(
        name=name,
        goal=goal,
        intensity=intensity,
        equipment=equipment,
        injuries=injuries,
        duration=session_duration
    )


async def refine_plan(current_plan: Dict[str, Any], feedback: str) -> Dict[str, Any]:
    """Applies athlete adjustments and tweaks to an existing plan using Gemini."""
    client = get_gemini_client()

    prompt = f"""
You are an expert fitness coach. Refine the following 7-day workout schedule according to the athlete's feedback.

CURRENT SCHEDULE:
{json.dumps(current_plan, indent=2)}

ATHLETE'S ADJUSTMENT REQUEST:
"{feedback}"

REQUIREMENTS:
1. Preserve the exact JSON schema with "Day 1" through "Day 7", each containing "focus", "warmup", "exercises" (name, sets, reps, notes, rest_sec), and "cooldown".
2. Thoughtfully incorporate every aspect of the athlete's feedback (e.g., swapping exercises, shortening rest, focusing on specific muscles, replacing equipment).
3. Return ONLY valid JSON.
"""

    if client:
        for model_name in get_candidate_models():
            try:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.4,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                )
                response = await client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config
                )
                if response and response.text:
                    parsed = _extract_json(response.text)
                    if isinstance(parsed, dict) and "Day 1" in parsed:
                        return parsed
            except Exception as e:
                logger.warning(f"Refinement with {model_name} failed: {e}")
                continue

    # If refinement fails, append note to Day 1
    current_plan["Day 1"]["notes"] = f"Note: Feedback queued ({feedback})"
    return current_plan


async def get_nutrition_tip(goal: str, dietary_style: str = "Standard / Balanced") -> str:
    """Generates concise, goal-tailored nutrition and recovery advice."""
    client = get_gemini_client()

    prompt = (
        f"Provide one concise, highly actionable, scientifically grounded nutrition and recovery tip "
        f"for an athlete pursuing '{goal}' following a '{dietary_style}' diet. "
        f"Keep it under 35 words. Return plain text only."
    )

    if client:
        for model_name in get_candidate_models():
            try:
                response = await client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text.strip().replace('"', '')
            except Exception as e:
                logger.warning(f"Nutrition tip generation failed with {model_name}: {e}")
                continue

    return "Distribute high-quality protein evenly across 3-4 meals, hydrate with 3L water daily, and prioritize 7-9 hours of restorative sleep for neuromuscular recovery."
