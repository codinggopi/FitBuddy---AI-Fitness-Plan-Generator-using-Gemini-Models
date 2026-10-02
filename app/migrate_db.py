import sqlite3
from app.config import settings

def migrate():
    # Only applies to sqlite db
    if "sqlite" not in settings.DATABASE_URL:
        return
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Check users table
    try:
        user_cols = [r[1] for r in c.execute("PRAGMA table_info(users)").fetchall()]
        if "gender" not in user_cols:
            c.execute("ALTER TABLE users ADD COLUMN gender VARCHAR(20) DEFAULT 'other'")
        if "dietary_preference" not in user_cols:
            c.execute("ALTER TABLE users ADD COLUMN dietary_preference VARCHAR(100) DEFAULT 'Standard / Balanced'")
        if "injuries" not in user_cols:
            c.execute("ALTER TABLE users ADD COLUMN injuries VARCHAR(255) DEFAULT 'None'")
    except Exception as e:
        print("User migration error:", e)

    # Check workout_plans table
    try:
        plan_cols = [r[1] for r in c.execute("PRAGMA table_info(workout_plans)").fetchall()]
        if "nutrition_json" not in plan_cols:
            c.execute("ALTER TABLE workout_plans ADD COLUMN nutrition_json TEXT")
    except Exception as e:
        print("Plan migration error:", e)

    conn.commit()
    conn.close()
    print("Database sync complete.")

if __name__ == "__main__":
    migrate()
