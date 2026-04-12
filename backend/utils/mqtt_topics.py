"""
HomeGuardian AI — MQTT Topic Helpers
Topic constants and parsing utilities.
"""


class MQTTTopics:
    """MQTT topic namespace and utilities."""

    SENSOR_FRAME_PATTERN = "homeguardian/sensors/+/frame"
    SENSOR_HEARTBEAT_PATTERN = "homeguardian/sensors/+/heartbeat"
    SENSOR_STATUS_PATTERN = "homeguardian/sensors/+/status"
    SENSOR_AUDIO_PATTERN = "homeguardian/sensors/+/audio"
    COMMAND_PATTERN = "homeguardian/commands/+"
    ALERT_BROADCAST = "homeguardian/alerts/broadcast"
    SYSTEM_STATUS = "homeguardian/system/status"

    @staticmethod
    def sensor_frame(device_id: str) -> str:
        return f"homeguardian/sensors/{device_id}/frame"

    @staticmethod
    def sensor_heartbeat(device_id: str) -> str:
        return f"homeguardian/sensors/{device_id}/heartbeat"

    @staticmethod
    def sensor_status(device_id: str) -> str:
        return f"homeguardian/sensors/{device_id}/status"

    @staticmethod
    def command_to_device(device_id: str) -> str:
        return f"homeguardian/commands/{device_id}"

    @staticmethod
    def extract_device_id(topic: str) -> str:
        parts = topic.split("/")
        if len(parts) >= 3 and parts[0] == "homeguardian" and parts[1] in ("sensors", "commands"):
            return parts[2]
        return ""

    @staticmethod
    def extract_message_type(topic: str) -> str:
        parts = topic.split("/")
        return parts[3] if len(parts) >= 4 else ""
