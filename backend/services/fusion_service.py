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

        # Spatial inconsistency increases suspicion
        spatial_boost = 0.0
        if spatial_consistency < 0.4:
            spatial_boost = 0.15

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
