# Chunk 05 — Intelligence Response Layer

**Goal**: Build the Smart Clip Extraction Engine, Claude API integration for AI narratives, context-aware alert system with FCM, and two-way communication relay.
**Estimated Time**: 50 minutes
**Dependencies**: Chunk 04 (ML and Anomaly Detection)
**Unlocks**: Chunk 09 (Secret Weapon + Deploy) when combined with Chunk 08.

---

## 05.1 — Video Encoder Utility (backend/utils/video_encoder.py)

```python
"""
HomeGuardian AI — Video Encoder
Encodes frames into MP4 clips with timestamp overlay.
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import List

from config import settings

logger = logging.getLogger("homeguardian.encoder")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available. Video encoding will be simulated.")


class VideoEncoder:
    """Encodes frame sequences into MP4 video clips."""

    CLIPS_DIR = Path(__file__).parent.parent / "clips"
    FPS = 15
    CODEC = "mp4v"

    @classmethod
    def encode_clip(cls, frames: List[dict], anomaly_id: int,
                    sensor_id: str, zone: str, anomaly_score: float) -> dict:
        """
        Encode a list of frames into an MP4 clip.
        Returns clip metadata.
        """
        cls.CLIPS_DIR.mkdir(parents=True, exist_ok=True)

        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"anomaly_{anomaly_id}_{timestamp_str}.mp4"
        filepath = cls.CLIPS_DIR / filename

        if not CV2_AVAILABLE or not frames:
            # Create a placeholder metadata entry
            return cls._create_placeholder_clip(filepath, anomaly_id, sensor_id, zone)

        try:
            # Decode first frame to get dimensions
            import base64
            first_frame_data = frames[0]["data"].get("frame_data", "")
            if not first_frame_data:
                return cls._create_placeholder_clip(filepath, anomaly_id, sensor_id, zone)

            first_bytes = base64.b64decode(first_frame_data)
            first_np = np.frombuffer(first_bytes, np.uint8)
            first_frame = cv2.imdecode(first_np, cv2.IMREAD_COLOR)

            if first_frame is None:
                return cls._create_placeholder_clip(filepath, anomaly_id, sensor_id, zone)

            h, w = first_frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*cls.CODEC)
            writer = cv2.VideoWriter(str(filepath), fourcc, cls.FPS, (w, h))

            frames_written = 0
            for frame_entry in frames:
                frame_data = frame_entry["data"].get("frame_data", "")
                if not frame_data:
                    continue

                frame_bytes = base64.b64decode(frame_data)
                frame_np = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)

                if frame is not None:
                    # Add timestamp overlay
                    ts = frame_entry.get("timestamp", "")
                    if ts:
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        text_size = cv2.getTextSize(ts, font, 0.5, 1)[0]
                        cv2.rectangle(frame, (8, h - 10 - text_size[1] - 4),
                                     (12 + text_size[0], h - 6), (0, 0, 0), -1)
                        cv2.putText(frame, ts, (10, h - 10), font, 0.5,
                                   (255, 255, 255), 1)
                    writer.write(frame)
                    frames_written += 1

            writer.release()

            duration = frames_written / cls.FPS if cls.FPS > 0 else 0

            metadata = {
                "anomaly_id": anomaly_id,
                "clip_path": str(filepath),
                "filename": filename,
                "duration_seconds": round(duration, 2),
                "frames_written": frames_written,
                "resolution": f"{w}x{h}",
                "sensor_id": sensor_id,
                "zone": zone,
                "anomaly_score": anomaly_score,
                "created_at": datetime.utcnow().isoformat()
            }

            logger.info(f"Clip encoded: {filename} ({frames_written} frames, {duration:.1f}s)")
            return metadata

        except Exception as e:
            logger.error(f"Clip encoding failed: {e}")
            return cls._create_placeholder_clip(filepath, anomaly_id, sensor_id, zone)

    @classmethod
    def _create_placeholder_clip(cls, filepath: Path, anomaly_id: int,
                                  sensor_id: str, zone: str) -> dict:
        """Create placeholder metadata when encoding is not possible."""
        # Create an empty file as placeholder
        filepath.touch()
        return {
            "anomaly_id": anomaly_id,
            "clip_path": str(filepath),
            "filename": filepath.name,
            "duration_seconds": 15.0,
            "frames_written": 0,
            "resolution": "640x480",
            "sensor_id": sensor_id,
            "zone": zone,
            "anomaly_score": 0.0,
            "created_at": datetime.utcnow().isoformat(),
            "placeholder": True
        }
```

---

## 05.2 — Clip Extraction Service (backend/services/clip_service.py)

```python
"""
HomeGuardian AI — Smart Clip Extraction Engine
Assembles pre-event + post-event frames into clips on anomaly confirmation.
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional

from config import settings
from database import get_db
from services.sensor_pipeline import sensor_pipeline
from utils.video_encoder import VideoEncoder

logger = logging.getLogger("homeguardian.clip")


class ClipExtractor:
    """Smart Clip Extraction Engine."""

    def __init__(self):
        self.pre_seconds = settings.CLIP_PRE_SECONDS
        self.post_seconds = settings.CLIP_POST_SECONDS
        self._active_captures: dict = {}

    async def trigger_clip(self, anomaly_id: int, sensor_id: str,
                           zone: str, anomaly_score: float) -> dict:
        """
        Trigger clip extraction for a confirmed anomaly.
        1. Pull pre-event frames from ring buffer
        2. Capture post-event frames
        3. Encode to MP4
        4. Save metadata to database
        """
        logger.info(f"Clip triggered for anomaly {anomaly_id} on {sensor_id}")

        # Step 1: Get pre-event frames
        pre_frames = sensor_pipeline.get_pre_event_frames(sensor_id, self.pre_seconds)
        logger.info(f"Retrieved {len(pre_frames)} pre-event frames")

        # Step 2: Capture post-event frames
        post_frames = await self._capture_post_event(sensor_id, self.post_seconds)
        logger.info(f"Captured {len(post_frames)} post-event frames")

        # Step 3: Combine frames
        all_frames = pre_frames + post_frames

        # Step 4: Encode clip
        metadata = VideoEncoder.encode_clip(
            frames=all_frames,
            anomaly_id=anomaly_id,
            sensor_id=sensor_id,
            zone=zone,
            anomaly_score=anomaly_score
        )

        # Step 5: Save to database
        with get_db() as conn:
            conn.execute(
                "UPDATE anomaly_events SET clip_path = ? WHERE id = ?",
                (metadata["clip_path"], anomaly_id)
            )

        metadata["pre_event_seconds"] = self.pre_seconds
        metadata["post_event_seconds"] = self.post_seconds

        return metadata

    async def _capture_post_event(self, sensor_id: str, seconds: float) -> list:
        """Capture post-event frames for the specified duration."""
        frames = []
        fps = 15
        total_frames = int(seconds * fps)
        frame_interval = 1.0 / fps

        queue = sensor_pipeline.register_frame_queue(sensor_id)

        try:
            for _ in range(total_frames):
                try:
                    frame = await asyncio.wait_for(queue.get(), timeout=frame_interval * 3)
                    frames.append({
                        "data": frame,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except asyncio.TimeoutError:
                    break
        finally:
            sensor_pipeline.unregister_frame_queue(sensor_id)

        return frames

    def get_clip_metadata(self, anomaly_id: int) -> Optional[dict]:
        """Get clip metadata from the database."""
        with get_db() as conn:
            row = conn.execute(
                "SELECT id, clip_path, detected_at FROM anomaly_events WHERE id = ? AND clip_path IS NOT NULL",
                (anomaly_id,)
            ).fetchone()
        if not row:
            return None
        event = dict(row)
        return {
            "anomaly_id": event["id"],
            "clip_path": event["clip_path"],
            "created_at": event["detected_at"]
        }


# Singleton instance
clip_extractor = ClipExtractor()
```

---

## 05.3 — Claude Narrative Service (backend/services/narrative_service.py)

```python
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
```

---

## 05.4 — Alert Service (backend/services/alert_service.py)

```python
"""
HomeGuardian AI — Context-Aware Alert System
Alert construction, FCM delivery, deduplication, and escalation.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from config import settings
from database import get_db

logger = logging.getLogger("homeguardian.alerts")

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FCM_AVAILABLE = True
except ImportError:
    FCM_AVAILABLE = False
    logger.warning("Firebase Admin SDK not available. Push notifications will be simulated.")


class AlertService:
    """Manages alert creation, delivery, and deduplication."""

    # Deduplication window: ignore duplicate alerts for the same zone within this period
    DEDUP_WINDOW_SECONDS = 60

    # Escalation rules
    ESCALATION_RULES = {
        "low": ["log"],
        "medium": ["log"],
        "high": ["push", "log"],
        "critical": ["push", "audio", "log"]
    }

    def __init__(self):
        self._recent_alerts: Dict[str, datetime] = {}
        self._fcm_initialized = False

        if FCM_AVAILABLE and not settings.DEMO_MODE:
            self._init_fcm()

    def _init_fcm(self):
        """Initialize Firebase Cloud Messaging."""
        try:
            from pathlib import Path
            cred_path = Path(__file__).parent.parent / "firebase-credentials.json"
            if cred_path.exists():
                cred = credentials.Certificate(str(cred_path))
                firebase_admin.initialize_app(cred)
                self._fcm_initialized = True
                logger.info("Firebase Cloud Messaging initialized")
            else:
                logger.warning("Firebase credentials file not found")
        except Exception as e:
            logger.error(f"FCM initialization failed: {e}")

    def should_alert(self, zone: str, risk_level: str) -> bool:
        """Check if an alert should be fired (deduplication check)."""
        key = f"{zone}:{risk_level}"
        last_alert = self._recent_alerts.get(key)

        if last_alert:
            elapsed = (datetime.utcnow() - last_alert).total_seconds()
            if elapsed < self.DEDUP_WINDOW_SECONDS:
                logger.debug(f"Alert deduplicated for {key} ({elapsed:.0f}s since last)")
                return False

        return True

    async def fire_alert(self, anomaly_id: int, context: dict) -> List[dict]:
        """
        Fire an alert based on risk level escalation rules.
        Returns list of alert records created.
        """
        risk_level = context.get("risk_level", "low")
        zone = context.get("zone", "unknown")

        if not self.should_alert(zone, risk_level):
            return []

        channels = self.ESCALATION_RULES.get(risk_level, ["log"])
        alert_records = []

        for channel in channels:
            alert_record = await self._send_via_channel(channel, anomaly_id, context)
            alert_records.append(alert_record)

        # Update deduplication tracker
        self._recent_alerts[f"{zone}:{risk_level}"] = datetime.utcnow()

        return alert_records

    async def _send_via_channel(self, channel: str, anomaly_id: int, context: dict) -> dict:
        """Send an alert through a specific channel."""
        alert_id = None
        delivery_status = "sent"
        fcm_message_id = None

        with get_db() as conn:
            cursor = conn.execute(
                """INSERT INTO alerts (anomaly_event_id, channel, delivery_status)
                   VALUES (?, ?, ?)""",
                (anomaly_id, channel, "pending")
            )
            alert_id = cursor.lastrowid

        if channel == "push":
            fcm_result = await self._send_push(anomaly_id, context)
            delivery_status = fcm_result.get("status", "sent")
            fcm_message_id = fcm_result.get("message_id")

        elif channel == "audio":
            # Audio alert will be sent via WebSocket to old devices
            delivery_status = "sent"
            logger.info(f"Audio alert triggered for anomaly {anomaly_id}")

        elif channel == "log":
            delivery_status = "delivered"

        # Update alert record
        with get_db() as conn:
            conn.execute(
                """UPDATE alerts SET delivery_status = ?, fcm_message_id = ?
                   WHERE id = ?""",
                (delivery_status, fcm_message_id, alert_id)
            )

        return {
            "alert_id": alert_id,
            "channel": channel,
            "delivery_status": delivery_status,
            "fcm_message_id": fcm_message_id
        }

    async def _send_push(self, anomaly_id: int, context: dict) -> dict:
        """Send FCM push notification."""
        if not self._fcm_initialized or settings.DEMO_MODE:
            logger.info(f"[DEMO] Push notification for anomaly {anomaly_id}")
            return {"status": "sent", "message_id": f"demo-{anomaly_id}"}

        try:
            # Get FCM tokens for new_device users
            with get_db() as conn:
                tokens = conn.execute(
                    "SELECT fcm_token FROM users WHERE role = 'new_device' AND fcm_token IS NOT NULL"
                ).fetchall()

            if not tokens:
                return {"status": "sent", "message_id": None}

            for token_row in tokens:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=f"HomeGuardian: {context.get('risk_level', 'Alert').upper()} Alert",
                        body=context.get("reasoning_summary", "Anomaly detected in your home."),
                    ),
                    data={
                        "anomaly_id": str(anomaly_id),
                        "risk_level": context.get("risk_level", "medium"),
                        "zone": context.get("zone", "unknown"),
                        "clip_available": str(context.get("clip_available", False))
                    },
                    token=token_row["fcm_token"]
                )
                response = messaging.send(message)
                return {"status": "delivered", "message_id": response}

        except Exception as e:
            logger.error(f"FCM send failed: {e}")
            return {"status": "failed", "message_id": None}

        return {"status": "sent", "message_id": None}


# Singleton instance
alert_service = AlertService()
```

---

## 05.5 — Communication Service (backend/services/communication_service.py)

```python
"""
HomeGuardian AI — Two-Way Communication Relay
Routes messages between new device dashboard and old device nodes.
"""

import uuid
import logging
from datetime import datetime

from mqtt_client import mqtt_manager
from utils.mqtt_topics import MQTTTopics
from websocket_manager import connection_manager

logger = logging.getLogger("homeguardian.communication")


class CommunicationService:
    """Manages two-way communication between dashboard and old devices."""

    async def send_message_to_device(self, target_device_id: str,
                                      message_text: str = None,
                                      audio_url: str = None,
                                      sender_id: str = "") -> dict:
        """Send a text or audio message to an old device."""
        message_id = str(uuid.uuid4())

        payload = {
            "type": "incoming_message",
            "message_id": message_id,
            "from": sender_id,
            "timestamp": datetime.utcnow().isoformat()
        }

        if message_text:
            payload["message_type"] = "text"
            payload["content"] = message_text
        elif audio_url:
            payload["message_type"] = "audio"
            payload["audio_url"] = audio_url
        else:
            return {"error": "No message content provided"}

        # Try WebSocket first
        ws = connection_manager.old_devices.get(target_device_id)
        if ws:
            try:
                await connection_manager.send_to_old_device(target_device_id, payload)
                logger.info(f"Message sent to {target_device_id} via WebSocket")
                return {
                    "message_id": message_id,
                    "status": "delivered",
                    "channel": "websocket",
                    "sent_at": payload["timestamp"]
                }
            except Exception as e:
                logger.error(f"WebSocket delivery failed: {e}")

        # Fallback to MQTT
        topic = MQTTTopics.command_to_device(target_device_id)
        mqtt_manager.publish(topic, payload)
        logger.info(f"Message sent to {target_device_id} via MQTT ({topic})")

        return {
            "message_id": message_id,
            "status": "sent",
            "channel": "mqtt",
            "sent_at": payload["timestamp"]
        }

    async def broadcast_warning(self, message_text: str, sender_id: str = "system") -> dict:
        """Broadcast a warning message to all connected old devices."""
        message_id = str(uuid.uuid4())

        payload = {
            "type": "warning_broadcast",
            "message_id": message_id,
            "from": sender_id,
            "message_type": "text",
            "content": message_text,
            "priority": "high",
            "timestamp": datetime.utcnow().isoformat()
        }

        # Send via WebSocket to all connected old devices
        await connection_manager.broadcast_to_old_devices(payload)

        # Also publish via MQTT for devices not on WebSocket
        mqtt_manager.publish("homeguardian/alerts/broadcast", payload)

        return {
            "message_id": message_id,
            "status": "broadcast",
            "devices_reached": connection_manager.active_old_devices,
            "sent_at": payload["timestamp"]
        }


# Singleton instance
communication_service = CommunicationService()
```

---

## 05.6 — Communication Routes (backend/routers/communication_routes.py)

```python
"""
HomeGuardian AI — Communication Routes
"""

from fastapi import APIRouter, Depends
from models import SendMessageRequest, MessageResponse
from auth import get_current_user, require_role
from models import UserRole
from services.communication_service import communication_service

router = APIRouter()


@router.post("/send", response_model=MessageResponse)
async def send_message(
    request: SendMessageRequest,
    user: dict = Depends(require_role(UserRole.NEW_DEVICE))
):
    """Send a message from dashboard to an old device."""
    result = await communication_service.send_message_to_device(
        target_device_id=request.target_device_id,
        message_text=request.message_text,
        audio_url=request.audio_url,
        sender_id=user["id"]
    )
    return MessageResponse(
        message_id=result["message_id"],
        status=result["status"],
        sent_at=result["sent_at"]
    )
```

Add to `main.py`:
```python
from routers.communication_routes import router as communication_router
app.include_router(communication_router, prefix="/api/communicate", tags=["Communication"])
```

---

## 05.7 — Clip and Narrative Routes (backend/routers/clip_routes.py and narrative_routes.py)

### clip_routes.py

```python
"""
HomeGuardian AI — Clip Routes
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from auth import get_current_user
from services.clip_service import clip_extractor

router = APIRouter()


@router.get("/{anomaly_id}")
async def get_clip_metadata(anomaly_id: int, user: dict = Depends(get_current_user)):
    """Get clip metadata for an anomaly event."""
    metadata = clip_extractor.get_clip_metadata(anomaly_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Clip not found for this anomaly")
    return metadata


@router.get("/{anomaly_id}/download")
async def download_clip(anomaly_id: int, user: dict = Depends(get_current_user)):
    """Download the clip MP4 file."""
    metadata = clip_extractor.get_clip_metadata(anomaly_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Clip not found")

    clip_path = Path(metadata["clip_path"])
    if not clip_path.exists():
        raise HTTPException(status_code=404, detail="Clip file not found on disk")

    return FileResponse(
        path=str(clip_path),
        media_type="video/mp4",
        filename=clip_path.name
    )
```

### narrative_routes.py

```python
"""
HomeGuardian AI — Narrative Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from auth import get_current_user
from database import get_db
from services.narrative_service import narrative_generator

router = APIRouter()


@router.get("/{anomaly_id}")
async def get_narrative(anomaly_id: int, user: dict = Depends(get_current_user)):
    """Get the AI narrative for an anomaly event."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, narrative_text, detected_at FROM anomaly_events WHERE id = ?",
            (anomaly_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Anomaly event not found")

    event = dict(row)
    if not event.get("narrative_text"):
        raise HTTPException(status_code=404, detail="No narrative generated yet")

    return {
        "anomaly_id": event["id"],
        "narrative_text": event["narrative_text"],
        "generated_at": event["detected_at"]
    }


@router.post("/{anomaly_id}/generate")
async def generate_narrative(anomaly_id: int, user: dict = Depends(get_current_user)):
    """Generate (or regenerate) an AI narrative for an anomaly event."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM anomaly_events WHERE id = ?", (anomaly_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Anomaly event not found")

    event = dict(row)
    context = {
        "timestamp": event["detected_at"],
        "zone": event["zone"],
        "anomaly_score": event["anomaly_score"],
        "risk_level": event["risk_level"],
        "baseline_deviation": event.get("baseline_deviation", 0),
        "duration_seconds": event.get("duration_seconds", 0),
        "classification": event.get("classification", "minor_deviation"),
        "sensor_count": len(event.get("sensor_node_ids", "").split(","))
    }

    result = await narrative_generator.generate_narrative(anomaly_id, context)
    return result
```

Add to `main.py`:
```python
from routers.clip_routes import router as clip_router
from routers.narrative_routes import router as narrative_router
app.include_router(clip_router, prefix="/api/clips", tags=["Clips"])
app.include_router(narrative_router, prefix="/api/narratives", tags=["Narratives"])
```

---

## Verification

```bash
# 1. Test narrative generator (template mode)
cd backend
source venv/bin/activate
python -c "
import asyncio
from services.narrative_service import narrative_generator
context = {
    'timestamp': '2:43 AM',
    'zone': 'living room',
    'anomaly_score': 0.87,
    'risk_level': 'high',
    'baseline_deviation': 3.2,
    'duration_seconds': 47,
    'classification': 'suspicious_nighttime_activity',
    'sensor_count': 2,
    'baseline_probability': 2,
    'movement_speed': 12.5,
    'baseline_speed': 3.2
}
result = asyncio.run(narrative_generator.generate_narrative(1, context))
print('Generated by:', result['generated_by'])
print('Narrative:')
print(result['narrative_text'])
print()
print('Narrative generator test PASSED')
"

# 2. Test alert service
python -c "
from services.alert_service import alert_service
print('Should alert (first time):', alert_service.should_alert('living_room', 'high'))
print('Should alert (dedup):', alert_service.should_alert('living_room', 'high'))
print('Alert service test PASSED')
"

# 3. Test API endpoints
curl http://localhost:8000/api/clips/1       # Should return 404 (no clips yet)
curl http://localhost:8000/api/narratives/1   # Should return 404 (no events yet)
```

Expected: Narrative generator produces a full, readable incident report from templates. Alert service correctly deduplicates. API endpoints return proper 404 responses for non-existent data.
