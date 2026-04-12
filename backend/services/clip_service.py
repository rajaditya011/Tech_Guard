"""
HomeGuardian AI — Smart Clip Extraction Engine
Assembles pre-event + post-event frames into clips on anomaly confirmation.
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional

from config import settings
from database import get_db
from services.sensor_pipeline import sensor_pipeline
from utils.video_encoder import VideoEncoder

logger = logging.getLogger("homeguardian.clip")


class ClipExtractor:
    """Smart Clip Extraction Engine."""

    def __init__(self):
        self.pre_seconds = settings.CLIP_PRE_SECONDS
        self.post_seconds = settings.CLIP_POST_SECONDS
        self._active_captures: dict = {}

    async def trigger_clip(self, anomaly_id: int, sensor_id: str,
                           zone: str, anomaly_score: float) -> dict:
        """
        Trigger clip extraction for a confirmed anomaly.
        1. Pull pre-event frames from ring buffer
        2. Capture post-event frames
        3. Encode to MP4
        4. Save metadata to database
        """
        logger.info(f"Clip triggered for anomaly {anomaly_id} on {sensor_id}")

        # Step 1: Get pre-event frames
        pre_frames = sensor_pipeline.get_pre_event_frames(sensor_id, self.pre_seconds)
        logger.info(f"Retrieved {len(pre_frames)} pre-event frames")

        # Step 2: Capture post-event frames
        post_frames = await self._capture_post_event(sensor_id, self.post_seconds)
        logger.info(f"Captured {len(post_frames)} post-event frames")

        # Step 3: Combine frames
        all_frames = pre_frames + post_frames

        # Step 4: Encode clip
        metadata = VideoEncoder.encode_clip(
            frames=all_frames,
            anomaly_id=anomaly_id,
            sensor_id=sensor_id,
            zone=zone,
            anomaly_score=anomaly_score
        )

        # Step 5: Save to database
        with get_db() as conn:
            conn.execute(
                "UPDATE anomaly_events SET clip_path = ? WHERE id = ?",
                (metadata["clip_path"], anomaly_id)
            )

        metadata["pre_event_seconds"] = self.pre_seconds
        metadata["post_event_seconds"] = self.post_seconds

        return metadata

    async def _capture_post_event(self, sensor_id: str, seconds: float) -> list:
        """Capture post-event frames for the specified duration."""
        frames = []
        fps = 15
        total_frames = int(seconds * fps)
        frame_interval = 1.0 / fps

        queue = sensor_pipeline.register_frame_queue(sensor_id)

        try:
            for _ in range(total_frames):
                try:
                    frame = await asyncio.wait_for(queue.get(), timeout=frame_interval * 3)
                    frames.append({
                        "frame_data": frame.get("frame_data", ""),
                        "timestamp": frame.get("timestamp", datetime.utcnow().isoformat()),
                        "resolution": frame.get("resolution", [640, 480])
                    })
                except asyncio.TimeoutError:
                    break
        finally:
            sensor_pipeline.unregister_frame_queue(sensor_id)

        return frames

    def get_clip_metadata(self, anomaly_id: int) -> Optional[dict]:
        """Get clip metadata from the database."""
        with get_db() as conn:
            row = conn.execute(
                "SELECT id, clip_path, detected_at FROM anomaly_events WHERE id = ? AND clip_path IS NOT NULL",
                (anomaly_id,)
            ).fetchone()
        if not row:
            return None
        event = dict(row)
        return {
            "anomaly_id": event["id"],
            "clip_path": event["clip_path"],
            "created_at": event["detected_at"]
        }


# Singleton instance
clip_extractor = ClipExtractor()
