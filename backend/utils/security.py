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
