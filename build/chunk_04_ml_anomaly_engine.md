# Chunk 04 — ML and Anomaly Detection Engine

**Goal**: Build the behavioral baseline builder, YOLO inference runner, Isolation Forest anomaly detector, multi-sensor fusion engine, and dynamic risk score calculator.
**Estimated Time**: 60 minutes
**Dependencies**: Chunk 03 (Sensor Pipeline)
**Unlocks**: Chunk 05 (Intelligence Response Layer)

---

## 04.1 — Baseline Service (backend/services/baseline_service.py)

```python
"""
HomeGuardian AI — Behavioral Baseline Builder
7-14 day passive observation phase. Builds per-zone, per-hour activity profiles.
"""

import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from database import get_db
from config import settings

logger = logging.getLogger("homeguardian.baseline")

try:
    from sklearn.cluster import DBSCAN
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Trajectory clustering will use fallback.")


class BaselineBuilder:
    """Builds behavioral baseline profiles from sensor observation data."""

    def __init__(self):
        self.baseline_days = settings.BASELINE_DAYS
        self._observation_buffer: Dict[str, List[dict]] = {}

    def record_observation(self, sensor_id: str, zone: str, movement_data: dict):
        """
        Record a single observation for baseline building.
        Called for every analyzed frame during the learning phase.
        """
        now = datetime.utcnow()
        observation = {
            "sensor_id": sensor_id,
            "zone": zone,
            "hour_of_day": now.hour,
            "day_of_week": now.weekday(),
            "movement_speed": movement_data.get("speed", 0.0),
            "trajectory_x": movement_data.get("trajectory_x", 0.0),
            "trajectory_y": movement_data.get("trajectory_y", 0.0),
            "timestamp": now.isoformat()
        }

        key = f"{sensor_id}:{zone}"
        if key not in self._observation_buffer:
            self._observation_buffer[key] = []
        self._observation_buffer[key].append(observation)

        # Flush to database periodically (every 100 observations)
        if len(self._observation_buffer[key]) >= 100:
            self._flush_observations(sensor_id, zone)

    def _flush_observations(self, sensor_id: str, zone: str):
        """Flush buffered observations to the database baseline profiles."""
        key = f"{sensor_id}:{zone}"
        observations = self._observation_buffer.get(key, [])
        if not observations:
            return

        # Group by hour and day
        groups: Dict[Tuple[int, int], List[dict]] = {}
        for obs in observations:
            group_key = (obs["hour_of_day"], obs["day_of_week"])
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(obs)

        with get_db() as conn:
            for (hour, day), group_obs in groups.items():
                # Calculate statistics
                speeds = [o["movement_speed"] for o in group_obs]
                avg_speed = float(np.mean(speeds)) if speeds else 0.0
                activity_prob = len(group_obs) / max(len(observations), 1)

                # Trajectory clustering
                centroids = self._cluster_trajectories(group_obs)

                # Upsert baseline profile
                existing = conn.execute(
                    """SELECT id, sample_count FROM baseline_profiles
                       WHERE sensor_node_id = ? AND zone = ? AND hour_of_day = ? AND day_of_week = ?""",
                    (sensor_id, zone, hour, day)
                ).fetchone()

                if existing:
                    new_count = existing["sample_count"] + len(group_obs)
                    conn.execute(
                        """UPDATE baseline_profiles SET
                           activity_probability = ?,
                           avg_movement_speed = ?,
                           trajectory_cluster_centroids = ?,
                           sample_count = ?,
                           last_updated = ?
                           WHERE id = ?""",
                        (activity_prob, avg_speed, json.dumps(centroids),
                         new_count, datetime.utcnow().isoformat(), existing["id"])
                    )
                else:
                    conn.execute(
                        """INSERT INTO baseline_profiles
                           (sensor_node_id, zone, hour_of_day, day_of_week,
                            activity_probability, avg_movement_speed,
                            trajectory_cluster_centroids, sample_count)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (sensor_id, zone, hour, day,
                         activity_prob, avg_speed, json.dumps(centroids), len(group_obs))
                    )

        # Clear buffer
        self._observation_buffer[key] = []
        logger.debug(f"Flushed {len(observations)} observations for {sensor_id}:{zone}")

    def _cluster_trajectories(self, observations: List[dict]) -> list:
        """Cluster movement trajectories using DBSCAN."""
        if not SKLEARN_AVAILABLE or len(observations) < 5:
            return []

        trajectories = np.array([
            [obs["trajectory_x"], obs["trajectory_y"]]
            for obs in observations
        ])

        try:
            clustering = DBSCAN(eps=0.5, min_samples=3).fit(trajectories)
            labels = clustering.labels_
            unique_labels = set(labels) - {-1}

            centroids = []
            for label in unique_labels:
                mask = labels == label
                centroid = trajectories[mask].mean(axis=0).tolist()
                centroids.append(centroid)

            return centroids
        except Exception as e:
            logger.error(f"Trajectory clustering failed: {e}")
            return []

    def get_baseline_profile(self, zone: str, hour: int, day: int) -> Optional[dict]:
        """Get the baseline profile for a specific zone, hour, and day."""
        with get_db() as conn:
            row = conn.execute(
                """SELECT * FROM baseline_profiles
                   WHERE zone = ? AND hour_of_day = ? AND day_of_week = ?""",
                (zone, hour, day)
            ).fetchone()
        if row:
            profile = dict(row)
            if profile.get("trajectory_cluster_centroids"):
                profile["trajectory_cluster_centroids"] = json.loads(
                    profile["trajectory_cluster_centroids"]
                )
            return profile
        return None

    def get_baseline_status(self, sensor_id: str) -> dict:
        """Get the baseline learning progress for a sensor."""
        with get_db() as conn:
            sensor = conn.execute(
                "SELECT enrolled_at FROM sensor_nodes WHERE id = ?",
                (sensor_id,)
            ).fetchone()

            if not sensor:
                return {"error": "Sensor not found"}

            enrolled_at = datetime.fromisoformat(sensor["enrolled_at"])
            days_elapsed = (datetime.utcnow() - enrolled_at).days
            days_complete = min(days_elapsed, self.baseline_days)
            percent = (days_complete / self.baseline_days) * 100

            # Get zones being learned
            zones = conn.execute(
                "SELECT DISTINCT zone FROM baseline_profiles WHERE sensor_node_id = ?",
                (sensor_id,)
            ).fetchall()
            zone_list = [z["zone"] for z in zones]

            # Get sample counts per zone
            samples = conn.execute(
                """SELECT zone, SUM(sample_count) as total FROM baseline_profiles
                   WHERE sensor_node_id = ? GROUP BY zone""",
                (sensor_id,)
            ).fetchall()
            sample_counts = {s["zone"]: s["total"] for s in samples}

        completion_date = enrolled_at + timedelta(days=self.baseline_days)

        return {
            "sensor_id": sensor_id,
            "days_complete": days_complete,
            "days_required": self.baseline_days,
            "percent_complete": round(percent, 1),
            "zones_learning": zone_list,
            "sample_counts": sample_counts,
            "estimated_completion": completion_date.isoformat() if percent < 100 else None,
            "is_complete": days_complete >= self.baseline_days
        }

    def compute_deviation(self, zone: str, hour: int, day: int,
                          current_speed: float, current_trajectory: list) -> float:
        """
        Compute how much a current observation deviates from the baseline.
        Returns a deviation score (0 = matches baseline, higher = more unusual).
        """
        profile = self.get_baseline_profile(zone, hour, day)
        if not profile:
            # No baseline = everything is unusual
            return 1.0

        deviation = 0.0

        # Activity probability deviation
        if profile["activity_probability"] < 0.05:
            # Zone normally has near-zero activity at this time
            deviation += 0.5

        # Speed deviation
        speed_diff = abs(current_speed - profile["avg_movement_speed"])
        if profile["avg_movement_speed"] > 0:
            speed_ratio = speed_diff / profile["avg_movement_speed"]
            deviation += min(speed_ratio * 0.2, 0.3)

        # Trajectory deviation from known clusters
        centroids = profile.get("trajectory_cluster_centroids", [])
        if centroids and current_trajectory:
            min_dist = float('inf')
            for centroid in centroids:
                dist = np.sqrt(
                    (current_trajectory[0] - centroid[0]) ** 2 +
                    (current_trajectory[1] - centroid[1]) ** 2
                )
                min_dist = min(min_dist, dist)
            # Normalize distance (arbitrary scale — tune based on real data)
            deviation += min(min_dist * 0.1, 0.2)

        return min(deviation, 1.0)


# Singleton instance
baseline_builder = BaselineBuilder()
```

---

## 04.2 — YOLO Service (backend/services/yolo_service.py)

```python
"""
HomeGuardian AI — YOLO Inference Runner
Real-time object detection on video frames.
"""

import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
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
```

---

## 04.3 — Anomaly Detection Service (backend/services/anomaly_service.py)

```python
"""
HomeGuardian AI — Anomaly Detection
Isolation Forest-based anomaly scoring with baseline comparison.
"""

import logging
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional

from database import get_db
from config import settings

logger = logging.getLogger("homeguardian.anomaly")

try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Anomaly detection will use threshold-based fallback.")


class AnomalyDetector:
    """Isolation Forest-based anomaly detection engine."""

    def __init__(self):
        self.model: Optional[IsolationForest] = None
        self.threshold = settings.ANOMALY_THRESHOLD
        self._feature_history: List[np.ndarray] = []
        self._is_trained = False
        self._min_training_samples = 100

    def build_feature_vector(self, zone: str, hour: int, day_of_week: int,
                              movement_speed: float, trajectory_angle: float,
                              zone_transition_count: int) -> np.ndarray:
        """
        Construct the feature vector for anomaly scoring.
        Features: zone_encoded, hour, day, speed, angle, transition_count
        """
        # Simple zone encoding (hash to numeric)
        zone_hash = hash(zone) % 100

        return np.array([
            zone_hash,
            hour,
            day_of_week,
            movement_speed,
            trajectory_angle,
            zone_transition_count
        ]).reshape(1, -1)

    def train(self, feature_vectors: List[np.ndarray]):
        """Train the Isolation Forest on baseline data."""
        if not SKLEARN_AVAILABLE:
            logger.warning("Cannot train: scikit-learn not available")
            return

        if len(feature_vectors) < self._min_training_samples:
            logger.info(f"Not enough samples to train ({len(feature_vectors)}/{self._min_training_samples})")
            return

        try:
            X = np.vstack(feature_vectors)
            self.model = IsolationForest(
                n_estimators=100,
                contamination=0.05,  # Expect 5% anomalies
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(X)
            self._is_trained = True
            logger.info(f"Isolation Forest trained on {len(feature_vectors)} samples")
        except Exception as e:
            logger.error(f"Training failed: {e}")

    def score(self, feature_vector: np.ndarray) -> float:
        """
        Score a feature vector for anomaly.
        Returns: anomaly score (0.0 = normal, 1.0 = highly anomalous)
        """
        # Store for future training
        self._feature_history.append(feature_vector)

        if self._is_trained and self.model is not None:
            try:
                # Isolation Forest returns negative scores; lower = more anomalous
                raw_score = self.model.decision_function(feature_vector)[0]
                # Convert to 0-1 range (more positive raw = more normal)
                normalized = max(0.0, min(1.0, 0.5 - raw_score))
                return round(normalized, 4)
            except Exception as e:
                logger.error(f"Scoring failed: {e}")
                return 0.0
        else:
            # Fallback: threshold-based scoring
            return self._threshold_score(feature_vector)

    def _threshold_score(self, feature_vector: np.ndarray) -> float:
        """Simple threshold-based fallback scoring."""
        hour = feature_vector[0, 1]
        speed = feature_vector[0, 3]

        score = 0.0

        # Night time activity is more suspicious
        if 0 <= hour <= 5:
            score += 0.3
        elif 22 <= hour <= 23:
            score += 0.15

        # High speed is more suspicious
        if speed > 10:
            score += 0.2
        elif speed > 5:
            score += 0.1

        return min(score, 1.0)

    def is_anomaly(self, score: float) -> bool:
        """Check if a score exceeds the anomaly threshold."""
        return score >= self.threshold

    def classify_anomaly(self, score: float, context: dict) -> str:
        """Classify the type of anomaly based on score and context."""
        hour = context.get("hour", 12)
        zone = context.get("zone", "unknown")
        speed = context.get("speed", 0)

        if score >= 0.9:
            return "critical_deviation"
        elif score >= 0.75:
            if 0 <= hour <= 5:
                return "suspicious_nighttime_activity"
            elif speed > 10:
                return "rapid_movement_anomaly"
            else:
                return "significant_behavioral_deviation"
        elif score >= 0.5:
            return "unfamiliar_movement_pattern"
        else:
            return "minor_deviation"

    @property
    def training_samples(self) -> int:
        return len(self._feature_history)

    def auto_retrain_if_needed(self):
        """Automatically retrain if enough new samples are available."""
        if len(self._feature_history) >= self._min_training_samples * 2:
            self.train(self._feature_history[-self._min_training_samples * 5:])


# Singleton instance
anomaly_detector = AnomalyDetector()
```

---

## 04.4 — Multi-Sensor Fusion (backend/services/fusion_service.py)

```python
"""
HomeGuardian AI — Multi-Sensor Fusion Engine
Cross-correlates events across sensor nodes for spatial consistency.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger("homeguardian.fusion")


class SensorEvent:
    """Represents a detection event from a single sensor."""
    def __init__(self, sensor_id: str, zone: str, timestamp: datetime,
                 detection: dict, anomaly_score: float):
        self.sensor_id = sensor_id
        self.zone = zone
        self.timestamp = timestamp
        self.detection = detection
        self.anomaly_score = anomaly_score


class FusionEngine:
    """Cross-correlates events across multiple sensors."""

    # Time window for considering events as simultaneous
    CORRELATION_WINDOW_SECONDS = 5.0

    # Zone adjacency map (defines which zones are neighbors)
    # This would be configured per home; using a default for demo
    ZONE_ADJACENCY = {
        "front_door": ["hallway", "porch"],
        "hallway": ["front_door", "living_room", "kitchen", "bedroom"],
        "living_room": ["hallway", "kitchen"],
        "kitchen": ["hallway", "living_room"],
        "bedroom": ["hallway", "bathroom"],
        "bathroom": ["bedroom"],
        "backyard": ["kitchen"],
        "porch": ["front_door"],
        "garage": ["hallway"]
    }

    def __init__(self):
        self._event_buffer: List[SensorEvent] = []
        self._max_buffer_size = 1000

    def add_event(self, event: SensorEvent):
        """Add a new sensor event to the fusion buffer."""
        self._event_buffer.append(event)
        # Trim old events
        if len(self._event_buffer) > self._max_buffer_size:
            cutoff = datetime.utcnow() - timedelta(minutes=5)
            self._event_buffer = [
                e for e in self._event_buffer if e.timestamp > cutoff
            ]

    def find_correlated_events(self, target_event: SensorEvent) -> List[SensorEvent]:
        """Find events that are temporally and spatially correlated."""
        correlated = []
        window = timedelta(seconds=self.CORRELATION_WINDOW_SECONDS)

        for event in self._event_buffer:
            if event.sensor_id == target_event.sensor_id:
                continue
            # Check temporal correlation
            time_diff = abs((event.timestamp - target_event.timestamp).total_seconds())
            if time_diff <= self.CORRELATION_WINDOW_SECONDS:
                correlated.append(event)

        return correlated

    def compute_spatial_consistency(self, events: List[SensorEvent]) -> float:
        """
        Check if events across sensors are spatially consistent.
        Returns consistency score (0-1).
        """
        if len(events) < 2:
            return 0.5  # Neutral — not enough data

        zones = [e.zone for e in events]
        consistency = 0.0
        pair_count = 0

        for i in range(len(zones)):
            for j in range(i + 1, len(zones)):
                pair_count += 1
                zone_a = zones[i]
                zone_b = zones[j]

                if zone_a == zone_b:
                    consistency += 1.0
                elif zone_b in self.ZONE_ADJACENCY.get(zone_a, []):
                    consistency += 0.7
                else:
                    consistency += 0.2

        return round(consistency / max(pair_count, 1), 3)

    def compute_compound_score(self, target_event: SensorEvent) -> dict:
        """
        Compute a compound event score by fusing data across sensors.
        Returns enhanced scoring with multi-sensor context.
        """
        correlated = self.find_correlated_events(target_event)

        if not correlated:
            return {
                "compound_score": target_event.anomaly_score,
                "sensor_count": 1,
                "correlated_sensors": [],
                "spatial_consistency": 0.5,
                "confidence_boost": 0.0,
                "reasoning": "Single sensor event — no corroborating data available."
            }

        all_events = [target_event] + correlated
        spatial_consistency = self.compute_spatial_consistency(all_events)

        # Compute compound score
        avg_anomaly = sum(e.anomaly_score for e in all_events) / len(all_events)
        sensor_count = len(set(e.sensor_id for e in all_events))

        # Multi-sensor confirmation boosts confidence
        confirmation_boost = min(0.2 * (sensor_count - 1), 0.4)

        # Spatial inconsistency (e.g., motion in living room but not hallway)
        # increases suspicion
        spatial_boost = 0.0
        if spatial_consistency < 0.4:
            spatial_boost = 0.15  # Suspicious: activity in non-adjacent zones

        compound_score = min(1.0, avg_anomaly + confirmation_boost + spatial_boost)

        # Build reasoning
        sensor_ids = [e.sensor_id for e in correlated]
        zones_involved = list(set(e.zone for e in all_events))

        if spatial_consistency < 0.4:
            reasoning = (
                f"Activity detected across {sensor_count} sensors in non-adjacent zones "
                f"({', '.join(zones_involved)}). Spatial inconsistency increases suspicion."
            )
        elif sensor_count > 1:
            reasoning = (
                f"Event confirmed across {sensor_count} sensors in zones: "
                f"{', '.join(zones_involved)}. Multi-sensor confirmation increases confidence."
            )
        else:
            reasoning = "Single sensor detection."

        return {
            "compound_score": round(compound_score, 4),
            "sensor_count": sensor_count,
            "correlated_sensors": sensor_ids,
            "spatial_consistency": spatial_consistency,
            "confidence_boost": round(confirmation_boost + spatial_boost, 3),
            "zones_involved": zones_involved,
            "reasoning": reasoning
        }


# Singleton instance
fusion_engine = FusionEngine()
```

---

## 04.5 — Risk Score Calculator (backend/services/risk_service.py)

```python
"""
HomeGuardian AI — Dynamic Risk Score Calculator
Computes and updates risk scores in real time.
"""

import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger("homeguardian.risk")


class RiskScoreCalculator:
    """
    Calculates dynamic risk scores for anomaly events.
    Score factors and weights:
      - Baseline deviation: 40%
      - Time of day risk: 20%
      - Zone sensitivity: 20%
      - Event duration: 10%
      - Multi-sensor confirmation: 10%
    """

    # Zone sensitivity levels (configurable per home)
    ZONE_SENSITIVITY = {
        "front_door": 0.9,
        "back_door": 0.85,
        "garage": 0.8,
        "porch": 0.7,
        "hallway": 0.5,
        "living_room": 0.4,
        "kitchen": 0.3,
        "bedroom": 0.6,
        "bathroom": 0.2,
        "backyard": 0.7
    }

    def __init__(self):
        self._active_scores: Dict[int, dict] = {}

    def calculate_initial_score(self, anomaly_score: float, zone: str,
                                 hour: int, duration_seconds: float,
                                 sensor_count: int, baseline_deviation: float) -> dict:
        """
        Calculate the initial risk score for a new anomaly event.
        Returns score details with breakdown.
        """
        # Factor 1: Baseline deviation (40%)
        deviation_factor = min(baseline_deviation, 1.0)

        # Factor 2: Time of day risk (20%)
        if 0 <= hour <= 5:
            time_factor = 1.0
        elif 22 <= hour <= 23:
            time_factor = 0.7
        elif 6 <= hour <= 8:
            time_factor = 0.3
        else:
            time_factor = 0.2

        # Factor 3: Zone sensitivity (20%)
        zone_factor = self.ZONE_SENSITIVITY.get(zone, 0.5)

        # Factor 4: Event duration (10%)
        if duration_seconds > 60:
            duration_factor = 1.0
        elif duration_seconds > 30:
            duration_factor = 0.7
        elif duration_seconds > 10:
            duration_factor = 0.4
        else:
            duration_factor = 0.2

        # Factor 5: Multi-sensor confirmation (10%)
        if sensor_count >= 3:
            sensor_factor = 1.0
        elif sensor_count == 2:
            sensor_factor = 0.7
        else:
            sensor_factor = 0.3

        # Weighted score (0-100)
        raw_score = (
            deviation_factor * 0.40 +
            time_factor * 0.20 +
            zone_factor * 0.20 +
            duration_factor * 0.10 +
            sensor_factor * 0.10
        )

        score = int(round(raw_score * 100))
        risk_level = self.classify_risk(score)

        factors = {
            "baseline_deviation": round(deviation_factor, 3),
            "time_of_day_risk": round(time_factor, 3),
            "zone_sensitivity": round(zone_factor, 3),
            "event_duration": round(duration_factor, 3),
            "multi_sensor_confirmation": round(sensor_factor, 3)
        }

        return {
            "score": score,
            "risk_level": risk_level,
            "factors": factors,
            "trend": "initial",
            "timestamp": datetime.utcnow().isoformat()
        }

    def update_score(self, anomaly_id: int, new_data: dict) -> dict:
        """
        Update an existing risk score with new information.
        Supports real-time escalation and de-escalation.
        """
        current = self._active_scores.get(anomaly_id)
        if not current:
            return {"error": "No active score for this anomaly"}

        previous_score = current["score"]

        # Recalculate with new data
        if "additional_sensors" in new_data:
            current["factors"]["multi_sensor_confirmation"] = min(
                current["factors"]["multi_sensor_confirmation"] + 0.2, 1.0
            )
        if "duration_update" in new_data:
            duration = new_data["duration_update"]
            if duration > 60:
                current["factors"]["event_duration"] = 1.0
            elif duration > 30:
                current["factors"]["event_duration"] = 0.7

        # Recalculate score
        f = current["factors"]
        raw_score = (
            f["baseline_deviation"] * 0.40 +
            f["time_of_day_risk"] * 0.20 +
            f["zone_sensitivity"] * 0.20 +
            f["event_duration"] * 0.10 +
            f["multi_sensor_confirmation"] * 0.10
        )

        new_score = int(round(raw_score * 100))

        # Determine trend
        if new_score > previous_score:
            trend = "escalating"
        elif new_score < previous_score:
            trend = "de-escalating"
        else:
            trend = "stable"

        current["score"] = new_score
        current["risk_level"] = self.classify_risk(new_score)
        current["trend"] = trend
        current["timestamp"] = datetime.utcnow().isoformat()

        self._active_scores[anomaly_id] = current
        return current

    def register_active_score(self, anomaly_id: int, score_data: dict):
        """Register a score for real-time tracking."""
        self._active_scores[anomaly_id] = score_data

    def deregister_score(self, anomaly_id: int):
        """Remove a score from active tracking."""
        self._active_scores.pop(anomaly_id, None)

    @staticmethod
    def classify_risk(score: int) -> str:
        """Classify risk level from score."""
        if score >= 76:
            return "critical"
        elif score >= 51:
            return "high"
        elif score >= 26:
            return "medium"
        else:
            return "low"

    def get_system_risk(self) -> dict:
        """Get the current system-wide risk score."""
        if not self._active_scores:
            return {
                "score": 0,
                "risk_level": "low",
                "active_anomalies": 0,
                "trend": "stable"
            }

        max_score = max(s["score"] for s in self._active_scores.values())
        return {
            "score": max_score,
            "risk_level": self.classify_risk(max_score),
            "active_anomalies": len(self._active_scores),
            "trend": "escalating" if any(
                s["trend"] == "escalating" for s in self._active_scores.values()
            ) else "stable"
        }


# Singleton instance
risk_calculator = RiskScoreCalculator()
```

---

## 04.6 — Anomaly Routes (backend/routers/anomaly_routes.py)

```python
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
```

Add to `main.py`:
```python
from routers.anomaly_routes import router as anomaly_router
app.include_router(anomaly_router, prefix="/api/anomalies", tags=["Anomalies"])
```

---

## Verification

```bash
# 1. Test baseline builder
cd backend
source venv/bin/activate
python -c "
from services.baseline_service import baseline_builder
baseline_builder.record_observation('test-sensor', 'living_room', {'speed': 5.0, 'trajectory_x': 1.0, 'trajectory_y': 2.0})
status = baseline_builder.get_baseline_status('test-sensor')
print('Baseline status:', status)
print('Baseline builder test PASSED')
"

# 2. Test anomaly detector
python -c "
from services.anomaly_service import anomaly_detector
import numpy as np
fv = anomaly_detector.build_feature_vector('living_room', 3, 0, 12.5, 45.0, 2)
score = anomaly_detector.score(fv)
print(f'Anomaly score: {score}')
print(f'Is anomaly: {anomaly_detector.is_anomaly(score)}')
print('Anomaly detector test PASSED')
"

# 3. Test risk calculator
python -c "
from services.risk_service import risk_calculator
result = risk_calculator.calculate_initial_score(0.8, 'front_door', 3, 45, 2, 0.85)
print(f'Risk score: {result[\"score\"]}')
print(f'Risk level: {result[\"risk_level\"]}')
print(f'Factors: {result[\"factors\"]}')
print('Risk calculator test PASSED')
"

# 4. Test fusion engine
python -c "
from services.fusion_service import fusion_engine, SensorEvent
from datetime import datetime
e1 = SensorEvent('sensor-1', 'front_door', datetime.utcnow(), {'class':'person'}, 0.7)
e2 = SensorEvent('sensor-2', 'hallway', datetime.utcnow(), {'class':'person'}, 0.6)
fusion_engine.add_event(e1)
fusion_engine.add_event(e2)
result = fusion_engine.compute_compound_score(e1)
print(f'Compound score: {result[\"compound_score\"]}')
print(f'Reasoning: {result[\"reasoning\"]}')
print('Fusion engine test PASSED')
"

# 5. Test anomaly routes
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/anomalies
```

Expected: All four unit tests pass. Anomaly routes return empty list (no events yet). Baseline builder records observations successfully.
