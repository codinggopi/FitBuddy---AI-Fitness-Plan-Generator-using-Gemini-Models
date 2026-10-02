import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

def run_tests():
    with TestClient(app) as client:
        payload = {
            "name": "Taylor Swift",
            "age": 30,
            "weight": 62.0,
            "height": 175.0,
            "gender": "female",
            "goal": "Fat Loss & Lean Shred",
            "intensity": "medium",
            "equipment": "Home Dumbbells & Bands",
            "dietary_preference": "Vegetarian",
            "injuries": "Knee discomfort",
            "session_duration": 45,
            "days_per_week": 5
        }

        print("Testing BMI & Body Composition Endpoint...")
        r_bmi = client.post("/api/nutrition/bmi", json={"weight": 70.0, "height": 175.0, "age": 25, "gender": "male"})
        assert r_bmi.status_code == 200
        bmi_data = r_bmi.json()
        assert bmi_data["bmi"] == 22.9
        assert bmi_data["category"] == "Normal Weight"
        print(f"BMI Test OK! BMI: {bmi_data['bmi']} ({bmi_data['category']})")

        print("Generating workout plan...")
        r = client.post("/api/plans/generate", json=payload)
        assert r.status_code == 200, f"Generate failed: {r.text}"
        data = r.json()
        plan_id = data["plan_id"]
        print(f"Generated Plan #{plan_id}")
        print("Day 1 Focus:", data["plan"]["Day 1"]["focus"])
        print("Nutrition Calories:", data["nutrition"]["target_calories"], "kcal")
        print("Nutrition Tip:", data["tip"])

        print("Testing Calendar Export...")
        r_cal = client.get(f"/api/export/{plan_id}/calendar")
        assert r_cal.status_code == 200
        assert "BEGIN:VCALENDAR" in r_cal.text
        print("Calendar Export OK!")

        print("Testing Plan Refine...")
        r_refine = client.post("/api/plans/refine", json={
            "plan_id": plan_id,
            "feedback": "Add more core exercises"
        })
        assert r_refine.status_code == 200
        print("Refinement OK!")

        print("All integration tests verified successfully!")

if __name__ == "__main__":
    run_tests()
