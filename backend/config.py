"""
HomeGuardian AI — Configuration
Loads and validates all environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    """Application settings loaded from environment variables."""

    # Demo Mode
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"

    # Claude API
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "")

    # Firebase
    FCM_SERVER_KEY: str = os.getenv("FCM_SERVER_KEY", "")

    # MQTT
    MQTT_BROKER_URL: str = os.getenv("MQTT_BROKER_URL", "localhost")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))

    # Database
    DB_PATH: str = os.getenv("DB_PATH", "data/homeguardian.db")

    # YOLO
    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", "models/yolov8n.pt")

    # Baseline
    BASELINE_DAYS: int = int(os.getenv("BASELINE_DAYS", "14"))
    ANOMALY_THRESHOLD: float = float(os.getenv("ANOMALY_THRESHOLD", "0.65"))

    # Clip Extraction
    CLIP_PRE_SECONDS: int = int(os.getenv("CLIP_PRE_SECONDS", "5"))
    CLIP_POST_SECONDS: int = int(os.getenv("CLIP_POST_SECONDS", "10"))

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "homeguardian-dev-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRY_MINUTES: int = int(os.getenv("JWT_ACCESS_EXPIRY_MINUTES", "15"))
    JWT_REFRESH_EXPIRY_DAYS: int = int(os.getenv("JWT_REFRESH_EXPIRY_DAYS", "7"))

    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

    # Server
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "5173"))

    @classmethod
    def validate(cls):
        """Validate critical settings on startup."""
        errors = []
        if not cls.DEMO_MODE:
            if not cls.CLAUDE_API_KEY:
                errors.append("CLAUDE_API_KEY is required when DEMO_MODE=false")
            if not cls.FCM_SERVER_KEY:
                errors.append("FCM_SERVER_KEY is required when DEMO_MODE=false")
        if not cls.JWT_SECRET or cls.JWT_SECRET == "homeguardian-dev-secret-change-in-production":
            import warnings
            warnings.warn("Using default JWT_SECRET — change this in production!")
        return errors


settings = Settings()
