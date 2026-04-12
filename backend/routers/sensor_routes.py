"""
HomeGuardian AI — Sensor Node Routes
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends

from models import SensorNodeCreate, SensorNodeResponse, SensorHealthResponse
from auth import get_current_user
from database import get_db

router = APIRouter()


@router.get("/", response_model=list)
async def list_sensors(user: dict = Depends(get_current_user)):
    """List all sensor nodes for the current user."""
    with get_db() as conn:
        if user["role"] == "new_device":
            rows = conn.execute("SELECT * FROM sensor_nodes ORDER BY enrolled_at DESC").fetchall()
        else:
            rows = conn.execute("SELECT * FROM sensor_nodes WHERE owner_id = ?", (user["id"],)).fetchall()
    return [dict(row) for row in rows]


@router.post("/", response_model=SensorNodeResponse, status_code=201)
async def register_sensor(sensor: SensorNodeCreate, user: dict = Depends(get_current_user)):
    """Register a new sensor node."""
    sensor_id = f"{sensor.type.value}-{str(uuid.uuid4())[:8]}"
    with get_db() as conn:
        conn.execute(
            """INSERT INTO sensor_nodes (id, name, type, location_zone, owner_id, status)
               VALUES (?, ?, ?, ?, ?, 'learning')""",
            (sensor_id, sensor.name, sensor.type.value, sensor.location_zone, user["id"])
        )
        row = conn.execute("SELECT * FROM sensor_nodes WHERE id = ?", (sensor_id,)).fetchone()
    return SensorNodeResponse(**dict(row))


@router.get("/{sensor_id}", response_model=SensorNodeResponse)
async def get_sensor(sensor_id: str, user: dict = Depends(get_current_user)):
    """Get details of a specific sensor node."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM sensor_nodes WHERE id = ?", (sensor_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sensor node not found")
    return SensorNodeResponse(**dict(row))


@router.put("/{sensor_id}/heartbeat")
async def update_heartbeat(sensor_id: str, user: dict = Depends(get_current_user)):
    """Update the heartbeat timestamp for a sensor node."""
    with get_db() as conn:
        result = conn.execute(
            "UPDATE sensor_nodes SET last_heartbeat = ?, status = 'active' WHERE id = ?",
            (datetime.utcnow().isoformat(), sensor_id)
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Sensor node not found")
    return {"status": "ok", "sensor_id": sensor_id}


@router.get("/{sensor_id}/health", response_model=SensorHealthResponse)
async def get_sensor_health(sensor_id: str, user: dict = Depends(get_current_user)):
    """Get health status of a specific sensor node."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM sensor_nodes WHERE id = ?", (sensor_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sensor node not found")

    sensor = dict(row)
    uptime = None
    quality = "unknown"

    if sensor.get("last_heartbeat"):
        try:
            last_hb = datetime.fromisoformat(sensor["last_heartbeat"])
            delta = datetime.utcnow() - last_hb
            uptime = int(delta.total_seconds())
            if delta.total_seconds() < 30:
                quality = "excellent"
            elif delta.total_seconds() < 120:
                quality = "good"
            elif delta.total_seconds() < 300:
                quality = "poor"
            else:
                quality = "disconnected"
        except ValueError:
            pass

    return SensorHealthResponse(
        sensor_id=sensor_id, status=sensor["status"],
        last_heartbeat=sensor.get("last_heartbeat"),
        uptime_seconds=uptime, connection_quality=quality
    )
