# HomeGuardian AI — Implementation Plan

**Version**: 1.0.0
**Last Updated**: 2026-04-11
**Change Notes**: Initial creation. Full technical specification for all features, architecture, schemas, APIs, design system, demo strategy, and build priorities.

---

## 1. Project Identity

| Field             | Value                                                        |
| ----------------- | ------------------------------------------------------------ |
| Project Name      | HomeGuardian AI                                              |
| Tagline           | Understanding behavior, not just detecting movement.         |
| Challenge         | Hackathon Challenge 06 — Smart Home Security Monitor         |
| Core Architecture | Dual-portal with AI processing hub                           |
| Target Stack      | Python/FastAPI + React/Vite + MQTT + YOLO + Claude           |

---

## 2. Services, APIs, and Platforms

| Service              | Auth Required | Free Tier Limits                         | Role in System                          |
| -------------------- | ------------- | ---------------------------------------- | --------------------------------------- |
| Claude API           | API Key       | $5 credit on signup                      | AI incident narrative generation        |
| Firebase FCM         | Service Acct  | Unlimited push notifications             | Push alerts to owner device             |
| Eclipse Mosquitto    | Optional ACL  | Self-hosted, no cost                     | MQTT broker for IoT sensor messaging    |
| Ultralytics YOLOv8   | None          | Free local inference                     | Object detection on video frames        |
| OpenCV               | None          | Free open-source                         | Frame processing and clip encoding      |
| scikit-learn         | None          | Free open-source                         | Isolation Forest, DBSCAN                |

---

## 3. Feature Specifications

### F01 — Legacy Device Integration

| Aspect      | Detail                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------ |
| **What**    | Plug-and-play enrollment for old smartphones, IP cameras, USB webcams                      |
| **How**     | Old Device Portal with camera permission request, MQTT connection, stream initialization    |
| **Key Detail** | Zero additional hardware cost. Any device with a camera and internet qualifies          |
| **Why It Matters** | Eliminates the primary barrier to home security adoption: cost                      |

### F02 — Behavioral Intelligence Engine

| Aspect      | Detail                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------ |
| **What**    | 7-14 day passive baseline learning of home behavioral patterns                             |
| **How**     | Per-zone, per-hour activity probability distributions; DBSCAN trajectory clustering         |
| **Key Detail** | Stores full behavioral profile in SQLite; adapts to gradual routine changes over time   |
| **Why It Matters** | Personalized baselines eliminate generic threshold false positives                   |

### F03 — Real-Time Vision Analysis

| Aspect      | Detail                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------ |
| **What**    | YOLO object detection on every incoming video frame                                        |
| **How**     | Frame preprocessing pipeline (resize, normalize), inference on AI hub, zone assignment      |
| **Key Detail** | Human detection, movement vector calculation, trajectory tracking. Runs server-side     |
| **Why It Matters** | Continuous monitoring without burdening old devices                                  |

### F04 — Multi-Sensor Fusion Engine

| Aspect      | Detail                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------ |
| **What**    | Cross-correlation of events across all active sensor nodes                                 |
| **How**     | Spatial consistency checking, compound event scoring, graph-based sequence reasoning         |
| **Key Detail** | Motion in Zone A without corridor reading is more suspicious than with it               |
| **Why It Matters** | Dramatically reduces false positives; validates events through multi-source consensus|

### F05 — Smart Clip Extraction Engine

| Aspect      | Detail                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------ |
| **What**    | Records nothing normally; captures 10-20s clips centered on anomaly events                  |
| **How**     | Ring buffer stores pre-event frames; post-event frames captured after detection              |
| **Key Detail** | MP4 with timestamp overlay, full metadata: sensor ID, zone, score, classification, path |
| **Why It Matters** | Every saved clip is immediately actionable evidence — no scrubbing hours of footage   |

### F06 — Context-Aware Alert System

| Aspect      | Detail                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------ |
| **What**    | Rich alerts with risk level, location, timestamp, AI reasoning, clip, and recommendations   |
| **How**     | FCM push notification with clip thumbnail; deduplication; smart escalation                   |
| **Key Detail** | Low = logged silently; High/Critical = push notification; Critical = audio on old device |
| **Why It Matters** | Intelligent escalation prevents alert fatigue while ensuring critical events seen     |

### F07 — AI Risk Scoring Engine

| Aspect      | Detail                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------ |
| **What**    | Dynamic risk score assigned to every anomaly, updating in real time                         |
| **How**     | Weighted factors: baseline deviation 40%, time-of-day 20%, zone sensitivity 20%, duration 10%, multi-sensor 10% |
| **Key Detail** | 0-25 Low, 26-50 Medium, 51-75 High, 76-100 Critical. Animated arc gauge on dashboard   |
| **Why It Matters** | Quantifies threat level for instant situational awareness                            |

### F08 — Smart Floor Plan Visualizer

| Aspect      | Detail                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------ |
| **What**    | Interactive SVG map with sensor locations and real-time activity heat zones                  |
| **How**     | Emerald (normal), amber (elevated), red (anomaly) heat zones; click-to-inspect              |
| **Key Detail** | Historical heat pattern views: 24h, 7d, 30d. Shows assigned sensor nodes per zone      |
| **Why It Matters** | Spatial awareness turns abstract data into intuitive visual intelligence              |

### F09 — AI Incident Narrative Generator

| Aspect      | Detail                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------ |
| **What**    | Claude-powered plain-English incident reports for every anomaly                             |
| **How**     | Structured JSON context sent to Claude; falls back to template narratives in demo mode      |
| **Key Detail** | Reads like a security officer's assessment, not a log file                              |
| **Why It Matters** | Makes AI reasoning accessible to non-technical users; judges love explainability      |

### F10 — Two-Way Communication System

| Aspect      | Detail                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------ |
| **What**    | Owner sends text/voice messages from dashboard to old device speakers                       |
| **How**     | MQTT message routing from New Device Dashboard to target Old Device node                    |
| **Key Detail** | Enables owner warnings, automated Critical alert audio, remote communication            |
| **Why It Matters** | Active deterrent capability; transforms passive cameras into interactive security     |

### F11 — Adaptive Surveillance Replay and Prediction Engine (Secret Weapon)

| Aspect      | Detail                                                                                     |
| ----------- | ------------------------------------------------------------------------------------------ |
| **What**    | Intrusion scenario matching with predictive alerting before final event occurs              |
| **How**     | Scenario library (Casing/Entry Probing/Reconnaissance/Intrusion); live sequence matching    |
| **Key Detail** | Raises prediction during early phases; AI reasoning timeline for demo replay            |
| **Why It Matters** | Catches intrusions during casing phase — before they start. The ultimate demo feature  |

---

## 4. System Architecture Diagram

```
+------------------------------------------------------------------+
|                      LEGACY DEVICE LAYER                         |
|                                                                  |
|  +------------+   +------------+   +------------+                |
|  | Old Phone  |   | IP Camera  |   | USB Webcam |                |
|  | (Sensor 1) |   | (Sensor 2) |   | (Sensor 3) |                |
|  +-----+------+   +-----+------+   +-----+------+                |
|        |                 |                 |                      |
|        +--------+--------+--------+--------+                     |
|                 |  MQTT (paho-mqtt)  |                            |
|                 +--------+-----------+                            |
+------------------------------------------------------------------+
                           |
                           v
+------------------------------------------------------------------+
|                    AI PROCESSING HUB                             |
|                                                                  |
|  +------------------+    +-------------------+                   |
|  | Frame Ingest     +--->| YOLO Inference    |                   |
|  | (Ring Buffer)    |    | (Object Detection)|                   |
|  +------------------+    +--------+----------+                   |
|                                   |                              |
|  +------------------+    +--------v----------+                   |
|  | Baseline Engine  |<---| Anomaly Detector  |                   |
|  | (DBSCAN/Stats)   |    | (Isolation Forest)|                   |
|  +------------------+    +--------+----------+                   |
|                                   |                              |
|  +------------------+    +--------v----------+                   |
|  | Multi-Sensor     +--->| Risk Score Engine |                   |
|  | Fusion           |    | (Dynamic Scoring) |                   |
|  +------------------+    +--------+----------+                   |
|                                   |                              |
|  +------------------+    +--------v----------+                   |
|  | Clip Extraction  |    | Claude Narrative  |                   |
|  | Engine (MP4)     |    | Generator         |                   |
|  +------------------+    +--------+----------+                   |
|                                   |                              |
|  +------------------+             |                              |
|  | Prediction       |             |                              |
|  | Engine (F11)     |             |                              |
|  +------------------+             |                              |
+------------------------------------------------------------------+
                           |
                           v
+------------------------------------------------------------------+
|                  INTELLIGENT RESPONSE LAYER                      |
|                                                                  |
|  +-------------------+   +-------------------+                   |
|  | FCM Push Notify   |   | WebSocket (live)  |                   |
|  | (to owner phone)  |   | (to dashboard)    |                   |
|  +-------------------+   +-------------------+                   |
|                                                                  |
|  +-------------------+   +-------------------+                   |
|  | MQTT Two-Way      |   | Alert Log         |                   |
|  | (to old devices)  |   | (SQLite persist)  |                   |
|  +-------------------+   +-------------------+                   |
+------------------------------------------------------------------+
```

---

## 5. Backend Directory Structure

```
backend/
|-- main.py                      # FastAPI application entry point
|-- config.py                    # Environment variable loading and validation
|-- database.py                  # SQLite connection, schema init, migrations
|-- models.py                    # Pydantic schemas for all request/response types
|-- auth.py                      # JWT authentication (old_device / new_device roles)
|-- mqtt_client.py               # MQTT connection, subscription, message routing
|-- websocket_manager.py         # WebSocket connection manager (both portal types)
|-- requirements.txt             # Pinned Python dependencies
|
|-- routers/
|   |-- auth_routes.py           # Login, register, token refresh endpoints
|   |-- sensor_routes.py         # Sensor node CRUD, heartbeat, health
|   |-- stream_routes.py         # Video stream relay, frame endpoints
|   |-- anomaly_routes.py        # Anomaly events, risk scores, history
|   |-- alert_routes.py          # Alert management, acknowledgment
|   |-- clip_routes.py           # Clip retrieval, metadata, download
|   |-- narrative_routes.py      # AI narrative generation, retrieval
|   |-- dashboard_routes.py      # Dashboard aggregation endpoints
|   |-- communication_routes.py  # Two-way messaging endpoints
|   |-- prediction_routes.py     # Prediction engine endpoints
|   |-- demo_routes.py           # Demo mode scenario control
|
|-- services/
|   |-- baseline_service.py      # Behavioral baseline builder (7-14 day)
|   |-- yolo_service.py          # YOLO inference runner
|   |-- anomaly_service.py       # Isolation Forest anomaly detection
|   |-- fusion_service.py        # Multi-sensor fusion engine
|   |-- risk_service.py          # Dynamic risk score calculator
|   |-- clip_service.py          # Smart clip extraction engine
|   |-- narrative_service.py     # Claude API integration + fallback
|   |-- alert_service.py         # Alert construction and delivery (FCM)
|   |-- communication_service.py # Two-way communication relay
|   |-- prediction_service.py    # Adaptive prediction engine
|   |-- demo_service.py          # Demo scenario data and simulation
|
|-- utils/
|   |-- ring_buffer.py           # Ring buffer for pre-anomaly frames
|   |-- frame_processor.py       # Frame resize, normalize, format convert
|   |-- video_encoder.py         # MP4 encoding with timestamp overlay
|   |-- mqtt_topics.py           # MQTT topic constants and helpers
|   |-- security.py              # Input sanitization, validation helpers
```

---

## 6. Frontend Directory Structure

```
frontend/
|-- index.html                   # HTML entry point
|-- vite.config.js               # Vite configuration
|-- tailwind.config.js           # TailwindCSS configuration with custom tokens
|-- postcss.config.js            # PostCSS configuration
|-- package.json                 # NPM dependencies
|
|-- public/
|   |-- favicon.ico              # App favicon
|   |-- demo/                    # Pre-loaded demo assets (clips, images)
|
|-- src/
|   |-- main.jsx                 # React entry point
|   |-- App.jsx                  # Root component with router
|   |-- index.css                # Global CSS with custom properties
|
|   |-- contexts/
|   |   |-- ThemeContext.jsx      # Theme provider (light/dark, localStorage)
|   |   |-- AuthContext.jsx       # Auth provider (JWT, role-based)
|   |   |-- WebSocketContext.jsx  # WebSocket connection provider
|
|   |-- stores/
|   |   |-- useAlertStore.js      # Zustand store for alerts
|   |   |-- useSensorStore.js     # Zustand store for sensor nodes
|   |   |-- useDashboardStore.js  # Zustand store for dashboard state
|
|   |-- hooks/
|   |   |-- useWebSocket.js       # WebSocket connection hook
|   |   |-- useAuth.js            # Auth hook (login, logout, role check)
|   |   |-- useSensors.js         # Sensor data fetching hook
|   |   |-- useAlerts.js          # Alert data fetching hook
|
|   |-- components/
|   |   |-- layout/
|   |   |   |-- AppShell.jsx      # Global layout wrapper
|   |   |   |-- NavBar.jsx        # Navigation bar
|   |   |   |-- Sidebar.jsx       # Dashboard sidebar navigation
|   |   |   |-- ThemeToggle.jsx   # Light/dark theme toggle button
|   |   |   |-- NotificationBadge.jsx  # Notification count badge
|   |   |
|   |   |-- shared/
|   |   |   |-- StatusBadge.jsx   # Active/Learning/Alert status badge
|   |   |   |-- RiskBadge.jsx     # Low/Medium/High/Critical risk badge
|   |   |   |-- LoadingSpinner.jsx # Loading state indicator
|   |   |   |-- EmptyState.jsx    # Empty state placeholder
|   |   |
|   |   |-- old-device/
|   |   |   |-- CameraPreview.jsx  # Live camera preview with status
|   |   |   |-- BaselineProgress.jsx # Baseline learning progress bar
|   |   |   |-- DeviceStatus.jsx   # Connection health monitor
|   |   |   |-- AudioWarning.jsx   # Audio warning playback component
|   |   |
|   |   |-- dashboard/
|   |   |   |-- LiveFeedGrid.jsx   # Multi-camera view with AI overlay
|   |   |   |-- FloorPlan.jsx      # Interactive SVG floor plan
|   |   |   |-- HeatZone.jsx       # Real-time activity heat zone
|   |   |   |-- AlertFeed.jsx      # Real-time alert feed panel
|   |   |   |-- AlertCard.jsx      # Individual alert card
|   |   |   |-- RiskGauge.jsx      # Animated arc gauge for risk score
|   |   |   |-- NarrativeModal.jsx # AI incident narrative modal
|   |   |   |-- ClipPlayer.jsx     # Video clip player
|   |   |   |-- SensorHealth.jsx   # Sensor node health panel
|   |   |   |-- CommPanel.jsx      # Two-way communication panel
|   |   |   |-- WatchlistConfig.jsx # Watchlist configuration panel
|   |   |   |-- TimelineReplay.jsx # AI reasoning timeline (F11)
|
|   |-- pages/
|   |   |-- OldDeviceLogin.jsx    # Old device login page
|   |   |-- OldDevicePortal.jsx   # Old device main portal
|   |   |-- NewDeviceLogin.jsx    # New device owner login page
|   |   |-- NewDeviceDashboard.jsx # New device full dashboard
|   |   |-- DemoPage.jsx          # Demo mode controller page
```

---

## 7. Database Schema

```sql
-- Sensor Nodes: All enrolled devices (old phones, webcams, CCTV)
CREATE TABLE sensor_nodes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('phone', 'webcam', 'cctv')),
    location_zone TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'inactive' CHECK(status IN ('active', 'inactive', 'learning', 'alert')),
    last_heartbeat DATETIME,
    enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);
CREATE INDEX idx_sensor_nodes_owner ON sensor_nodes(owner_id);
CREATE INDEX idx_sensor_nodes_status ON sensor_nodes(status);

-- Behavioral Baseline Profiles: Per-zone, per-hour activity distributions
CREATE TABLE baseline_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_node_id TEXT NOT NULL,
    zone TEXT NOT NULL,
    hour_of_day INTEGER NOT NULL CHECK(hour_of_day >= 0 AND hour_of_day <= 23),
    day_of_week INTEGER NOT NULL CHECK(day_of_week >= 0 AND day_of_week <= 6),
    activity_probability REAL NOT NULL DEFAULT 0.0,
    avg_movement_speed REAL DEFAULT 0.0,
    trajectory_cluster_centroids TEXT,  -- JSON array of centroid coordinates
    sample_count INTEGER NOT NULL DEFAULT 0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_node_id) REFERENCES sensor_nodes(id)
);
CREATE INDEX idx_baseline_zone_hour ON baseline_profiles(zone, hour_of_day, day_of_week);

-- Anomaly Events: Every detected anomaly with full context
CREATE TABLE anomaly_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_node_ids TEXT NOT NULL,  -- Comma-separated sensor node IDs
    zone TEXT NOT NULL,
    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    anomaly_score REAL NOT NULL,
    risk_level TEXT NOT NULL CHECK(risk_level IN ('low', 'medium', 'high', 'critical')),
    classification TEXT,
    baseline_deviation REAL,
    duration_seconds REAL,
    clip_path TEXT,
    narrative_text TEXT,
    acknowledged INTEGER NOT NULL DEFAULT 0,
    acknowledged_at DATETIME,
    acknowledged_by TEXT
);
CREATE INDEX idx_anomaly_detected_at ON anomaly_events(detected_at);
CREATE INDEX idx_anomaly_risk_level ON anomaly_events(risk_level);

-- Alerts: Delivery tracking for all sent alerts
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anomaly_event_id INTEGER NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    channel TEXT NOT NULL CHECK(channel IN ('push', 'audio', 'log')),
    delivery_status TEXT NOT NULL DEFAULT 'pending' CHECK(delivery_status IN ('pending', 'sent', 'delivered', 'failed')),
    fcm_message_id TEXT,
    FOREIGN KEY (anomaly_event_id) REFERENCES anomaly_events(id)
);
CREATE INDEX idx_alerts_anomaly ON alerts(anomaly_event_id);

-- Users: Both old device and new device users
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    role TEXT NOT NULL CHECK(role IN ('old_device', 'new_device')),
    device_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    fcm_token TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_users_role ON users(role);

-- Scenario Library: Intrusion scenario definitions (F11)
CREATE TABLE scenario_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    phase_count INTEGER NOT NULL,
    phase_definitions_json TEXT NOT NULL,  -- JSON array of phase objects
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Prediction Events: Matched scenario predictions (F11)
CREATE TABLE prediction_events (
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
CREATE INDEX idx_prediction_detected ON prediction_events(detected_at);
```

---

## 8. API Endpoints

| Method | Path                                  | Description                                    | Response                    |
| ------ | ------------------------------------- | ---------------------------------------------- | --------------------------- |
| POST   | /api/auth/register                    | Register new user (old_device or new_device)   | { token, user }             |
| POST   | /api/auth/login                       | Authenticate and get JWT token                 | { token, role, expires }    |
| POST   | /api/auth/refresh                     | Refresh JWT token                              | { token, expires }          |
| GET    | /api/sensors                          | List all sensor nodes for current owner        | [ SensorNode ]              |
| POST   | /api/sensors                          | Register a new sensor node                     | SensorNode                  |
| GET    | /api/sensors/{id}                     | Get sensor node details                        | SensorNode                  |
| PUT    | /api/sensors/{id}/heartbeat           | Update sensor heartbeat                        | { status }                  |
| GET    | /api/sensors/{id}/health              | Get sensor health status                       | SensorHealth                |
| GET    | /api/stream/{sensor_id}               | Get live video stream (MJPEG)                  | Stream                      |
| GET    | /api/baseline/status                  | Get baseline learning progress                 | BaselineStatus              |
| GET    | /api/baseline/profile/{zone}          | Get behavioral profile for zone                | BaselineProfile             |
| GET    | /api/anomalies                        | List anomaly events (with filters)             | [ AnomalyEvent ]            |
| GET    | /api/anomalies/{id}                   | Get anomaly event details                      | AnomalyEvent                |
| PUT    | /api/anomalies/{id}/acknowledge       | Acknowledge an anomaly event                   | { status }                  |
| GET    | /api/alerts                           | List alerts (with filters)                     | [ Alert ]                   |
| GET    | /api/clips/{anomaly_id}               | Get clip for anomaly event                     | ClipMetadata + URL          |
| GET    | /api/clips/{anomaly_id}/download      | Download clip MP4 file                         | Binary MP4                  |
| GET    | /api/narratives/{anomaly_id}          | Get AI narrative for anomaly                   | NarrativeResponse           |
| POST   | /api/narratives/{anomaly_id}/generate | Generate narrative (trigger Claude)            | NarrativeResponse           |
| GET    | /api/dashboard/summary                | Dashboard aggregated stats                     | DashboardSummary            |
| GET    | /api/dashboard/heatmap/{zone}         | Get heat zone data for floor plan              | HeatmapData                 |
| POST   | /api/communicate/send                 | Send message to old device                     | { status, message_id }      |
| GET    | /api/risk/current                     | Get current system-wide risk score             | RiskScore                   |
| GET    | /api/risk/{anomaly_id}                | Get risk score for specific anomaly            | RiskScore                   |
| GET    | /api/predictions                      | List active prediction events (F11)            | [ PredictionEvent ]         |
| GET    | /api/predictions/{id}/timeline        | Get AI reasoning timeline for prediction       | ReasoningTimeline           |
| POST   | /api/demo/start/{scenario}            | Start demo scenario simulation                 | { status, scenario }        |
| POST   | /api/demo/stop                        | Stop active demo simulation                    | { status }                  |
| GET    | /api/demo/scenarios                   | List available demo scenarios                  | [ Scenario ]                |
| GET    | /api/health                           | System health check                            | { status, services }        |
| WS     | /ws/old-device/{device_id}            | WebSocket for old device communication         | Bidirectional               |
| WS     | /ws/dashboard/{user_id}               | WebSocket for dashboard real-time updates      | Bidirectional               |

---

## 9. WebSocket Message Types

### sensor_frame
```json
{
  "type": "sensor_frame",
  "sensor_id": "phone-001",
  "timestamp": "2026-04-11T02:43:12Z",
  "frame_data": "<base64_encoded_jpeg>",
  "resolution": [640, 480],
  "fps": 15
}
```

### anomaly_detected
```json
{
  "type": "anomaly_detected",
  "anomaly_id": 42,
  "sensor_ids": ["phone-001", "webcam-003"],
  "zone": "living_room",
  "timestamp": "2026-04-11T02:43:12Z",
  "anomaly_score": 0.87,
  "risk_level": "high",
  "classification": "unfamiliar_movement_pattern",
  "baseline_deviation": 3.2,
  "clip_available": true
}
```

### risk_score_update
```json
{
  "type": "risk_score_update",
  "anomaly_id": 42,
  "previous_score": 62,
  "current_score": 78,
  "risk_level": "critical",
  "factors": {
    "baseline_deviation": 0.92,
    "time_of_day_risk": 0.85,
    "zone_sensitivity": 0.70,
    "event_duration": 0.45,
    "multi_sensor_confirmation": 1.0
  },
  "trend": "escalating",
  "timestamp": "2026-04-11T02:43:59Z"
}
```

### alert_fired
```json
{
  "type": "alert_fired",
  "alert_id": 15,
  "anomaly_id": 42,
  "risk_level": "critical",
  "zone": "living_room",
  "timestamp": "2026-04-11T02:44:01Z",
  "channels": ["push", "audio"],
  "reasoning_summary": "Unusual movement in living room at 2:43 AM; zero baseline activity expected; persisted 47 seconds across 2 sensors.",
  "clip_thumbnail": "/api/clips/42/thumbnail",
  "recommended_actions": ["Verify household members are safe", "Check attached clip", "Consider contacting authorities"]
}
```

### clip_ready
```json
{
  "type": "clip_ready",
  "anomaly_id": 42,
  "clip_path": "/clips/anomaly_42_20260411_024312.mp4",
  "duration_seconds": 15.2,
  "pre_event_seconds": 5.0,
  "post_event_seconds": 10.2,
  "thumbnail_url": "/api/clips/42/thumbnail",
  "timestamp": "2026-04-11T02:44:05Z"
}
```

### narrative_ready
```json
{
  "type": "narrative_ready",
  "anomaly_id": 42,
  "narrative_text": "At 2:43 AM, unusual movement was detected in the living room. This zone typically shows zero activity between midnight and 6 AM based on 14 days of baseline data. The detected movement trajectory does not match any household member's known pattern. The event persisted for 47 seconds across two sensor nodes, confirming it is not a false positive. Risk assessment: High. Recommended action: verify household members are safe and check the attached clip.",
  "generated_by": "claude",
  "timestamp": "2026-04-11T02:44:08Z"
}
```

### system_status
```json
{
  "type": "system_status",
  "active_sensors": 3,
  "total_sensors": 4,
  "system_mode": "monitoring",
  "baseline_status": "complete",
  "current_risk": 12,
  "risk_level": "low",
  "uptime_hours": 342,
  "last_anomaly": "2026-04-11T02:44:01Z",
  "mqtt_connected": true,
  "timestamp": "2026-04-11T03:00:00Z"
}
```

### baseline_progress
```json
{
  "type": "baseline_progress",
  "sensor_id": "phone-001",
  "zone": "living_room",
  "days_complete": 5,
  "days_required": 14,
  "percent_complete": 35.7,
  "zones_learning": ["living_room", "kitchen", "hallway", "front_door"],
  "sample_counts": { "living_room": 4320, "kitchen": 3890, "hallway": 2100, "front_door": 1560 },
  "estimated_completion": "2026-04-17T00:00:00Z",
  "timestamp": "2026-04-11T06:00:00Z"
}
```

---

## 10. Design System

### Color Tokens

```css
/* --- DARK THEME (default) --- */
:root {
  /* Backgrounds */
  --bg-primary: #08090f;
  --bg-secondary: #0f1119;
  --bg-tertiary: #161822;
  --bg-surface: rgba(255, 255, 255, 0.03);
  --bg-glass: rgba(255, 255, 255, 0.05);
  --bg-glass-hover: rgba(255, 255, 255, 0.08);

  /* Text */
  --text-primary: #f0f0f5;
  --text-secondary: #8b8fa3;
  --text-tertiary: #555870;
  --text-inverse: #08090f;

  /* Accents */
  --accent-blue: #3b82f6;
  --accent-blue-glow: rgba(59, 130, 246, 0.3);
  --accent-violet: #8b5cf6;
  --accent-violet-glow: rgba(139, 92, 246, 0.3);
  --accent-emerald: #10b981;
  --accent-emerald-glow: rgba(16, 185, 129, 0.3);
  --accent-amber: #f59e0b;
  --accent-amber-glow: rgba(245, 158, 11, 0.3);
  --accent-red: #ef4444;
  --accent-red-glow: rgba(239, 68, 68, 0.3);

  /* Borders */
  --border-primary: rgba(255, 255, 255, 0.06);
  --border-secondary: rgba(255, 255, 255, 0.10);
  --border-accent: rgba(59, 130, 246, 0.3);

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
  --shadow-glow-blue: 0 0 20px rgba(59, 130, 246, 0.2);
  --shadow-glow-violet: 0 0 20px rgba(139, 92, 246, 0.2);
  --shadow-glow-emerald: 0 0 20px rgba(16, 185, 129, 0.2);
  --shadow-glow-red: 0 0 20px rgba(239, 68, 68, 0.3);
}

/* --- LIGHT THEME --- */
[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f8f9fc;
  --bg-tertiary: #f0f1f5;
  --bg-surface: rgba(0, 0, 0, 0.02);
  --bg-glass: rgba(255, 255, 255, 0.80);
  --bg-glass-hover: rgba(255, 255, 255, 0.90);

  --text-primary: #111827;
  --text-secondary: #6b7280;
  --text-tertiary: #9ca3af;
  --text-inverse: #ffffff;

  --accent-blue: #2563eb;
  --accent-violet: #7c3aed;
  --accent-emerald: #059669;
  --accent-amber: #d97706;
  --accent-red: #dc2626;

  --border-primary: rgba(0, 0, 0, 0.06);
  --border-secondary: rgba(0, 0, 0, 0.10);
  --border-accent: rgba(37, 99, 235, 0.3);

  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.12);
  --shadow-glow-blue: 0 0 20px rgba(37, 99, 235, 0.1);
  --shadow-glow-violet: 0 0 20px rgba(124, 58, 237, 0.1);
  --shadow-glow-emerald: 0 0 20px rgba(5, 150, 105, 0.1);
  --shadow-glow-red: 0 0 20px rgba(220, 38, 38, 0.15);
}
```

### Typography

```css
:root {
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */
  --text-5xl: 3rem;      /* 48px */

  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### Spacing

```css
:root {
  --space-1: 0.25rem;    /* 4px */
  --space-2: 0.5rem;     /* 8px */
  --space-3: 0.75rem;    /* 12px */
  --space-4: 1rem;       /* 16px */
  --space-5: 1.25rem;    /* 20px */
  --space-6: 1.5rem;     /* 24px */
  --space-8: 2rem;       /* 32px */
  --space-10: 2.5rem;    /* 40px */
  --space-12: 3rem;      /* 48px */
  --space-16: 4rem;      /* 64px */
  --space-20: 5rem;      /* 80px */
  --space-24: 6rem;      /* 96px */
}
```

### Borders and Radii

```css
:root {
  --radius-sm: 0.375rem;   /* 6px */
  --radius-md: 0.5rem;     /* 8px */
  --radius-lg: 0.75rem;    /* 12px */
  --radius-xl: 1rem;       /* 16px */
  --radius-2xl: 1.5rem;    /* 24px */
  --radius-full: 9999px;
}
```

### Animations

```css
:root {
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
  --duration-slower: 600ms;

  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

---

## 11. Demo Strategy

### Pre-loaded Scenarios

| ID | Scenario Name             | Duration | Key Events                                                       | Risk Level Reached |
| -- | ------------------------- | -------- | ---------------------------------------------------------------- | ------------------ |
| A  | Normal Morning Routine    | 60s      | Baseline complete, owner leaves 8 AM, kitchen/living activity    | Low (12)           |
| B  | Late Night Anomaly        | 45s      | 2:43 AM living room motion, no match, clip generated, narrative  | High (78)          |
| C  | Casing Simulation         | 90s      | Perimeter passes, watch flag, escalation, 73% casing match       | Medium (58)        |
| D  | Full Intrusion Prediction | 120s     | 4-phase: casing, entry probing, Critical before intrusion phase  | Critical (92)      |

### Demo Mode Behavior

- All scenarios use synthetic sensor data injected via the demo service
- No external API calls required (Claude narratives use pre-written fallbacks)
- WebSocket events are simulated with realistic timing
- Risk scores escalate dynamically on screen
- Clips are pre-rendered MP4 files in `/public/demo/`
- Floor plan heat zones update in real time with simulated data

---

## 12. Security Measures

1. All API keys loaded from environment variables, never hardcoded
2. JWT authentication with short expiry (15 min access, 7 day refresh)
3. Role-based access control (old_device vs new_device)
4. Rate limiting on all endpoints via slowapi
5. CORS with strict origin whitelist
6. CSP headers on all responses
7. All SQL queries use parameterized statements
8. MQTT topic access control per device
9. WebSocket authentication on handshake
10. Input sanitization on all user inputs
11. No stack traces in production error responses
12. File upload validation for demo scenarios
13. Pinned dependency versions with audit checks
14. Secrets never logged, even at debug level

---

## 13. Build Priority Table

| Priority | Phase                          | What It Unlocks                                   | Demo Ready? |
| -------- | ------------------------------ | ------------------------------------------------- | ----------- |
| P0       | Manifest + Setup (Chunk 0-1)   | Project skeleton, dependencies, environment       | No          |
| P1       | Backend Core (Chunk 2)         | API server, database, auth, WebSocket             | No          |
| P2       | Sensor Pipeline (Chunk 3)      | Video ingestion, MQTT messaging, streaming        | No          |
| P3       | Frontend Shell (Chunk 6)       | React app, design system, routing                 | Partial     |
| P4       | ML + Anomaly (Chunk 4)         | Baseline learning, YOLO, anomaly detection        | Partial     |
| P5       | Intelligence Layer (Chunk 5)   | Clip extraction, Claude narratives, alerts        | Yes (basic) |
| P6       | Both Portals (Chunk 7-8)       | Complete Old Device + Dashboard UI                | Yes (full)  |
| P7       | Secret Weapon + Deploy (Chunk 9)| Prediction engine, security hardening, Docker     | Yes (demo)  |

---

## 14. API Key Access Instructions

### Claude API (Anthropic)
1. Visit https://console.anthropic.com/
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new key and copy it
5. Set `CLAUDE_API_KEY=sk-ant-...` in your `.env` file

### Firebase Cloud Messaging
1. Visit https://console.firebase.google.com/
2. Create a new project (or use existing)
3. Go to Project Settings > Cloud Messaging
4. Generate a Server Key
5. Download the service account JSON file
6. Set `FCM_SERVER_KEY=...` in your `.env` file
7. Place the JSON file at `backend/firebase-credentials.json`

### MQTT (Eclipse Mosquitto)
- No API key needed — self-hosted
- Install via Docker: `docker run -p 1883:1883 eclipse-mosquitto`
- Or install locally: `brew install mosquitto` (macOS)

### YOLO (Ultralytics)
- No API key needed — local inference
- Model downloads automatically on first use via `ultralytics` pip package
- Or manually download: `yolo export model=yolov8n.pt`

---

## 15. Judge Pitch Lines

1. "We don't detect motion — we detect intent."
2. "Your old devices become your AI security network."
3. "Security is not about cameras — it is about understanding."
4. "Every alert comes with a clip, a reason, and a recommendation."
5. "We catch intrusions during the casing phase — before they start."
6. "14 days of learning. Zero hardware cost. Infinite behavioral intelligence."
7. "HomeGuardian AI: the AI that knows your home better than a stranger ever could."
