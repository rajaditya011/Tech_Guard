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

        await connection_manager.broadcast_to_old_devices(payload)
        mqtt_manager.publish("homeguardian/alerts/broadcast", payload)

        return {
            "message_id": message_id,
            "status": "broadcast",
            "devices_reached": connection_manager.active_old_devices,
            "sent_at": payload["timestamp"]
        }


# Singleton instance
communication_service = CommunicationService()
