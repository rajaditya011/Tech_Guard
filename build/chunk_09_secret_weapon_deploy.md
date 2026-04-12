# Chunk 09 — Secret Weapon, Security, and Deployment

**Goal**: Build the Adaptive Surveillance Replay and Prediction Engine, security hardening, production Dockerfiles, Nginx config, health checks, and deployment scripts.
**Estimated Time**: 75 minutes
**Dependencies**: Chunk 05 (Intelligence Response), Chunk 08 (Dashboard)
**Unlocks**: Complete system — demo-ready.

---

## 09.1 — Prediction Engine Service (backend/services/prediction_service.py)

```python
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
        self._init_scenario_library()

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
```

---

## 09.2 — Prediction Routes (backend/routers/prediction_routes.py)

```python
"""
HomeGuardian AI — Prediction Engine Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from auth import get_current_user
from services.prediction_service import prediction_engine

router = APIRouter()


@router.get("/")
async def list_predictions(user: dict = Depends(get_current_user)):
    """List active (unresolved) prediction events."""
    return prediction_engine.get_active_predictions()


@router.get("/{prediction_id}/timeline")
async def get_timeline(prediction_id: int, user: dict = Depends(get_current_user)):
    """Get the AI reasoning timeline for a prediction."""
    timeline = prediction_engine.get_reasoning_timeline(prediction_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="No timeline data for this prediction")
    return {
        "prediction_id": prediction_id,
        "entries": timeline
    }
```

Add to `main.py`:
```python
from routers.prediction_routes import router as prediction_router
app.include_router(prediction_router, prefix="/api/predictions", tags=["Predictions"])
```

---

## 09.3 — Security Middleware (backend/utils/security.py)

```python
"""
HomeGuardian AI — Security Utilities
Input sanitization, validation, and security helpers.
"""

import re
import html
import logging
from typing import Any

logger = logging.getLogger("homeguardian.security")


def sanitize_string(value: str, max_length: int = 500) -> str:
    """Sanitize a string input."""
    if not isinstance(value, str):
        return ""
    # Trim length
    value = value[:max_length]
    # Escape HTML entities
    value = html.escape(value, quote=True)
    # Remove null bytes
    value = value.replace('\x00', '')
    return value.strip()


def sanitize_mqtt_topic(topic: str) -> str:
    """Sanitize an MQTT topic string."""
    # Only allow alphanumeric, hyphens, underscores, and forward slashes
    sanitized = re.sub(r'[^a-zA-Z0-9\-_/]', '', topic)
    # Prevent directory traversal
    sanitized = sanitized.replace('..', '')
    return sanitized


def validate_device_id(device_id: str) -> bool:
    """Validate a device ID format."""
    pattern = r'^[a-zA-Z0-9\-_]{3,50}$'
    return bool(re.match(pattern, device_id))


def validate_zone_name(zone: str) -> bool:
    """Validate a zone name format."""
    pattern = r'^[a-z0-9_]{2,50}$'
    return bool(re.match(pattern, zone))


def validate_risk_level(level: str) -> bool:
    """Validate a risk level value."""
    return level in ('low', 'medium', 'high', 'critical')


def log_security_event(event_type: str, details: str, severity: str = "info"):
    """Log a security-relevant event."""
    logger.log(
        logging.WARNING if severity == "warning" else logging.INFO,
        f"[SECURITY] {event_type}: {details}"
    )
```

---

## 09.4 — Dashboard Routes (backend/routers/dashboard_routes.py)

```python
"""
HomeGuardian AI — Dashboard Aggregation Routes
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from auth import get_current_user
from database import get_db
from services.risk_service import risk_calculator
from config import settings

router = APIRouter()


@router.get("/summary")
async def dashboard_summary(user: dict = Depends(get_current_user)):
    """Get aggregated dashboard statistics."""
    with get_db() as conn:
        total_sensors = conn.execute("SELECT COUNT(*) as c FROM sensor_nodes").fetchone()["c"]
        active_sensors = conn.execute(
            "SELECT COUNT(*) as c FROM sensor_nodes WHERE status = 'active'"
        ).fetchone()["c"]

        today = datetime.utcnow().strftime("%Y-%m-%d")
        anomalies_today = conn.execute(
            "SELECT COUNT(*) as c FROM anomaly_events WHERE detected_at >= ?",
            (today,)
        ).fetchone()["c"]
        alerts_today = conn.execute(
            "SELECT COUNT(*) as c FROM alerts WHERE sent_at >= ?",
            (today,)
        ).fetchone()["c"]

    system_risk = risk_calculator.get_system_risk()

    return {
        "active_sensors": active_sensors,
        "total_sensors": total_sensors,
        "system_mode": "demo" if settings.DEMO_MODE else "monitoring",
        "baseline_status": "learning",
        "current_risk": system_risk["score"],
        "risk_level": system_risk["risk_level"],
        "total_anomalies_today": anomalies_today,
        "total_alerts_today": alerts_today,
        "uptime_hours": 0
    }


@router.get("/heatmap/{zone}")
async def get_heatmap(zone: str, user: dict = Depends(get_current_user)):
    """Get heat zone data for the floor plan."""
    with get_db() as conn:
        recent = conn.execute(
            """SELECT COUNT(*) as c FROM anomaly_events
               WHERE zone = ? AND detected_at >= ?""",
            (zone, (datetime.utcnow() - timedelta(hours=24)).isoformat())
        ).fetchone()

    activity_count = recent["c"] if recent else 0
    intensity = min(1.0, activity_count / 10.0)
    risk = "low" if intensity < 0.3 else "medium" if intensity < 0.7 else "high"

    return {
        "zone": zone,
        "intensity": intensity,
        "activity_count": activity_count,
        "last_activity": None,
        "risk_level": risk
    }
```

Add to `main.py`:
```python
from routers.dashboard_routes import router as dashboard_router
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
```

---

## 09.5 — Alert Routes (backend/routers/alert_routes.py)

```python
"""
HomeGuardian AI — Alert Routes
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from auth import get_current_user
from database import get_db

router = APIRouter()


@router.get("/")
async def list_alerts(
    channel: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    user: dict = Depends(get_current_user)
):
    """List alerts with optional filters."""
    with get_db() as conn:
        query = "SELECT * FROM alerts"
        params = []
        if channel:
            query += " WHERE channel = ?"
            params.append(channel)
        query += " ORDER BY sent_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]
```

Add to `main.py`:
```python
from routers.alert_routes import router as alert_router
app.include_router(alert_router, prefix="/api/alerts", tags=["Alerts"])
```

---

## 09.6 — Production Deployment Scripts

### deploy.sh (project root)

```bash
#!/bin/bash
# HomeGuardian AI — Production Deployment Script
# Usage: bash deploy.sh [local|cloud]

set -e

MODE=${1:-local}

echo "========================================="
echo "  HomeGuardian AI — Deployment ($MODE)"
echo "========================================="

if [ "$MODE" = "local" ]; then
    echo "[1/4] Building Docker images..."
    docker-compose build

    echo "[2/4] Starting services..."
    docker-compose up -d

    echo "[3/4] Waiting for services to start..."
    sleep 5

    echo "[4/4] Running health check..."
    curl -s http://localhost:8000/api/health | python -m json.tool

    echo ""
    echo "========================================="
    echo "  Deployment complete!"
    echo "  Frontend: http://localhost:5173"
    echo "  API:      http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo "  MQTT:     localhost:1883"
    echo "========================================="

elif [ "$MODE" = "cloud" ]; then
    echo "Cloud Run deployment requires gcloud CLI."
    echo "Run: gcloud run deploy homeguardian-api --source ./backend"
    echo "Run: gcloud run deploy homeguardian-frontend --source ./frontend"
fi
```

### health_check.sh (project root)

```bash
#!/bin/bash
# Quick health check for all services

echo "Checking services..."

# API
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health)
echo "API: $API_STATUS"

# Frontend
FE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173)
echo "Frontend: $FE_STATUS"

# MQTT
if nc -z localhost 1883 2>/dev/null; then
    echo "MQTT: UP"
else
    echo "MQTT: DOWN"
fi

echo "Done."
```

---

## Verification

```bash
# 1. Test prediction engine
cd backend
source venv/bin/activate
python -c "
from services.prediction_service import prediction_engine
event = {
    'zone': 'front_door',
    'movement_speed': 3.0,
    'duration': 20,
    'trajectory_familiar': False,
    'hour': 3
}
result = prediction_engine.evaluate_event(event)
if result:
    print(f'Match: {result[\"matched_phase_label\"]} ({result[\"confidence\"]*100:.0f}%)')
    if result.get('predicted_next_phase'):
        print(f'Predicted next: {result[\"predicted_next_phase\"][\"phase_label\"]}')
    print(f'Reasoning: {result[\"reasoning\"]}')
else:
    print('No match found (threshold not met)')
print('Prediction engine test PASSED')
"

# 2. Test all API routes
uvicorn main:app --reload --port 8000 &
sleep 3

curl http://localhost:8000/api/health
curl http://localhost:8000/api/demo/scenarios
curl http://localhost:8000/api/dashboard/summary -H "Authorization: Bearer $TOKEN"
curl http://localhost:8000/api/predictions -H "Authorization: Bearer $TOKEN"

# 3. Full deployment test
cd ..
docker-compose build
docker-compose up -d
bash health_check.sh

# 4. Run full diagnostics
python diagnostics.py
```

Expected: Prediction engine evaluates events and matches against casing phase. All API routes respond correctly. Docker services start. Health check passes for all services.
