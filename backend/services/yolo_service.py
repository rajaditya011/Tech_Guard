"""
HomeGuardian AI — YOLO Inference Runner
Real-time object detection on video frames.
"""

import logging
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path

from config import settings

logger = logging.getLogger("homeguardian.yolo")

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.warning("Ultralytics not available. YOLO inference will use demo mode.")


class YOLOService:
    """Runs YOLO inference for human detection and tracking."""

    # COCO class IDs for relevant objects
    PERSON_CLASS_ID = 0
    CONFIDENCE_THRESHOLD = 0.5

    def __init__(self):
        self.model = None
        self._previous_detections: Dict[str, List[dict]] = {}

    def load_model(self):
        """Load the YOLO model."""
        if not YOLO_AVAILABLE:
            logger.warning("YOLO not available — running in demo mode")
            return

        model_path = Path(settings.YOLO_MODEL_PATH)
        if not model_path.exists():
            logger.warning(f"YOLO model not found at {model_path}. Attempting download...")
            try:
                self.model = YOLO("yolov8n.pt")
                logger.info("YOLO model downloaded and loaded")
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")
                return
        else:
            try:
                self.model = YOLO(str(model_path))
                logger.info(f"YOLO model loaded from {model_path}")
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")

    def detect(self, frame: np.ndarray, sensor_id: str = "") -> List[dict]:
        """
        Run YOLO inference on a frame.
        Returns list of detection dicts with bounding boxes and classification.
        """
        if self.model is None or not YOLO_AVAILABLE:
            return self._demo_detections()

        try:
            results = self.model(frame, verbose=False, conf=self.CONFIDENCE_THRESHOLD)

            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])

                    if class_id == self.PERSON_CLASS_ID:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2

                        detection = {
                            "class": "person",
                            "confidence": round(confidence, 3),
                            "bbox": {
                                "x1": round(x1, 1),
                                "y1": round(y1, 1),
                                "x2": round(x2, 1),
                                "y2": round(y2, 1)
                            },
                            "center": {
                                "x": round(center_x, 1),
                                "y": round(center_y, 1)
                            },
                            "area": round((x2 - x1) * (y2 - y1), 1)
                        }

                        # Calculate movement vector if previous detections exist
                        movement = self._calculate_movement(sensor_id, detection)
                        detection["movement"] = movement

                        detections.append(detection)

            # Store for next frame's movement calculation
            self._previous_detections[sensor_id] = detections

            return detections

        except Exception as e:
            logger.error(f"YOLO inference failed: {e}")
            return []

    def _calculate_movement(self, sensor_id: str, current: dict) -> dict:
        """Calculate movement vector from previous detection."""
        prev = self._previous_detections.get(sensor_id, [])
        if not prev:
            return {"speed": 0.0, "direction_x": 0.0, "direction_y": 0.0, "angle": 0.0}

        # Find closest previous detection (simple nearest-neighbor tracking)
        min_dist = float('inf')
        closest = None
        for p in prev:
            dx = current["center"]["x"] - p["center"]["x"]
            dy = current["center"]["y"] - p["center"]["y"]
            dist = np.sqrt(dx**2 + dy**2)
            if dist < min_dist:
                min_dist = dist
                closest = p

        if closest and min_dist < 200:  # Maximum tracking distance
            dx = current["center"]["x"] - closest["center"]["x"]
            dy = current["center"]["y"] - closest["center"]["y"]
            speed = np.sqrt(dx**2 + dy**2)
            angle = float(np.degrees(np.arctan2(dy, dx)))

            return {
                "speed": round(speed, 2),
                "direction_x": round(dx, 2),
                "direction_y": round(dy, 2),
                "angle": round(angle, 2)
            }

        return {"speed": 0.0, "direction_x": 0.0, "direction_y": 0.0, "angle": 0.0}

    def _demo_detections(self) -> List[dict]:
        """Return synthetic detections for demo mode."""
        import random
        if random.random() < 0.3:  # 30% chance of detection in demo
            return [{
                "class": "person",
                "confidence": round(random.uniform(0.7, 0.95), 3),
                "bbox": {
                    "x1": round(random.uniform(100, 300), 1),
                    "y1": round(random.uniform(50, 200), 1),
                    "x2": round(random.uniform(350, 550), 1),
                    "y2": round(random.uniform(250, 450), 1)
                },
                "center": {
                    "x": round(random.uniform(200, 450), 1),
                    "y": round(random.uniform(150, 350), 1)
                },
                "area": round(random.uniform(20000, 80000), 1),
                "movement": {
                    "speed": round(random.uniform(0, 15), 2),
                    "direction_x": round(random.uniform(-10, 10), 2),
                    "direction_y": round(random.uniform(-10, 10), 2),
                    "angle": round(random.uniform(-180, 180), 2)
                }
            }]
        return []


# Singleton instance
yolo_service = YOLOService()
