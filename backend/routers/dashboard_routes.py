"""
HomeGuardian AI — Dashboard Aggregation Routes
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from auth import get_current_user
from database import get_db
from services.risk_service import risk_calculator
from config import settings

router = APIRouter()


@router.get("/summary")
async def dashboard_summary(user: dict = Depends(get_current_user)):
    """Get aggregated dashboard statistics."""
    with get_db() as conn:
        total_sensors = conn.execute("SELECT COUNT(*) as c FROM sensor_nodes").fetchone()["c"]
        active_sensors = conn.execute(
            "SELECT COUNT(*) as c FROM sensor_nodes WHERE status = 'active'"
        ).fetchone()["c"]

        today = datetime.utcnow().strftime("%Y-%m-%d")
        anomalies_today = conn.execute(
            "SELECT COUNT(*) as c FROM anomaly_events WHERE detected_at >= ?",
            (today,)
        ).fetchone()["c"]
        alerts_today = conn.execute(
            "SELECT COUNT(*) as c FROM alerts WHERE sent_at >= ?",
            (today,)
        ).fetchone()["c"]

    system_risk = risk_calculator.get_system_risk()

    return {
        "active_sensors": active_sensors,
        "total_sensors": total_sensors,
        "system_mode": "demo" if settings.DEMO_MODE else "monitoring",
        "baseline_status": "learning",
        "current_risk": system_risk["score"],
        "risk_level": system_risk["risk_level"],
        "total_anomalies_today": anomalies_today,
        "total_alerts_today": alerts_today,
        "uptime_hours": 0
    }


@router.get("/heatmap/{zone}")
async def get_heatmap(zone: str, user: dict = Depends(get_current_user)):
    """Get heat zone data for the floor plan."""
    with get_db() as conn:
        recent = conn.execute(
            """SELECT COUNT(*) as c FROM anomaly_events
               WHERE zone = ? AND detected_at >= ?""",
            (zone, (datetime.utcnow() - timedelta(hours=24)).isoformat())
        ).fetchone()

    activity_count = recent["c"] if recent else 0
    intensity = min(1.0, activity_count / 10.0)
    risk = "low" if intensity < 0.3 else "medium" if intensity < 0.7 else "high"

    return {
        "zone": zone,
        "intensity": intensity,
        "activity_count": activity_count,
        "last_activity": None,
        "risk_level": risk
    }
