"""
HomeGuardian AI — Anomaly Detection Routes
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from models import AnomalyEventResponse, AnomalyAcknowledgeRequest, RiskScoreResponse
from auth import get_current_user
from database import get_db
from services.risk_service import risk_calculator

router = APIRouter()


@router.get("/", response_model=list)
async def list_anomalies(
    risk_level: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    user: dict = Depends(get_current_user)
):
    """List anomaly events with optional filters."""
    with get_db() as conn:
        query = "SELECT * FROM anomaly_events"
        params = []
        if risk_level:
            query += " WHERE risk_level = ?"
            params.append(risk_level)
        query += " ORDER BY detected_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


@router.get("/{anomaly_id}", response_model=AnomalyEventResponse)
async def get_anomaly(anomaly_id: int, user: dict = Depends(get_current_user)):
    """Get details of a specific anomaly event."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM anomaly_events WHERE id = ?", (anomaly_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Anomaly event not found")
    return AnomalyEventResponse(**dict(row))


@router.put("/{anomaly_id}/acknowledge")
async def acknowledge_anomaly(
    anomaly_id: int,
    request: AnomalyAcknowledgeRequest,
    user: dict = Depends(get_current_user)
):
    """Acknowledge an anomaly event."""
    with get_db() as conn:
        result = conn.execute(
            """UPDATE anomaly_events SET acknowledged = 1,
               acknowledged_at = ?, acknowledged_by = ? WHERE id = ?""",
            (datetime.utcnow().isoformat(), request.acknowledged_by, anomaly_id)
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Anomaly event not found")
    risk_calculator.deregister_score(anomaly_id)
    return {"status": "acknowledged", "anomaly_id": anomaly_id}
