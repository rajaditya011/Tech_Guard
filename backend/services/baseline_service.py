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
