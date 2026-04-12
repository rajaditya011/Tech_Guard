# Chunk 02 — Backend Core

**Goal**: Build the FastAPI application entry point, database initialization, JWT authentication, MQTT client, WebSocket manager, and all Pydantic models.
**Estimated Time**: 45 minutes
**Dependencies**: Chunk 01
**Unlocks**: Chunk 03 (Sensor Pipeline), Chunk 06 (Frontend Shell) — both can start in parallel after this.

---

## 02.1 — Configuration (backend/config.py)

```python
"""
HomeGuardian AI — Configuration
Loads and validates all environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    """Application settings loaded from environment variables."""

    # Demo Mode
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"

    # Claude API
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "")

    # Firebase
    FCM_SERVER_KEY: str = os.getenv("FCM_SERVER_KEY", "")

    # MQTT
    MQTT_BROKER_URL: str = os.getenv("MQTT_BROKER_URL", "localhost")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))

    # Database
    DB_PATH: str = os.getenv("DB_PATH", "data/homeguardian.db")

    # YOLO
    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", "models/yolov8n.pt")

    # Baseline
    BASELINE_DAYS: int = int(os.getenv("BASELINE_DAYS", "14"))
    ANOMALY_THRESHOLD: float = float(os.getenv("ANOMALY_THRESHOLD", "0.65"))

    # Clip Extraction
    CLIP_PRE_SECONDS: int = int(os.getenv("CLIP_PRE_SECONDS", "5"))
    CLIP_POST_SECONDS: int = int(os.getenv("CLIP_POST_SECONDS", "10"))

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "homeguardian-dev-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRY_MINUTES: int = int(os.getenv("JWT_ACCESS_EXPIRY_MINUTES", "15"))
    JWT_REFRESH_EXPIRY_DAYS: int = int(os.getenv("JWT_REFRESH_EXPIRY_DAYS", "7"))

    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

    # Server
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "5173"))

    @classmethod
    def validate(cls):
        """Validate critical settings on startup."""
        errors = []
        if not cls.DEMO_MODE:
            if not cls.CLAUDE_API_KEY:
                errors.append("CLAUDE_API_KEY is required when DEMO_MODE=false")
            if not cls.FCM_SERVER_KEY:
                errors.append("FCM_SERVER_KEY is required when DEMO_MODE=false")
        if not cls.JWT_SECRET or cls.JWT_SECRET == "homeguardian-dev-secret-change-in-production":
            import warnings
            warnings.warn("Using default JWT_SECRET — change this in production!")
        return errors


settings = Settings()
```

---

## 02.2 — Database Initialization (backend/database.py)

```python
"""
HomeGuardian AI — Database
SQLite connection, schema initialization, and query helpers.
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

from config import settings

DB_FULL_PATH = Path(__file__).parent / settings.DB_PATH


def get_db_path() -> str:
    """Get the full database path and ensure the directory exists."""
    DB_FULL_PATH.parent.mkdir(parents=True, exist_ok=True)
    return str(DB_FULL_PATH)


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """Create all tables if they do not exist."""
    with get_db() as conn:
        conn.executescript("""
            -- Users: Both old device and new device users
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                role TEXT NOT NULL CHECK(role IN ('old_device', 'new_device')),
                device_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                fcm_token TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

            -- Sensor Nodes: All enrolled devices
            CREATE TABLE IF NOT EXISTS sensor_nodes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('phone', 'webcam', 'cctv')),
                location_zone TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'inactive'
                    CHECK(status IN ('active', 'inactive', 'learning', 'alert')),
                last_heartbeat DATETIME,
                enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            );
            CREATE INDEX IF NOT EXISTS idx_sensor_nodes_owner ON sensor_nodes(owner_id);
            CREATE INDEX IF NOT EXISTS idx_sensor_nodes_status ON sensor_nodes(status);

            -- Behavioral Baseline Profiles
            CREATE TABLE IF NOT EXISTS baseline_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_node_id TEXT NOT NULL,
                zone TEXT NOT NULL,
                hour_of_day INTEGER NOT NULL CHECK(hour_of_day >= 0 AND hour_of_day <= 23),
                day_of_week INTEGER NOT NULL CHECK(day_of_week >= 0 AND day_of_week <= 6),
                activity_probability REAL NOT NULL DEFAULT 0.0,
                avg_movement_speed REAL DEFAULT 0.0,
                trajectory_cluster_centroids TEXT,
                sample_count INTEGER NOT NULL DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sensor_node_id) REFERENCES sensor_nodes(id)
            );
            CREATE INDEX IF NOT EXISTS idx_baseline_zone_hour
                ON baseline_profiles(zone, hour_of_day, day_of_week);

            -- Anomaly Events
            CREATE TABLE IF NOT EXISTS anomaly_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_node_ids TEXT NOT NULL,
                zone TEXT NOT NULL,
                detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                anomaly_score REAL NOT NULL,
                risk_level TEXT NOT NULL
                    CHECK(risk_level IN ('low', 'medium', 'high', 'critical')),
                classification TEXT,
                baseline_deviation REAL,
                duration_seconds REAL,
                clip_path TEXT,
                narrative_text TEXT,
                acknowledged INTEGER NOT NULL DEFAULT 0,
                acknowledged_at DATETIME,
                acknowledged_by TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_anomaly_detected_at ON anomaly_events(detected_at);
            CREATE INDEX IF NOT EXISTS idx_anomaly_risk_level ON anomaly_events(risk_level);

            -- Alerts
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anomaly_event_id INTEGER NOT NULL,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                channel TEXT NOT NULL CHECK(channel IN ('push', 'audio', 'log')),
                delivery_status TEXT NOT NULL DEFAULT 'pending'
                    CHECK(delivery_status IN ('pending', 'sent', 'delivered', 'failed')),
                fcm_message_id TEXT,
                FOREIGN KEY (anomaly_event_id) REFERENCES anomaly_events(id)
            );
            CREATE INDEX IF NOT EXISTS idx_alerts_anomaly ON alerts(anomaly_event_id);

            -- Scenario Library (F11)
            CREATE TABLE IF NOT EXISTS scenario_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                phase_count INTEGER NOT NULL,
                phase_definitions_json TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            -- Prediction Events (F11)
            CREATE TABLE IF NOT EXISTS prediction_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matched_scenario_id INTEGER NOT NULL,
                matched_phase TEXT NOT NULL,
                confidence REAL NOT NULL,
                predicted_next_phase TEXT,
                detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved_at DATETIME,
                outcome TEXT,
                FOREIGN KEY (matched_scenario_id) REFERENCES scenario_library(id)
            );
            CREATE INDEX IF NOT EXISTS idx_prediction_detected ON prediction_events(detected_at);
        """)
    print("[DB] Database initialized successfully.")
```

---

## 02.3 — Pydantic Models (backend/models.py)

```python
"""
HomeGuardian AI — Pydantic Models
Request and response schemas for all API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================================
# Enums
# ============================================================
class UserRole(str, Enum):
    OLD_DEVICE = "old_device"
    NEW_DEVICE = "new_device"


class DeviceType(str, Enum):
    PHONE = "phone"
    WEBCAM = "webcam"
    CCTV = "cctv"


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


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


# ============================================================
# Auth Models
# ============================================================
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


# ============================================================
# Sensor Node Models
# ============================================================
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


# ============================================================
# Baseline Models
# ============================================================
class BaselineStatusResponse(BaseModel):
    sensor_id: str
    zone: str
    days_complete: int
    days_required: int
    percent_complete: float
    zones_learning: List[str]
    sample_counts: dict
    estimated_completion: Optional[str]


class BaselineProfileResponse(BaseModel):
    zone: str
    hour_of_day: int
    day_of_week: int
    activity_probability: float
    avg_movement_speed: float
    sample_count: int


# ============================================================
# Anomaly Models
# ============================================================
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


# ============================================================
# Alert Models
# ============================================================
class AlertResponse(BaseModel):
    id: int
    anomaly_event_id: int
    sent_at: str
    channel: AlertChannel
    delivery_status: DeliveryStatus
    fcm_message_id: Optional[str]


# ============================================================
# Clip Models
# ============================================================
class ClipMetadataResponse(BaseModel):
    anomaly_id: int
    clip_path: str
    duration_seconds: float
    pre_event_seconds: float
    post_event_seconds: float
    thumbnail_url: Optional[str]
    created_at: str


# ============================================================
# Narrative Models
# ============================================================
class NarrativeResponse(BaseModel):
    anomaly_id: int
    narrative_text: str
    generated_by: str  # "claude" or "template"
    generated_at: str


# ============================================================
# Dashboard Models
# ============================================================
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


class HeatmapData(BaseModel):
    zone: str
    intensity: float
    activity_count: int
    last_activity: Optional[str]
    risk_level: RiskLevel


# ============================================================
# Risk Score Models
# ============================================================
class RiskScoreResponse(BaseModel):
    score: int
    risk_level: RiskLevel
    factors: dict
    trend: str  # "escalating", "stable", "de-escalating"
    timestamp: str


# ============================================================
# Communication Models
# ============================================================
class SendMessageRequest(BaseModel):
    target_device_id: str
    message_text: Optional[str] = None
    audio_url: Optional[str] = None
    message_type: str = "text"  # "text" or "audio"


class MessageResponse(BaseModel):
    message_id: str
    status: str
    sent_at: str


# ============================================================
# Prediction Models (F11)
# ============================================================
class PredictionEventResponse(BaseModel):
    id: int
    matched_scenario_id: int
    matched_scenario_name: Optional[str]
    matched_phase: str
    confidence: float
    predicted_next_phase: Optional[str]
    detected_at: str
    resolved_at: Optional[str]
    outcome: Optional[str]


class ReasoningTimelineEntry(BaseModel):
    timestamp: str
    event_type: str
    data_point: str
    conclusion: str
    confidence_delta: float


class ReasoningTimelineResponse(BaseModel):
    prediction_id: int
    entries: List[ReasoningTimelineEntry]


# ============================================================
# Demo Models
# ============================================================
class DemoScenarioResponse(BaseModel):
    id: int
    name: str
    phase_count: int
    description: Optional[str]


class DemoStartResponse(BaseModel):
    status: str
    scenario: str
    message: str


# ============================================================
# System Models
# ============================================================
class HealthResponse(BaseModel):
    status: str
    services: dict
    version: str = "1.0.0"
    demo_mode: bool
```

---

## 02.4 — JWT Authentication (backend/auth.py)

```python
"""
HomeGuardian AI — Authentication
JWT token management for both portal types.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings
from database import get_db
from models import UserRole

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token scheme
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, role: str) -> str:
    """Create a JWT access token."""
    expires = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_EXPIRY_MINUTES)
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "exp": expires,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4())
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str, role: str) -> str:
    """Create a JWT refresh token."""
    expires = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRY_DAYS)
    payload = {
        "sub": user_id,
        "role": role,
        "type": "refresh",
        "exp": expires,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4())
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Extract and validate the current user from the JWT token."""
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    with get_db() as conn:
        user = conn.execute(
            "SELECT id, role, device_name FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return dict(user)


def require_role(required_role: UserRole):
    """Dependency that requires a specific user role."""
    async def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This endpoint requires {required_role.value} role"
            )
        return user
    return role_checker


def register_user(device_name: str, password: str, role: str, fcm_token: Optional[str] = None) -> dict:
    """Register a new user."""
    user_id = str(uuid.uuid4())
    password_hash = hash_password(password)
    with get_db() as conn:
        # Check if device_name already exists for this role
        existing = conn.execute(
            "SELECT id FROM users WHERE device_name = ? AND role = ?",
            (device_name, role)
        ).fetchone()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Device name already registered for this role"
            )
        conn.execute(
            "INSERT INTO users (id, role, device_name, password_hash, fcm_token) VALUES (?, ?, ?, ?, ?)",
            (user_id, role, device_name, password_hash, fcm_token)
        )
    return {
        "id": user_id,
        "role": role,
        "device_name": device_name
    }


def authenticate_user(device_name: str, password: str) -> Optional[dict]:
    """Authenticate a user and return user data if valid."""
    with get_db() as conn:
        user = conn.execute(
            "SELECT id, role, device_name, password_hash FROM users WHERE device_name = ?",
            (device_name,)
        ).fetchone()
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return {
        "id": user["id"],
        "role": user["role"],
        "device_name": user["device_name"]
    }
```

---

## 02.5 — MQTT Client (backend/mqtt_client.py)

```python
"""
HomeGuardian AI — MQTT Client
Connection management and message routing.
"""

import json
import logging
import threading
from typing import Callable, Dict, List

import paho.mqtt.client as mqtt

from config import settings

logger = logging.getLogger("homeguardian.mqtt")


# Topic constants
class Topics:
    """MQTT topic namespace."""
    SENSOR_FRAME = "homeguardian/sensors/{device_id}/frame"
    SENSOR_HEARTBEAT = "homeguardian/sensors/{device_id}/heartbeat"
    SENSOR_STATUS = "homeguardian/sensors/{device_id}/status"
    SENSOR_AUDIO = "homeguardian/sensors/{device_id}/audio"

    COMMAND_TO_DEVICE = "homeguardian/commands/{device_id}"
    ALERT_BROADCAST = "homeguardian/alerts/broadcast"
    SYSTEM_STATUS = "homeguardian/system/status"

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
        self.client = mqtt.Client(client_id="homeguardian-hub", protocol=mqtt.MQTTv311)
        self.connected = False
        self._handlers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()

        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def connect(self):
        """Connect to the MQTT broker."""
        try:
            logger.info(f"Connecting to MQTT broker at {settings.MQTT_BROKER_URL}:{settings.MQTT_PORT}")
            self.client.connect(
                settings.MQTT_BROKER_URL,
                settings.MQTT_PORT,
                keepalive=60
            )
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            if settings.DEMO_MODE:
                logger.warning("DEMO_MODE: Continuing without MQTT connection")
            else:
                raise

    def disconnect(self):
        """Disconnect from the MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False

    def subscribe(self, topic: str, handler: Callable):
        """Subscribe to a topic with a message handler."""
        with self._lock:
            if topic not in self._handlers:
                self._handlers[topic] = []
                if self.connected:
                    self.client.subscribe(topic)
            self._handlers[topic].append(handler)

    def publish(self, topic: str, payload: dict, qos: int = 1):
        """Publish a message to a topic."""
        try:
            message = json.dumps(payload)
            self.client.publish(topic, message, qos=qos)
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker."""
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker")
            # Subscribe to all registered topics
            with self._lock:
                for topic in self._handlers:
                    client.subscribe(topic)
                # Subscribe to wildcard for all sensor data
                client.subscribe("homeguardian/sensors/+/frame")
                client.subscribe("homeguardian/sensors/+/heartbeat")
                client.subscribe("homeguardian/sensors/+/status")
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from broker."""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection (rc={rc}). Reconnecting...")

    def _on_message(self, client, userdata, msg):
        """Callback when a message is received."""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())

            # Find matching handlers (including wildcard matches)
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
        """Check if a topic matches a subscription pattern (supports + and # wildcards)."""
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


# Singleton instance
mqtt_manager = MQTTManager()
```

---

## 02.6 — WebSocket Manager (backend/websocket_manager.py)

```python
"""
HomeGuardian AI — WebSocket Manager
Manages WebSocket connections for both portal types.
"""

import json
import logging
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger("homeguardian.websocket")


class ConnectionManager:
    """Manages WebSocket connections for old devices and dashboard users."""

    def __init__(self):
        # Old device connections: {device_id: WebSocket}
        self.old_devices: Dict[str, WebSocket] = {}
        # Dashboard connections: {user_id: WebSocket}
        self.dashboards: Dict[str, WebSocket] = {}

    async def connect_old_device(self, device_id: str, websocket: WebSocket):
        """Register an old device WebSocket connection."""
        await websocket.accept()
        self.old_devices[device_id] = websocket
        logger.info(f"Old device connected: {device_id}")

    async def connect_dashboard(self, user_id: str, websocket: WebSocket):
        """Register a dashboard WebSocket connection."""
        await websocket.accept()
        self.dashboards[user_id] = websocket
        logger.info(f"Dashboard connected: {user_id}")

    def disconnect_old_device(self, device_id: str):
        """Remove an old device connection."""
        self.old_devices.pop(device_id, None)
        logger.info(f"Old device disconnected: {device_id}")

    def disconnect_dashboard(self, user_id: str):
        """Remove a dashboard connection."""
        self.dashboards.pop(user_id, None)
        logger.info(f"Dashboard disconnected: {user_id}")

    async def send_to_old_device(self, device_id: str, message: dict):
        """Send a message to a specific old device."""
        ws = self.old_devices.get(device_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to old device {device_id}: {e}")
                self.disconnect_old_device(device_id)

    async def send_to_dashboard(self, user_id: str, message: dict):
        """Send a message to a specific dashboard."""
        ws = self.dashboards.get(user_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to dashboard {user_id}: {e}")
                self.disconnect_dashboard(user_id)

    async def broadcast_to_dashboards(self, message: dict):
        """Broadcast a message to all connected dashboards."""
        disconnected = []
        for user_id, ws in self.dashboards.items():
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(user_id)
        for user_id in disconnected:
            self.disconnect_dashboard(user_id)

    async def broadcast_to_old_devices(self, message: dict):
        """Broadcast a message to all connected old devices."""
        disconnected = []
        for device_id, ws in self.old_devices.items():
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(device_id)
        for device_id in disconnected:
            self.disconnect_old_device(device_id)

    @property
    def active_old_devices(self) -> int:
        return len(self.old_devices)

    @property
    def active_dashboards(self) -> int:
        return len(self.dashboards)


# Singleton instance
connection_manager = ConnectionManager()
```

---

## 02.7 — FastAPI Application Entry Point (backend/main.py)

```python
"""
HomeGuardian AI — Main Application
FastAPI entry point with all middleware and route configuration.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import settings
from database import init_database
from mqtt_client import mqtt_manager
from websocket_manager import connection_manager
from auth import decode_token

# ---- Logging Setup ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("homeguardian")

# ---- Rate Limiter ----
limiter = Limiter(key_func=get_remote_address)


# ---- Lifespan ----
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # Startup
    logger.info("Starting HomeGuardian AI...")
    logger.info(f"Demo Mode: {settings.DEMO_MODE}")

    # Validate settings
    errors = settings.validate()
    for error in errors:
        logger.warning(f"Config Warning: {error}")

    # Initialize database
    init_database()

    # Connect MQTT
    try:
        mqtt_manager.connect()
    except Exception as e:
        logger.error(f"MQTT connection failed: {e}")

    logger.info("HomeGuardian AI started successfully.")
    yield

    # Shutdown
    logger.info("Shutting down HomeGuardian AI...")
    mqtt_manager.disconnect()
    logger.info("Shutdown complete.")


# ---- App Instance ----
app = FastAPI(
    title="HomeGuardian AI",
    description="Adaptive Intelligence Security System API",
    version="1.0.0",
    lifespan=lifespan
)

# ---- Middleware ----
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Security Headers Middleware ----
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: blob:; "
        "connect-src 'self' ws: wss:; "
    )
    return response


# ---- Import and Include Routers ----
from routers.auth_routes import router as auth_router
from routers.sensor_routes import router as sensor_router
from routers.demo_routes import router as demo_router

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sensor_router, prefix="/api/sensors", tags=["Sensors"])
app.include_router(demo_router, prefix="/api/demo", tags=["Demo"])

# Additional routers will be added in subsequent chunks:
# from routers.stream_routes import router as stream_router
# from routers.anomaly_routes import router as anomaly_router
# from routers.alert_routes import router as alert_router
# from routers.clip_routes import router as clip_router
# from routers.narrative_routes import router as narrative_router
# from routers.dashboard_routes import router as dashboard_router
# from routers.communication_routes import router as communication_router
# from routers.prediction_routes import router as prediction_router


# ---- Health Check ----
@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "demo_mode": settings.DEMO_MODE,
        "services": {
            "database": "connected",
            "mqtt": "connected" if mqtt_manager.connected else "disconnected",
            "websocket_old_devices": connection_manager.active_old_devices,
            "websocket_dashboards": connection_manager.active_dashboards
        }
    }


# ---- WebSocket Endpoints ----
@app.websocket("/ws/old-device/{device_id}")
async def websocket_old_device(websocket: WebSocket, device_id: str):
    """WebSocket endpoint for old device communication."""
    # TODO: Add token authentication on handshake in Chunk 09
    await connection_manager.connect_old_device(device_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Route received data to appropriate handler
            msg_type = data.get("type", "")
            if msg_type == "sensor_frame":
                # Will be handled by sensor pipeline (Chunk 03)
                pass
            elif msg_type == "heartbeat":
                # Update heartbeat in database
                pass
            logger.debug(f"Received from old device {device_id}: {msg_type}")
    except WebSocketDisconnect:
        connection_manager.disconnect_old_device(device_id)


@app.websocket("/ws/dashboard/{user_id}")
async def websocket_dashboard(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for dashboard real-time updates."""
    # TODO: Add token authentication on handshake in Chunk 09
    await connection_manager.connect_dashboard(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "")
            if msg_type == "send_message":
                # Two-way communication (Chunk 05)
                target_device = data.get("target_device_id")
                if target_device:
                    await connection_manager.send_to_old_device(target_device, {
                        "type": "incoming_message",
                        "from": user_id,
                        "content": data.get("content", "")
                    })
            logger.debug(f"Received from dashboard {user_id}: {msg_type}")
    except WebSocketDisconnect:
        connection_manager.disconnect_dashboard(user_id)


# ---- Error Handlers ----
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler — no stack traces in production."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again later."}
    )
```

---

## 02.8 — Auth Routes (backend/routers/auth_routes.py)

```python
"""
HomeGuardian AI — Authentication Routes
"""

import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

from models import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse
)
from auth import (
    register_user, authenticate_user,
    create_access_token, create_refresh_token,
    decode_token, get_current_user
)
from config import settings

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(request: RegisterRequest):
    """Register a new user (old_device or new_device)."""
    try:
        user = register_user(
            device_name=request.device_name,
            password=request.password,
            role=request.role.value,
            fcm_token=request.fcm_token
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Registration failed")

    access_token = create_access_token(user["id"], user["role"])
    refresh_token = create_refresh_token(user["id"], user["role"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user["role"],
        expires_in=settings.JWT_ACCESS_EXPIRY_MINUTES * 60
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate a user and return JWT tokens."""
    user = authenticate_user(request.device_name, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device name or password"
        )

    access_token = create_access_token(user["id"], user["role"])
    refresh_token = create_refresh_token(user["id"], user["role"])

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user["role"],
        expires_in=settings.JWT_ACCESS_EXPIRY_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Refresh an access token using a refresh token."""
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    role = payload.get("role")

    new_access_token = create_access_token(user_id, role)
    new_refresh_token = create_refresh_token(user_id, role)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        role=role,
        expires_in=settings.JWT_ACCESS_EXPIRY_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """Get the current authenticated user's info."""
    return UserResponse(
        id=user["id"],
        role=user["role"],
        device_name=user["device_name"],
        created_at=""
    )
```

---

## 02.9 — Sensor Routes (backend/routers/sensor_routes.py)

```python
"""
HomeGuardian AI — Sensor Node Routes
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends

from models import SensorNodeCreate, SensorNodeResponse, SensorHealthResponse
from auth import get_current_user, require_role
from models import UserRole
from database import get_db

router = APIRouter()


@router.get("/", response_model=list)
async def list_sensors(user: dict = Depends(get_current_user)):
    """List all sensor nodes for the current user."""
    with get_db() as conn:
        if user["role"] == "new_device":
            # Dashboard users see all sensors
            rows = conn.execute("SELECT * FROM sensor_nodes ORDER BY enrolled_at DESC").fetchall()
        else:
            # Old device users see only their own sensor
            rows = conn.execute(
                "SELECT * FROM sensor_nodes WHERE owner_id = ?",
                (user["id"],)
            ).fetchall()
    return [dict(row) for row in rows]


@router.post("/", response_model=SensorNodeResponse, status_code=201)
async def register_sensor(sensor: SensorNodeCreate, user: dict = Depends(get_current_user)):
    """Register a new sensor node."""
    sensor_id = f"{sensor.type.value}-{str(uuid.uuid4())[:8]}"
    with get_db() as conn:
        conn.execute(
            """INSERT INTO sensor_nodes (id, name, type, location_zone, owner_id, status)
               VALUES (?, ?, ?, ?, ?, 'learning')""",
            (sensor_id, sensor.name, sensor.type.value, sensor.location_zone, user["id"])
        )
        row = conn.execute("SELECT * FROM sensor_nodes WHERE id = ?", (sensor_id,)).fetchone()
    return SensorNodeResponse(**dict(row))


@router.get("/{sensor_id}", response_model=SensorNodeResponse)
async def get_sensor(sensor_id: str, user: dict = Depends(get_current_user)):
    """Get details of a specific sensor node."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM sensor_nodes WHERE id = ?", (sensor_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sensor node not found")
    return SensorNodeResponse(**dict(row))


@router.put("/{sensor_id}/heartbeat")
async def update_heartbeat(sensor_id: str, user: dict = Depends(get_current_user)):
    """Update the heartbeat timestamp for a sensor node."""
    with get_db() as conn:
        result = conn.execute(
            "UPDATE sensor_nodes SET last_heartbeat = ?, status = 'active' WHERE id = ?",
            (datetime.utcnow().isoformat(), sensor_id)
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Sensor node not found")
    return {"status": "ok", "sensor_id": sensor_id}


@router.get("/{sensor_id}/health", response_model=SensorHealthResponse)
async def get_sensor_health(sensor_id: str, user: dict = Depends(get_current_user)):
    """Get health status of a specific sensor node."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM sensor_nodes WHERE id = ?", (sensor_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sensor node not found")

    sensor = dict(row)
    uptime = None
    quality = "unknown"

    if sensor.get("last_heartbeat"):
        try:
            last_hb = datetime.fromisoformat(sensor["last_heartbeat"])
            delta = datetime.utcnow() - last_hb
            uptime = int(delta.total_seconds())
            if delta.total_seconds() < 30:
                quality = "excellent"
            elif delta.total_seconds() < 120:
                quality = "good"
            elif delta.total_seconds() < 300:
                quality = "poor"
            else:
                quality = "disconnected"
        except ValueError:
            pass

    return SensorHealthResponse(
        sensor_id=sensor_id,
        status=sensor["status"],
        last_heartbeat=sensor.get("last_heartbeat"),
        uptime_seconds=uptime,
        connection_quality=quality
    )
```

---

## 02.10 — Demo Routes (backend/routers/demo_routes.py)

```python
"""
HomeGuardian AI — Demo Mode Routes
"""

from fastapi import APIRouter, HTTPException
from models import DemoScenarioResponse, DemoStartResponse
from config import settings

router = APIRouter()

# Pre-defined demo scenarios
DEMO_SCENARIOS = [
    {
        "id": 1,
        "name": "Normal Morning Routine",
        "phase_count": 1,
        "description": "14-day baseline established. Owner leaves at 8 AM. Normal kitchen and living room activity. No alerts."
    },
    {
        "id": 2,
        "name": "Late Night Anomaly",
        "phase_count": 3,
        "description": "2:43 AM motion in living room. No baseline match. Risk escalates from Medium to High. Clip generated. Narrative written."
    },
    {
        "id": 3,
        "name": "Casing Simulation",
        "phase_count": 2,
        "description": "Afternoon perimeter sensor detects slow repeated passes. Watch flag raised. Escalates to Suspicious. 73% casing match."
    },
    {
        "id": 4,
        "name": "Full Intrusion Prediction",
        "phase_count": 4,
        "description": "Complete 4-phase simulation. Casing, Entry Probing detected. Critical alert during Entry Probing before Intrusion phase."
    }
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

    # TODO: Implement scenario simulation engine in Chunk 09
    return DemoStartResponse(
        status="started",
        scenario=scenario["name"],
        message=f"Demo scenario '{scenario['name']}' started. Events will be injected via WebSocket."
    )


@router.post("/stop")
async def stop_scenario():
    """Stop the active demo simulation."""
    return {"status": "stopped", "message": "Demo simulation stopped."}
```

---

## Verification

```bash
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment
source venv/bin/activate  # or: source ../venv/bin/activate

# 3. Start the server
uvicorn main:app --reload --port 8000

# 4. Test health endpoint
curl http://localhost:8000/api/health

# 5. Test registration
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"device_name":"test-phone","password":"test123456","role":"old_device"}'

# 6. Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"device_name":"test-phone","password":"test123456"}'

# 7. Test demo scenarios
curl http://localhost:8000/api/demo/scenarios

# 8. Check API docs
# Open: http://localhost:8000/docs
```

Expected: Server starts without errors. Health endpoint returns JSON with status "healthy". Registration returns JWT tokens. Login returns JWT tokens. Demo scenarios endpoint returns 4 scenarios. Swagger docs accessible at /docs.
