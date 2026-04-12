"""
HomeGuardian AI — Pydantic Models
Request and response schemas for all API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    OLD_DEVICE = "old_device"
    NEW_DEVICE = "new_device"

class DeviceType(str, Enum):
    PHONE = "phone"
    WEBCAM = "webcam"
    CCTV = "cctv"
    IOT_SENSOR = "iot_sensor"

class DeviceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    LEARNING = "learning"
    ALERT = "alert"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertChannel(str, Enum):
    PUSH = "push"
    AUDIO = "audio"
    LOG = "log"
    EMAIL = "email"

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


# Auth Models
class RegisterRequest(BaseModel):
    device_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)
    role: UserRole
    fcm_token: Optional[str] = None

class LoginRequest(BaseModel):
    device_name: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: UserRole
    expires_in: int

class UserResponse(BaseModel):
    id: str
    role: UserRole
    device_name: str
    created_at: str


# Sensor Node Models
class SensorNodeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: DeviceType
    location_zone: str = Field(..., min_length=1, max_length=100)

class SensorNodeResponse(BaseModel):
    id: str
    name: str
    type: DeviceType
    location_zone: str
    owner_id: str
    status: DeviceStatus
    last_heartbeat: Optional[str]
    enrolled_at: str

class SensorHealthResponse(BaseModel):
    sensor_id: str
    status: DeviceStatus
    last_heartbeat: Optional[str]
    uptime_seconds: Optional[int]
    connection_quality: str = "unknown"


# Baseline Models
class BaselineStatusResponse(BaseModel):
    sensor_id: str
    zone: str
    days_complete: int
    days_required: int
    percent_complete: float
    zones_learning: List[str]
    sample_counts: dict
    estimated_completion: Optional[str]


# Anomaly Models
class AnomalyEventResponse(BaseModel):
    id: int
    sensor_node_ids: str
    zone: str
    detected_at: str
    anomaly_score: float
    risk_level: RiskLevel
    classification: Optional[str]
    baseline_deviation: Optional[float]
    duration_seconds: Optional[float]
    clip_path: Optional[str]
    narrative_text: Optional[str]
    acknowledged: bool
    acknowledged_at: Optional[str]
    acknowledged_by: Optional[str]

class AnomalyAcknowledgeRequest(BaseModel):
    acknowledged_by: str


# Alert Models
class AlertResponse(BaseModel):
    id: int
    anomaly_event_id: int
    sent_at: str
    channel: AlertChannel
    delivery_status: DeliveryStatus
    fcm_message_id: Optional[str]


# Dashboard Models
class DashboardSummary(BaseModel):
    active_sensors: int
    total_sensors: int
    system_mode: str
    baseline_status: str
    current_risk: int
    risk_level: RiskLevel
    total_anomalies_today: int
    total_alerts_today: int
    uptime_hours: int


# Risk Score Models
class RiskScoreResponse(BaseModel):
    score: int
    risk_level: RiskLevel
    factors: dict
    trend: str
    timestamp: str


# Communication Models
class SendMessageRequest(BaseModel):
    target_device_id: str
    message_text: Optional[str] = None
    audio_url: Optional[str] = None
    message_type: str = "text"

class MessageResponse(BaseModel):
    message_id: str
    status: str
    sent_at: str


# Demo Models
class DemoScenarioResponse(BaseModel):
    id: int
    name: str
    phase_count: int
    description: Optional[str]

class DemoStartResponse(BaseModel):
    status: str
    scenario: str
    message: str


# System Models
class HealthResponse(BaseModel):
    status: str
    services: dict
    version: str = "1.0.0"
    demo_mode: bool
