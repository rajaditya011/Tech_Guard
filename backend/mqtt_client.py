"""
HomeGuardian AI — MQTT Client
Connection management and message routing.
"""

import json
import logging
import threading
from typing import Callable, Dict, List

try:
    import paho.mqtt.client as mqtt
    from paho.mqtt.enums import CallbackAPIVersion
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

from config import settings

logger = logging.getLogger("homeguardian.mqtt")


class Topics:
    """MQTT topic namespace."""
    @staticmethod
    def sensor_frame(device_id: str) -> str:
        return f"homeguardian/sensors/{device_id}/frame"
    @staticmethod
    def sensor_heartbeat(device_id: str) -> str:
        return f"homeguardian/sensors/{device_id}/heartbeat"
    @staticmethod
    def command_to_device(device_id: str) -> str:
        return f"homeguardian/commands/{device_id}"


class MQTTManager:
    """Manages MQTT connection and message routing."""

    def __init__(self):
        if MQTT_AVAILABLE:
            self.client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION1, client_id="homeguardian-hub", protocol=mqtt.MQTTv311)
        else:
            self.client = None
            logger.warning("paho-mqtt not available. MQTT features disabled.")
        self.connected = False
        self._handlers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
        if self.client:
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

    def connect(self):
        if not self.client:
            logger.warning("MQTT client not available. Skipping connection.")
            return
        try:
            logger.info(f"Connecting to MQTT broker at {settings.MQTT_BROKER_URL}:{settings.MQTT_PORT}")
            self.client.connect(settings.MQTT_BROKER_URL, settings.MQTT_PORT, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            if settings.DEMO_MODE:
                logger.warning("DEMO_MODE: Continuing without MQTT connection")
            else:
                raise

    def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
        self.connected = False

    def subscribe(self, topic: str, handler: Callable):
        with self._lock:
            if topic not in self._handlers:
                self._handlers[topic] = []
                if self.connected and self.client:
                    self.client.subscribe(topic)
            self._handlers[topic].append(handler)

    def publish(self, topic: str, payload: dict, qos: int = 1):
        if not self.client:
            return
        try:
            message = json.dumps(payload)
            self.client.publish(topic, message, qos=qos)
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker")
            with self._lock:
                for topic in self._handlers:
                    client.subscribe(topic)
                client.subscribe("homeguardian/sensors/+/frame")
                client.subscribe("homeguardian/sensors/+/heartbeat")
                client.subscribe("homeguardian/sensors/+/status")
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection (rc={rc}). Reconnecting...")

    def _on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            with self._lock:
                for pattern, handlers in self._handlers.items():
                    if self._topic_matches(pattern, topic):
                        for handler in handlers:
                            try:
                                handler(topic, payload)
                            except Exception as e:
                                logger.error(f"Handler error for {topic}: {e}")
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON on topic {msg.topic}")
        except Exception as e:
            logger.error(f"Message processing error: {e}")

    @staticmethod
    def _topic_matches(pattern: str, topic: str) -> bool:
        pattern_parts = pattern.split("/")
        topic_parts = topic.split("/")
        if len(pattern_parts) != len(topic_parts):
            if pattern_parts[-1] != "#":
                return False
        for p, t in zip(pattern_parts, topic_parts):
            if p == "+":
                continue
            elif p == "#":
                return True
            elif p != t:
                return False
        return len(pattern_parts) == len(topic_parts)


mqtt_manager = MQTTManager()
