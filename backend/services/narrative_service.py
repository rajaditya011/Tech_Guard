"""
HomeGuardian AI — AI Incident Narrative Generator
Powered by Claude API with pre-written fallback templates.
"""

import logging
from datetime import datetime
from typing import Optional

from config import settings
from database import get_db

logger = logging.getLogger("homeguardian.narrative")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic SDK not available. Narratives will use template fallback.")


# Pre-written fallback narratives for demo mode
FALLBACK_NARRATIVES = {
    "suspicious_nighttime_activity": (
        "At {time}, unusual movement was detected in the {zone}. This zone typically shows "
        "zero activity between midnight and 6 AM based on {baseline_days} days of baseline data. "
        "The detected movement trajectory does not match any household member's known pattern. "
        "The event persisted for {duration} seconds across {sensor_count} sensor node(s), "
        "{confirmation_note}. Risk assessment: {risk_level}. "
        "Recommended action: verify household members are safe and check the attached clip."
    ),
    "unfamiliar_movement_pattern": (
        "At {time}, a movement pattern was detected in the {zone} that does not match "
        "the established behavioral baseline. The baseline for this zone at this hour indicates "
        "typical activity probability of {baseline_probability}%. The detected activity deviates "
        "from known trajectories by a factor of {deviation_factor}. "
        "Risk assessment: {risk_level}. Recommended action: review the attached clip."
    ),
    "rapid_movement_anomaly": (
        "At {time}, rapid movement was detected in the {zone}. The movement speed of "
        "{movement_speed} pixels per frame significantly exceeds the baseline average of "
        "{baseline_speed} for this zone. The trajectory suggests {trajectory_description}. "
        "Risk assessment: {risk_level}. Recommended action: check the attached clip immediately."
    ),
    "critical_deviation": (
        "CRITICAL ALERT at {time}: Extreme behavioral deviation detected in the {zone}. "
        "Multiple factors indicate a high-confidence anomaly: {factor_summary}. "
        "This event has been confirmed across {sensor_count} sensor(s). "
        "Risk score: {risk_score}/100. Risk assessment: CRITICAL. "
        "Recommended actions: 1) Verify household member safety immediately, "
        "2) Review the attached video clip, 3) Consider contacting local authorities."
    ),
    "significant_behavioral_deviation": (
        "At {time}, significant behavioral deviation was detected in the {zone}. "
        "The current activity pattern diverges from the learned baseline by {deviation_pct}%. "
        "Contributing factors: {factor_summary}. "
        "Risk assessment: {risk_level}. Recommended action: review attached clip and monitor."
    ),
    "minor_deviation": (
        "At {time}, a minor deviation from normal patterns was detected in the {zone}. "
        "While the activity falls outside the typical baseline, the confidence level is moderate. "
        "Risk assessment: {risk_level}. This event has been logged for pattern analysis."
    )
}


class NarrativeGenerator:
    """Generates AI incident narratives using Claude API or fallback templates."""

    def __init__(self):
        self.client = None
        if ANTHROPIC_AVAILABLE and settings.CLAUDE_API_KEY and not settings.DEMO_MODE:
            try:
                self.client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)
                logger.info("Claude API client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")

    async def generate_narrative(self, anomaly_id: int, context: dict) -> dict:
        """
        Generate an incident narrative for an anomaly.
        Uses Claude API if available, falls back to templates.
        """
        if self.client and not settings.DEMO_MODE:
            try:
                return await self._generate_with_claude(anomaly_id, context)
            except Exception as e:
                logger.error(f"Claude generation failed, falling back to template: {e}")

        return self._generate_from_template(anomaly_id, context)

    async def _generate_with_claude(self, anomaly_id: int, context: dict) -> dict:
        """Generate narrative using Claude API."""
        prompt = self._build_claude_prompt(context)

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        narrative_text = message.content[0].text

        # Save to database
        with get_db() as conn:
            conn.execute(
                "UPDATE anomaly_events SET narrative_text = ? WHERE id = ?",
                (narrative_text, anomaly_id)
            )

        return {
            "anomaly_id": anomaly_id,
            "narrative_text": narrative_text,
            "generated_by": "claude",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_from_template(self, anomaly_id: int, context: dict) -> dict:
        """Generate narrative from pre-written templates."""
        classification = context.get("classification", "minor_deviation")
        template = FALLBACK_NARRATIVES.get(classification, FALLBACK_NARRATIVES["minor_deviation"])

        # Build template variables
        sensor_count = context.get("sensor_count", 1)
        confirmation_note = (
            "confirming it is not a false positive" if sensor_count > 1
            else "single sensor detection"
        )

        narrative_text = template.format(
            time=context.get("timestamp", datetime.utcnow().strftime("%I:%M %p")),
            zone=context.get("zone", "unknown area"),
            baseline_days=settings.BASELINE_DAYS,
            duration=context.get("duration_seconds", 0),
            sensor_count=sensor_count,
            confirmation_note=confirmation_note,
            risk_level=context.get("risk_level", "Medium").upper(),
            risk_score=context.get("risk_score", 50),
            baseline_probability=context.get("baseline_probability", 0),
            deviation_factor=context.get("baseline_deviation", 0),
            deviation_pct=round(context.get("baseline_deviation", 0) * 100, 1),
            movement_speed=context.get("movement_speed", 0),
            baseline_speed=context.get("baseline_speed", 0),
            trajectory_description=context.get("trajectory_desc", "non-standard movement"),
            factor_summary=context.get("factor_summary", "multiple behavioral deviations detected")
        )

        # Save to database
        with get_db() as conn:
            conn.execute(
                "UPDATE anomaly_events SET narrative_text = ? WHERE id = ?",
                (narrative_text, anomaly_id)
            )

        return {
            "anomaly_id": anomaly_id,
            "narrative_text": narrative_text,
            "generated_by": "template",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _build_claude_prompt(self, context: dict) -> str:
        """Build the prompt for Claude API."""
        return f"""You are a professional home security AI analyst. Generate a concise, 
plain-English incident narrative based on the following sensor data. Write it as a security 
officer would — factual, clear, actionable. Do not use jargon. Include specific data points.

Event Data:
- Timestamp: {context.get('timestamp', 'Unknown')}
- Zone: {context.get('zone', 'Unknown')}
- Anomaly Score: {context.get('anomaly_score', 0):.2f}
- Risk Level: {context.get('risk_level', 'Unknown')}
- Baseline Deviation: {context.get('baseline_deviation', 0):.2f}
- Duration: {context.get('duration_seconds', 0)} seconds
- Sensors Reporting: {context.get('sensor_count', 1)}
- Movement Speed: {context.get('movement_speed', 0):.1f}
- Classification: {context.get('classification', 'Unknown')}
- Baseline Days: {settings.BASELINE_DAYS}

Write a 3-5 sentence incident narrative. End with a risk assessment and recommended action.
Do not use bullet points — write in paragraph form."""


# Singleton instance
narrative_generator = NarrativeGenerator()
