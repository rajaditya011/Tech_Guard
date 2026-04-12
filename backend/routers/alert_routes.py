"""
HomeGuardian AI — Alert Routes
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from auth import get_current_user
from database import get_db

router = APIRouter()


@router.get("/")
async def list_alerts(
    channel: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    user: dict = Depends(get_current_user)
):
    """List alerts with optional filters."""
    with get_db() as conn:
        query = "SELECT * FROM alerts"
        params = []
        if channel:
            query += " WHERE channel = ?"
            params.append(channel)
        query += " ORDER BY sent_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]
