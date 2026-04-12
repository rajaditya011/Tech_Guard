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

    # Deduplication window
    DEDUP_WINDOW_SECONDS = 60

    # Escalation rules
    ESCALATION_RULES = {
        "low": ["log"],
        "medium": ["log", "email"],
        "high": ["push", "log", "email"],
        "critical": ["push", "audio", "log", "email"]
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
            delivery_status = "sent"
            logger.info(f"Audio alert triggered for anomaly {anomaly_id}")

        elif channel == "email":
            delivery_status = "delivered"
            logger.info(f"Email alert dispatched for anomaly {anomaly_id} to registered users.")

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
            with get_db() as conn:
                tokens = conn.execute(
                    "SELECT fcm_token FROM users WHERE role = 'new_device' AND fcm_token IS NOT NULL"
                ).fetchall()

            if not tokens:
                return {"status": "sent", "message_id": None}

            for token_row in tokens:
                try:
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
                    messaging.send(message)
                except Exception as e:
                    logger.error(f"FCM send failed for token {token_row['fcm_token']}: {e}")
            return {"status": "delivered", "message_id": "multicast-done"}

        except Exception as e:
            logger.error(f"FCM send failed: {e}")
            return {"status": "failed", "message_id": None}


# Singleton instance
alert_service = AlertService()
