"""
HomeGuardian AI — Video Encoder
Encodes frames into MP4 clips with timestamp overlay.
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import List

from config import settings

logger = logging.getLogger("homeguardian.encoder")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available. Video encoding will be simulated.")


class VideoEncoder:
    """Encodes frame sequences into MP4 video clips."""

    CLIPS_DIR = Path(__file__).parent.parent / "clips"
    FPS = 15
    CODEC = "mp4v"

    @classmethod
    def encode_clip(cls, frames: List[dict], anomaly_id: int,
                    sensor_id: str, zone: str, anomaly_score: float) -> dict:
        """
        Encode a list of frames into an MP4 clip.
        Returns clip metadata.
        """
        cls.CLIPS_DIR.mkdir(parents=True, exist_ok=True)

        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"anomaly_{anomaly_id}_{timestamp_str}.mp4"
        filepath = cls.CLIPS_DIR / filename

        if not CV2_AVAILABLE or not frames:
            return cls._create_placeholder_clip(filepath, anomaly_id, sensor_id, zone)

        try:
            import base64
            first_frame_data = frames[0]["data"].get("frame_data", "")
            if not first_frame_data:
                return cls._create_placeholder_clip(filepath, anomaly_id, sensor_id, zone)

            first_bytes = base64.b64decode(first_frame_data)
            first_np = np.frombuffer(first_bytes, np.uint8)
            first_frame = cv2.imdecode(first_np, cv2.IMREAD_COLOR)

            if first_frame is None:
                return cls._create_placeholder_clip(filepath, anomaly_id, sensor_id, zone)

            h, w = first_frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*cls.CODEC)
            writer = cv2.VideoWriter(str(filepath), fourcc, cls.FPS, (w, h))

            frames_written = 0
            for frame_entry in frames:
                frame_data = frame_entry["data"].get("frame_data", "")
                if not frame_data:
                    continue

                frame_bytes = base64.b64decode(frame_data)
                frame_np = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)

                if frame is not None:
                    ts = frame_entry.get("timestamp", "")
                    if ts:
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        text_size = cv2.getTextSize(ts, font, 0.5, 1)[0]
                        cv2.rectangle(frame, (8, h - 10 - text_size[1] - 4),
                                     (12 + text_size[0], h - 6), (0, 0, 0), -1)
                        cv2.putText(frame, ts, (10, h - 10), font, 0.5,
                                   (255, 255, 255), 1)
                    writer.write(frame)
                    frames_written += 1

            writer.release()

            duration = frames_written / cls.FPS if cls.FPS > 0 else 0

            metadata = {
                "anomaly_id": anomaly_id,
                "clip_path": str(filepath),
                "filename": filename,
                "duration_seconds": round(duration, 2),
                "frames_written": frames_written,
                "resolution": f"{w}x{h}",
                "sensor_id": sensor_id,
                "zone": zone,
                "anomaly_score": anomaly_score,
                "created_at": datetime.utcnow().isoformat()
            }

            logger.info(f"Clip encoded: {filename} ({frames_written} frames, {duration:.1f}s)")
            return metadata

        except Exception as e:
            logger.error(f"Clip encoding failed: {e}")
            return cls._create_placeholder_clip(filepath, anomaly_id, sensor_id, zone)

    @classmethod
    def _create_placeholder_clip(cls, filepath: Path, anomaly_id: int,
                                  sensor_id: str, zone: str) -> dict:
        """Create placeholder metadata when encoding is not possible."""
        filepath.touch()
        return {
            "anomaly_id": anomaly_id,
            "clip_path": str(filepath),
            "filename": filepath.name,
            "duration_seconds": 15.0,
            "frames_written": 0,
            "resolution": "640x480",
            "sensor_id": sensor_id,
            "zone": zone,
            "anomaly_score": 0.0,
            "created_at": datetime.utcnow().isoformat(),
            "placeholder": True
        }
