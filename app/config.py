import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


class Settings(BaseSettings):
    APP_NAME: str = "FitBuddy AI"
    APP_VERSION: str = "3.0.0"
    APP_DESCRIPTION: str = "Enterprise AI-Powered 7-Day Workout & Nutrition Planner using Google Gemini Models"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    # Server Network
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/fitbuddy.db")

    # Gemini AI (100% Free Tier - No Billing Required)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    PRIMARY_MODEL: str = os.getenv("PRIMARY_MODEL", "gemini-3.5-flash-lite")
    FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL", "gemini-flash-latest")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
