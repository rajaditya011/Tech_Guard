"""
HomeGuardian AI — Demo Mode Routes
"""

from fastapi import APIRouter, HTTPException
from models import DemoScenarioResponse, DemoStartResponse
from config import settings

router = APIRouter()

DEMO_SCENARIOS = [
    {"id": 1, "name": "Normal Morning Routine", "phase_count": 1,
     "description": "14-day baseline established. Owner leaves at 8 AM. Normal kitchen and living room activity. No alerts."},
    {"id": 2, "name": "Late Night Anomaly", "phase_count": 3,
     "description": "2:43 AM motion in living room. No baseline match. Risk escalates from Medium to High. Clip generated. Narrative written."},
    {"id": 3, "name": "Casing Simulation", "phase_count": 2,
     "description": "Afternoon perimeter sensor detects slow repeated passes. Watch flag raised. Escalates to Suspicious. 73% casing match."},
    {"id": 4, "name": "Full Intrusion Prediction", "phase_count": 4,
     "description": "Complete 4-phase simulation. Casing, Entry Probing detected. Critical alert during Entry Probing before Intrusion phase."},
]


@router.get("/scenarios", response_model=list)
async def list_scenarios():
    """List all available demo scenarios."""
    return DEMO_SCENARIOS


@router.post("/start/{scenario_id}", response_model=DemoStartResponse)
async def start_scenario(scenario_id: int):
    """Start a demo scenario simulation."""
    scenario = next((s for s in DEMO_SCENARIOS if s["id"] == scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return DemoStartResponse(
        status="started", scenario=scenario["name"],
        message=f"Demo scenario '{scenario['name']}' started. Events will be injected via WebSocket."
    )


@router.post("/stop")
async def stop_scenario():
    """Stop the active demo simulation."""
    return {"status": "stopped", "message": "Demo simulation stopped."}


@router.post("/clear")
async def clear_demo_data():
    """Clear all demo telemetry data."""
    from database import get_db
    with get_db() as conn:
        conn.execute("DELETE FROM anomaly_events")
        conn.execute("DELETE FROM prediction_events")
        conn.execute("DELETE FROM alerts")
    return {"status": "cleared", "message": "Demo data successfully wiped."}
