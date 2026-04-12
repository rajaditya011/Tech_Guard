"""
HomeGuardian AI — Narrative Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from auth import get_current_user
from database import get_db
from services.narrative_service import narrative_generator

router = APIRouter()


@router.get("/{anomaly_id}")
async def get_narrative(anomaly_id: int, user: dict = Depends(get_current_user)):
    """Get the AI narrative for an anomaly event."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, narrative_text, detected_at FROM anomaly_events WHERE id = ?",
            (anomaly_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Anomaly event not found")

    event = dict(row)
    if not event.get("narrative_text"):
        raise HTTPException(status_code=404, detail="No narrative generated yet")

    return {
        "anomaly_id": event["id"],
        "narrative_text": event["narrative_text"],
        "generated_at": event["detected_at"]
    }


@router.post("/{anomaly_id}/generate")
async def generate_narrative(anomaly_id: int, user: dict = Depends(get_current_user)):
    """Generate (or regenerate) an AI narrative for an anomaly event."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM anomaly_events WHERE id = ?", (anomaly_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Anomaly event not found")

    event = dict(row)
    context = {
        "timestamp": event["detected_at"],
        "zone": event["zone"],
        "anomaly_score": event["anomaly_score"],
        "risk_level": event["risk_level"],
        "baseline_deviation": event.get("baseline_deviation", 0),
        "duration_seconds": event.get("duration_seconds", 0),
        "classification": event.get("classification", "minor_deviation"),
        "sensor_count": len(event.get("sensor_node_ids", "").split(","))
    }

    result = await narrative_generator.generate_narrative(anomaly_id, context)
    return result
