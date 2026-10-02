from typing import Optional, Dict, Any


def calculate_nutrition_targets(
    weight: float,
    height: Optional[float],
    age: int,
    goal: str,
    intensity: str,
    gender: Optional[str] = "other"
) -> Dict[str, Any]:
    """
    Computes scientifically grounded energy and macronutrient targets
    using the Mifflin-St Jeor equation with biological sex adjustments.
    """
    h = height if (height and height > 50) else 175.0
    w = max(weight, 30.0)
    a = max(age, 12)
    gen = (gender or "other").lower()

    # 1. Base Mifflin-St Jeor BMR calculation
    if gen == "male":
        bmr = 10 * w + 6.25 * h - 5 * a + 5
    elif gen == "female":
        bmr = 10 * w + 6.25 * h - 5 * a - 161
    else:
        # Neutral midpoint
        bmr = 10 * w + 6.25 * h - 5 * a - 78

    bmr = round(bmr)

    # 2. Activity Multiplier
    activity_multipliers = {
        "low": 1.25,      # Sedentary / light movement
        "medium": 1.45,   # Moderate workout (3-4 days/wk)
        "high": 1.65      # Intense conditioning / heavy lifting (5-6 days/wk)
    }
    mult = activity_multipliers.get((intensity or "medium").lower(), 1.45)
    tdee = round(bmr * mult)

    # 3. Goal Adjustment & Macronutrient distribution
    goal_lower = (goal or "").lower()

    if any(k in goal_lower for k in ["loss", "lose", "cut", "lean", "burn", "shred"]):
        # Safe 20% deficit (capped to avoid starvation)
        deficit = min(500, max(300, round(tdee * 0.20)))
        target_cals = max(tdee - deficit, 1200 if gen == "female" else 1500)
        protein_g = round(w * 2.2)  # Higher protein to preserve lean muscle in deficit
        fat_pct = 0.25
        goal_type = "Fat Loss Caloric Deficit"

    elif any(k in goal_lower for k in ["build", "gain", "bulk", "muscle", "mass", "hypertrophy"]):
        # Clean lean surplus of 10-15%
        surplus = min(400, max(250, round(tdee * 0.12)))
        target_cals = tdee + surplus
        protein_g = round(w * 2.0)
        fat_pct = 0.25
        goal_type = "Muscle Growth Surplus"

    elif any(k in goal_lower for k in ["strength", "power", "heavy"]):
        target_cals = tdee + 150
        protein_g = round(w * 2.0)
        fat_pct = 0.28
        goal_type = "Strength & Power Output"

    elif any(k in goal_lower for k in ["endurance", "cardio", "stamina"]):
        target_cals = tdee + 100
        protein_g = round(w * 1.7)
        fat_pct = 0.22
        goal_type = "Endurance & Glycogen Replenishment"

    else:
        target_cals = tdee
        protein_g = round(w * 1.8)
        fat_pct = 0.25
        goal_type = "Maintenance & Functional Health"

    # Calculate fat and carbohydrate grams
    fat_cals = target_cals * fat_pct
    fat_g = round(fat_cals / 9)

    protein_cals = protein_g * 4
    remaining_cals = max(target_cals - (protein_cals + (fat_g * 9)), 200)
    carbs_g = round(remaining_cals / 4)

    # Calculate Macro Percentages for UI Visualization
    total_macro_cals = (protein_g * 4) + (carbs_g * 4) + (fat_g * 9)
    if total_macro_cals > 0:
        p_pct = round(((protein_g * 4) / total_macro_cals) * 100)
        c_pct = round(((carbs_g * 4) / total_macro_cals) * 100)
        f_pct = max(0, 100 - (p_pct + c_pct))
    else:
        p_pct, c_pct, f_pct = 30, 45, 25

    # Recommended daily water intake (liters)
    hydration_liters = round((w * 0.035) + (0.5 if intensity == "high" else 0.2), 1)

    return {
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_cals,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "goal_type": goal_type,
        "macro_split": {
            "protein_pct": p_pct,
            "carbs_pct": c_pct,
            "fat_pct": f_pct
        },
        "hydration_liters": hydration_liters
    }


def calculate_bmi_details(
    weight: float,
    height: float,
    age: Optional[int] = 25,
    gender: Optional[str] = "other"
) -> Dict[str, Any]:
    """
    Computes BMI, WHO health classifications, healthy weight ranges,
    and estimated body fat percentage using the Deurenberg equation.
    """
    h_m = (height / 100.0) if (height and height > 50) else 1.75
    w = max(weight, 25.0)
    bmi = round(w / (h_m * h_m), 1)

    min_healthy = round(18.5 * (h_m * h_m), 1)
    max_healthy = round(24.9 * (h_m * h_m), 1)

    if bmi < 18.5:
        category = "Underweight"
        category_color = "sky"
        diff = round(min_healthy - w, 1)
        status_msg = f"Below standard healthy range. Consider gaining ~{diff} kg of lean mass to enter the optimal zone."
    elif 18.5 <= bmi < 25.0:
        category = "Normal Weight"
        category_color = "emerald"
        diff = 0.0
        status_msg = "Optimal healthy range. Maintain your current weight with progressive strength training and conditioning."
    elif 25.0 <= bmi < 30.0:
        category = "Overweight"
        category_color = "amber"
        diff = round(w - max_healthy, 1)
        status_msg = f"Above standard range. A mild caloric deficit targeting ~{diff} kg loss can bring you to optimal health."
    else:
        category = "Obesity Range"
        category_color = "rose"
        diff = round(w - max_healthy, 1)
        status_msg = f"High range. Prioritize a structured caloric deficit and low-impact movement to reduce ~{diff} kg."

    # Deurenberg Adult Body Fat % formula
    gen = (gender or "other").lower()
    sex_factor = 1 if gen == "male" else (0 if gen == "female" else 0.5)
    body_fat_pct = round((1.20 * bmi) + (0.23 * (age or 25)) - (10.8 * sex_factor) - 5.4, 1)
    body_fat_pct = max(5.0, min(body_fat_pct, 55.0))

    return {
        "bmi": bmi,
        "category": category,
        "category_color": category_color,
        "healthy_weight_min_kg": min_healthy,
        "healthy_weight_max_kg": max_healthy,
        "difference_kg": diff,
        "estimated_body_fat_pct": body_fat_pct,
        "status_message": status_msg
    }
