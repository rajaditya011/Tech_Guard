"""
HomeGuardian AI — Prediction Engine Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from auth import get_current_user
from services.prediction_service import prediction_engine

router = APIRouter()


@router.get("/")
async def list_predictions(user: dict = Depends(get_current_user)):
    """List active (unresolved) prediction events."""
    return prediction_engine.get_active_predictions()


@router.get("/{prediction_id}/timeline")
async def get_timeline(prediction_id: int, user: dict = Depends(get_current_user)):
    """Get the AI reasoning timeline for a prediction."""
    timeline = prediction_engine.get_reasoning_timeline(prediction_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="No timeline data for this prediction")
    return {
        "prediction_id": prediction_id,
        "entries": timeline
    }
