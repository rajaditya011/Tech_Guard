"""
HomeGuardian AI — Video Stream Routes
Endpoints for live video streaming and frame relay.
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from auth import get_current_user
from services.sensor_pipeline import sensor_pipeline
from database import get_db

logger = logging.getLogger("homeguardian.stream")

router = APIRouter()


@router.get("/{sensor_id}")
async def get_live_stream(sensor_id: str, user: dict = Depends(get_current_user)):
    """Get live video stream from a sensor node (MJPEG format)."""
    with get_db() as conn:
        sensor = conn.execute("SELECT * FROM sensor_nodes WHERE id = ?", (sensor_id,)).fetchone()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor node not found")

    async def frame_generator():
        queue = sensor_pipeline.register_frame_queue(sensor_id)
        try:
            while True:
                try:
                    frame_data = await asyncio.wait_for(queue.get(), timeout=10.0)
                    frame_b64 = frame_data.get("frame_data", "")
                    if frame_b64:
                        import base64
                        frame_bytes = base64.b64decode(frame_b64)
                        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
                except asyncio.TimeoutError:
                    yield b"--frame\r\n\r\n"
        finally:
            sensor_pipeline.unregister_frame_queue(sensor_id)

    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")


@router.get("/{sensor_id}/snapshot")
async def get_snapshot(sensor_id: str, user: dict = Depends(get_current_user)):
    """Get the latest frame from a sensor node."""
    buffer = sensor_pipeline.ring_buffers.get_buffer(sensor_id)
    frames = buffer.get_last_n(1)
    if not frames:
        raise HTTPException(status_code=404, detail="No frames available from this sensor")
    latest = frames[0]
    return {
        "sensor_id": sensor_id,
        "frame_data": latest["data"].get("frame_data", ""),
        "timestamp": latest["timestamp"],
        "resolution": latest["data"].get("resolution", [640, 480])
    }


@router.get("/{sensor_id}/stats")
async def get_stream_stats(sensor_id: str, user: dict = Depends(get_current_user)):
    """Get streaming statistics for a sensor node."""
    stats = sensor_pipeline.get_sensor_stats(sensor_id)
    if stats["total_frames"] == 0:
        raise HTTPException(status_code=404, detail="No data from this sensor")
    return stats
