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
        # Deterministic zone encoding
        import hashlib
        zone_hash = int(hashlib.md5(zone.encode()).hexdigest(), 16) % 100

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
