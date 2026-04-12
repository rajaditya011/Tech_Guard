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
