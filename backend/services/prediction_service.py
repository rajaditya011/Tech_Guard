"""
HomeGuardian AI — Adaptive Surveillance Replay and Prediction Engine (F11)
Intrusion scenario library, sequence matching, and predictive alerting.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from database import get_db

logger = logging.getLogger("homeguardian.prediction")


# ============================================================
# Intrusion Scenario Definitions
# ============================================================
SCENARIO_LIBRARY = [
    {
        "name": "Standard Home Intrusion",
        "phases": [
            {
                "id": "casing",
                "label": "Casing",
                "description": "Slow perimeter movement, repeated passes, no entry attempt",
                "signatures": {
                    "zone_types": ["front_door", "porch", "backyard", "garage"],
                    "movement_speed_range": [1.0, 5.0],
                    "min_duration_seconds": 15,
                    "repeated_passes": True,
                    "entry_attempt": False,
                    "time_pattern": "any"
                }
            },
            {
                "id": "entry_probing",
                "label": "Entry Probing",
                "description": "Testing doors and windows, brief contact events",
                "signatures": {
                    "zone_types": ["front_door", "back_door", "garage"],
                    "movement_speed_range": [0.5, 3.0],
                    "min_duration_seconds": 5,
                    "contact_events": True,
                    "brief_stops": True,
                    "time_pattern": "any"
                }
            },
            {
                "id": "reconnaissance",
                "label": "Reconnaissance",
                "description": "Interior movement, exploring rooms",
                "signatures": {
                    "zone_types": ["hallway", "living_room", "kitchen", "bedroom"],
                    "movement_speed_range": [2.0, 8.0],
                    "min_duration_seconds": 10,
                    "zone_transitions": 2,
                    "unfamiliar_trajectory": True,
                    "time_pattern": "any"
                }
            },
            {
                "id": "intrusion",
                "label": "Intrusion",
                "description": "Extended unfamiliar presence, rapid movement",
                "signatures": {
                    "zone_types": ["any"],
                    "movement_speed_range": [3.0, 20.0],
                    "min_duration_seconds": 30,
                    "extended_presence": True,
                    "unfamiliar_trajectory": True,
                    "time_pattern": "nighttime_preferred"
                }
            }
        ]
    }
]


class PredictionEngine:
    """
    Adaptive Surveillance Replay and Prediction Engine.
    Matches live sensor events against intrusion scenario phase signatures.
    """

    def __init__(self):
        self._active_matches: Dict[str, dict] = {}
        self._event_history: List[dict] = []
        self._reasoning_timeline: Dict[int, List[dict]] = {}
        self._scenario_library_initialized = False

    def _ensure_scenario_library(self):
        """Lazily initialize scenario library when DB is ready."""
        if self._scenario_library_initialized:
            return
        self._init_scenario_library()
        self._scenario_library_initialized = True

    def _init_scenario_library(self):
        """Initialize the scenario library in the database."""
        try:
            with get_db() as conn:
                for scenario in SCENARIO_LIBRARY:
                    existing = conn.execute(
                        "SELECT id FROM scenario_library WHERE name = ?",
                        (scenario["name"],)
                    ).fetchone()
                    if not existing:
                        conn.execute(
                            """INSERT INTO scenario_library (name, phase_count, phase_definitions_json)
                               VALUES (?, ?, ?)""",
                            (scenario["name"], len(scenario["phases"]),
                             json.dumps(scenario["phases"]))
                        )
            logger.info("Scenario library initialized")
        except Exception as e:
            logger.error(f"Failed to init scenario library: {e}")

    def evaluate_event(self, event_data: dict) -> Optional[dict]:
        """
        Evaluate a live sensor event against scenario phase signatures.
        Returns prediction if early phases match with sufficient confidence.
        """
        self._ensure_scenario_library()
        zone = event_data.get("zone", "")
        speed = event_data.get("movement_speed", 0)
        duration = event_data.get("duration", 0)
        hour = event_data.get("hour", 12)
        trajectory_familiar = event_data.get("trajectory_familiar", True)

        self._event_history.append({
            **event_data,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Trim old events
        if len(self._event_history) > 500:
            self._event_history = self._event_history[-200:]

        best_match = None
        best_confidence = 0.0

        for scenario in SCENARIO_LIBRARY:
            for phase in scenario["phases"]:
                confidence = self._match_phase(phase, event_data)
                if confidence > best_confidence and confidence > 0.4:
                    best_confidence = confidence
                    best_match = {
                        "scenario_name": scenario["name"],
                        "matched_phase": phase["id"],
                        "matched_phase_label": phase["label"],
                        "confidence": round(confidence, 3),
                        "description": phase["description"]
                    }

        if best_match and best_confidence > 0.5:
            # Determine predicted next phase
            prediction = self._build_prediction(best_match)
            return prediction

        return None

    def _match_phase(self, phase: dict, event: dict) -> float:
        """Score how well an event matches a phase signature."""
        signatures = phase["signatures"]
        score = 0.0
        max_factors = 5

        zone = event.get("zone", "")
        speed = event.get("movement_speed", 0)
        duration = event.get("duration", 0)
        trajectory_familiar = event.get("trajectory_familiar", True)

        # Zone match
        zone_types = signatures.get("zone_types", [])
        if "any" in zone_types or zone in zone_types:
            score += 1.0
        elif any(z in zone for z in zone_types):
            score += 0.5

        # Speed match
        speed_range = signatures.get("movement_speed_range", [0, 100])
        if speed_range[0] <= speed <= speed_range[1]:
            score += 1.0
        elif speed < speed_range[0]:
            score += 0.3

        # Duration match
        min_duration = signatures.get("min_duration_seconds", 0)
        if duration >= min_duration:
            score += 1.0
        elif duration >= min_duration * 0.5:
            score += 0.5

        # Unfamiliar trajectory
        if signatures.get("unfamiliar_trajectory") and not trajectory_familiar:
            score += 1.0
        elif not signatures.get("unfamiliar_trajectory"):
            score += 0.5

        # Time pattern
        time_pref = signatures.get("time_pattern", "any")
        hour = event.get("hour", 12)
        if time_pref == "any":
            score += 0.5
        elif time_pref == "nighttime_preferred" and (hour < 6 or hour >= 22):
            score += 1.0
        elif time_pref == "nighttime_preferred":
            score += 0.3

        return score / max_factors

    def _build_prediction(self, match: dict) -> dict:
        """Build a prediction response including next phase forecast."""
        scenario = next(
            (s for s in SCENARIO_LIBRARY if s["name"] == match["scenario_name"]), None
        )
        if not scenario:
            return match

        phases = scenario["phases"]
        current_idx = next(
            (i for i, p in enumerate(phases) if p["id"] == match["matched_phase"]), -1
        )

        predicted_next = None
        if current_idx >= 0 and current_idx < len(phases) - 1:
            next_phase = phases[current_idx + 1]
            predicted_next = {
                "phase_id": next_phase["id"],
                "phase_label": next_phase["label"],
                "description": next_phase["description"]
            }

        # Store prediction in database
        prediction_id = self._save_prediction(match, predicted_next)

        # Build reasoning timeline entry
        self._add_reasoning_entry(prediction_id, match)

        return {
            "prediction_id": prediction_id,
            "scenario_name": match["scenario_name"],
            "matched_phase": match["matched_phase"],
            "matched_phase_label": match["matched_phase_label"],
            "confidence": match["confidence"],
            "predicted_next_phase": predicted_next,
            "reasoning": f"Current activity matches {match['matched_phase_label']} phase "
                        f"({match['confidence']*100:.0f}% confidence). "
                        f"{match['description']}.",
            "timestamp": datetime.utcnow().isoformat()
        }

    def _save_prediction(self, match: dict, predicted_next: dict) -> int:
        """Save prediction to database."""
        try:
            with get_db() as conn:
                scenario = conn.execute(
                    "SELECT id FROM scenario_library WHERE name = ?",
                    (match["scenario_name"],)
                ).fetchone()

                if scenario:
                    cursor = conn.execute(
                        """INSERT INTO prediction_events
                           (matched_scenario_id, matched_phase, confidence, predicted_next_phase)
                           VALUES (?, ?, ?, ?)""",
                        (scenario["id"], match["matched_phase"], match["confidence"],
                         predicted_next["phase_label"] if predicted_next else None)
                    )
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to save prediction: {e}")
        return 0

    def _add_reasoning_entry(self, prediction_id: int, match: dict):
        """Add an entry to the reasoning timeline."""
        if prediction_id not in self._reasoning_timeline:
            self._reasoning_timeline[prediction_id] = []

        self._reasoning_timeline[prediction_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "phase_match",
            "data_point": f"Phase '{match['matched_phase']}' detected",
            "conclusion": f"{match['confidence']*100:.0f}% confidence match",
            "confidence_delta": match["confidence"]
        })

    def get_reasoning_timeline(self, prediction_id: int) -> List[dict]:
        """Get the full reasoning timeline for a prediction."""
        return self._reasoning_timeline.get(prediction_id, [])

    def get_active_predictions(self) -> List[dict]:
        """Get all active (unresolved) predictions."""
        self._ensure_scenario_library()
        with get_db() as conn:
            rows = conn.execute(
                """SELECT pe.*, sl.name as scenario_name
                   FROM prediction_events pe
                   JOIN scenario_library sl ON pe.matched_scenario_id = sl.id
                   WHERE pe.resolved_at IS NULL
                   ORDER BY pe.detected_at DESC"""
            ).fetchall()
        return [dict(row) for row in rows]


# ============================================================
# Demo Simulation Engine
# ============================================================
class DemoSimulator:
    """Injects synthetic sensor events for demo scenario simulation."""

    def __init__(self, prediction_engine: PredictionEngine):
        self.engine = prediction_engine
        self._active_scenario = None
        self._phase_index = 0

    async def start_scenario(self, scenario_name: str) -> dict:
        """Start a demo scenario simulation."""
        scenario = next(
            (s for s in SCENARIO_LIBRARY if s["name"] == scenario_name), None
        )
        if not scenario:
            return {"error": "Scenario not found"}

        self._active_scenario = scenario
        self._phase_index = 0

        return {
            "status": "started",
            "scenario": scenario_name,
            "total_phases": len(scenario["phases"]),
            "message": f"Simulating '{scenario_name}' — {len(scenario['phases'])} phases"
        }

    def get_next_synthetic_event(self) -> Optional[dict]:
        """Generate the next synthetic event for the active scenario."""
        if not self._active_scenario:
            return None

        phases = self._active_scenario["phases"]
        if self._phase_index >= len(phases):
            return None

        phase = phases[self._phase_index]
        sigs = phase["signatures"]

        # Generate synthetic event matching phase signatures
        import random
        zone_types = sigs.get("zone_types", ["living_room"])
        zone = random.choice(zone_types) if "any" not in zone_types else "living_room"
        speed_range = sigs.get("movement_speed_range", [1, 5])
        speed = random.uniform(speed_range[0], speed_range[1])
        duration = sigs.get("min_duration_seconds", 10) * random.uniform(1.0, 2.0)

        event = {
            "type": "synthetic_sensor_event",
            "sensor_id": "demo-sensor-001",
            "zone": zone,
            "movement_speed": round(speed, 2),
            "duration": round(duration, 1),
            "trajectory_familiar": False,
            "hour": 3,  # Night time for demo
            "phase_label": phase["label"],
            "timestamp": datetime.utcnow().isoformat()
        }

        self._phase_index += 1
        return event

    def stop(self):
        """Stop the active simulation."""
        self._active_scenario = None
        self._phase_index = 0


# Singleton instances
prediction_engine = PredictionEngine()
demo_simulator = DemoSimulator(prediction_engine)
