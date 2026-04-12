# Chunk 03 — Sensor Data Pipeline

**Goal**: Build MQTT message ingestion, video frame buffering, ring buffer, sensor health tracking, frame preprocessing, and streaming endpoints.
**Estimated Time**: 40 minutes
**Dependencies**: Chunk 02 (Backend Core)
**Unlocks**: Chunk 04 (ML and Anomaly Detection)

---

## 03.1 — Ring Buffer (backend/utils/ring_buffer.py)

```python
"""
HomeGuardian AI — Ring Buffer
Circular buffer for storing pre-anomaly context frames.
"""

import threading
from collections import deque
from typing import Any, List, Optional
from datetime import datetime


class RingBuffer:
    """Thread-safe circular buffer for frame storage."""

    def __init__(self, capacity: int = 150):
        """
        Initialize ring buffer.
        Args:
            capacity: Maximum number of frames to store.
                      At 15fps and 5 seconds pre-event = 75 frames.
                      Default 150 for safety margin.
        """
        self._buffer: deque = deque(maxlen=capacity)
        self._lock = threading.Lock()
        self.capacity = capacity

    def push(self, frame_data: dict):
        """Add a frame to the buffer."""
        with self._lock:
            self._buffer.append({
                "data": frame_data,
                "timestamp": datetime.utcnow().isoformat()
            })

    def get_all(self) -> List[dict]:
        """Get all frames currently in the buffer."""
        with self._lock:
            return list(self._buffer)

    def get_last_n(self, n: int) -> List[dict]:
        """Get the last N frames from the buffer."""
        with self._lock:
            items = list(self._buffer)
            return items[-n:] if len(items) >= n else items

    def get_last_seconds(self, seconds: float, fps: int = 15) -> List[dict]:
        """Get frames from the last N seconds."""
        n_frames = int(seconds * fps)
        return self.get_last_n(n_frames)

    def clear(self):
        """Clear all frames from the buffer."""
        with self._lock:
            self._buffer.clear()

    @property
    def size(self) -> int:
        """Current number of frames in the buffer."""
        with self._lock:
            return len(self._buffer)

    @property
    def is_full(self) -> bool:
        """Whether the buffer is at capacity."""
        return self.size >= self.capacity


class MultiSensorRingBuffer:
    """Manages individual ring buffers for each sensor node."""

    def __init__(self, capacity_per_sensor: int = 150):
        self._buffers: dict = {}
        self._capacity = capacity_per_sensor
        self._lock = threading.Lock()

    def get_buffer(self, sensor_id: str) -> RingBuffer:
        """Get or create a ring buffer for a sensor."""
        with self._lock:
            if sensor_id not in self._buffers:
                self._buffers[sensor_id] = RingBuffer(self._capacity)
            return self._buffers[sensor_id]

    def push_frame(self, sensor_id: str, frame_data: dict):
        """Push a frame to a sensor's ring buffer."""
        buffer = self.get_buffer(sensor_id)
        buffer.push(frame_data)

    def get_pre_event_frames(self, sensor_id: str, seconds: float, fps: int = 15) -> List[dict]:
        """Get pre-event frames from a sensor's buffer."""
        buffer = self.get_buffer(sensor_id)
        return buffer.get_last_seconds(seconds, fps)

    def remove_sensor(self, sensor_id: str):
        """Remove a sensor's buffer."""
        with self._lock:
            self._buffers.pop(sensor_id, None)
```

---

## 03.2 — Frame Processor (backend/utils/frame_processor.py)

```python
"""
HomeGuardian AI — Frame Processor
Frame preprocessing pipeline: resize, normalize, format conversion.
"""

import base64
import io
import logging
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger("homeguardian.frame_processor")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available. Frame processing will use fallback mode.")


class FrameProcessor:
    """Processes raw video frames for YOLO inference and storage."""

    # YOLO input dimensions
    YOLO_INPUT_SIZE = (640, 640)
    # Standard frame size for storage
    STORAGE_SIZE = (640, 480)

    @staticmethod
    def decode_base64_frame(base64_data: str) -> Optional[np.ndarray]:
        """Decode a base64-encoded JPEG frame into a numpy array."""
        if not CV2_AVAILABLE:
            return None
        try:
            img_bytes = base64.b64decode(base64_data)
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        except Exception as e:
            logger.error(f"Failed to decode frame: {e}")
            return None

    @staticmethod
    def encode_frame_base64(frame: np.ndarray, quality: int = 85) -> str:
        """Encode a numpy frame to base64 JPEG."""
        if not CV2_AVAILABLE:
            return ""
        try:
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
            _, buffer = cv2.imencode('.jpg', frame, encode_params)
            return base64.b64encode(buffer).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode frame: {e}")
            return ""

    @staticmethod
    def resize_for_yolo(frame: np.ndarray) -> np.ndarray:
        """Resize frame to YOLO input dimensions."""
        if not CV2_AVAILABLE:
            return frame
        return cv2.resize(frame, FrameProcessor.YOLO_INPUT_SIZE)

    @staticmethod
    def resize_for_storage(frame: np.ndarray) -> np.ndarray:
        """Resize frame to standard storage dimensions."""
        if not CV2_AVAILABLE:
            return frame
        return cv2.resize(frame, FrameProcessor.STORAGE_SIZE)

    @staticmethod
    def normalize(frame: np.ndarray) -> np.ndarray:
        """Normalize pixel values to 0-1 range for ML inference."""
        return frame.astype(np.float32) / 255.0

    @staticmethod
    def preprocess_for_yolo(frame: np.ndarray) -> np.ndarray:
        """Full preprocessing pipeline for YOLO input."""
        # Resize
        resized = FrameProcessor.resize_for_yolo(frame)
        # Convert BGR to RGB (YOLO expects RGB)
        if CV2_AVAILABLE:
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        else:
            rgb = resized
        # Normalize
        normalized = FrameProcessor.normalize(rgb)
        return normalized

    @staticmethod
    def add_timestamp_overlay(frame: np.ndarray, timestamp: str) -> np.ndarray:
        """Add a timestamp text overlay to a frame."""
        if not CV2_AVAILABLE:
            return frame
        overlay = frame.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (255, 255, 255)
        thickness = 1

        # Background rectangle for readability
        text_size = cv2.getTextSize(timestamp, font, font_scale, thickness)[0]
        x, y = 10, frame.shape[0] - 10
        cv2.rectangle(overlay, (x - 2, y - text_size[1] - 4), (x + text_size[0] + 2, y + 4), (0, 0, 0), -1)
        cv2.putText(overlay, timestamp, (x, y), font, font_scale, color, thickness)
        return overlay

    @staticmethod
    def compute_motion_diff(frame1: np.ndarray, frame2: np.ndarray, threshold: int = 25) -> Tuple[float, np.ndarray]:
        """
        Compute motion difference between two frames.
        Returns: (motion_score, diff_mask)
        """
        if not CV2_AVAILABLE:
            return 0.0, np.zeros((1,))

        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Gaussian blur to reduce noise
        gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
        gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)

        diff = cv2.absdiff(gray1, gray2)
        _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

        motion_score = np.sum(thresh > 0) / thresh.size
        return motion_score, thresh
```

---

## 03.3 — MQTT Topics Helper (backend/utils/mqtt_topics.py)

```python
"""
HomeGuardian AI — MQTT Topic Helpers
Topic constants and parsing utilities.
"""


class MQTTTopics:
    """MQTT topic namespace and utilities."""

    # Base namespace
    BASE = "homeguardian"

    # Sensor topics (published by old devices)
    SENSOR_FRAME_PATTERN = "homeguardian/sensors/+/frame"
    SENSOR_HEARTBEAT_PATTERN = "homeguardian/sensors/+/heartbeat"
    SENSOR_STATUS_PATTERN = "homeguardian/sensors/+/status"
    SENSOR_AUDIO_PATTERN = "homeguardian/sensors/+/audio"

    # Command topics (published by hub to old devices)
    COMMAND_PATTERN = "homeguardian/commands/+"

    # Alert topics
    ALERT_BROADCAST = "homeguardian/alerts/broadcast"

    # System topics
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
    def sensor_audio(device_id: str) -> str:
        return f"homeguardian/sensors/{device_id}/audio"

    @staticmethod
    def command_to_device(device_id: str) -> str:
        return f"homeguardian/commands/{device_id}"

    @staticmethod
    def extract_device_id(topic: str) -> str:
        """Extract the device ID from a sensor topic."""
        parts = topic.split("/")
        if len(parts) >= 3 and parts[0] == "homeguardian" and parts[1] == "sensors":
            return parts[2]
        if len(parts) >= 3 and parts[0] == "homeguardian" and parts[1] == "commands":
            return parts[2]
        return ""

    @staticmethod
    def extract_message_type(topic: str) -> str:
        """Extract the message type from a topic."""
        parts = topic.split("/")
        if len(parts) >= 4:
            return parts[3]
        return ""
```

---

## 03.4 — Sensor Pipeline Service (backend/services/sensor_pipeline.py)

```python
"""
HomeGuardian AI — Sensor Data Pipeline
Handles MQTT message ingestion, frame buffering, and health tracking.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional

from utils.ring_buffer import MultiSensorRingBuffer
from utils.frame_processor import FrameProcessor
from utils.mqtt_topics import MQTTTopics
from database import get_db

logger = logging.getLogger("homeguardian.sensor_pipeline")


class SensorPipeline:
    """Central pipeline for processing incoming sensor data."""

    def __init__(self):
        self.ring_buffers = MultiSensorRingBuffer(capacity_per_sensor=150)
        self.frame_processor = FrameProcessor()
        self._frame_queues: Dict[str, asyncio.Queue] = {}
        self._active_streams: set = set()
        self._frame_counts: Dict[str, int] = {}
        self._last_frame_time: Dict[str, datetime] = {}

    def process_sensor_frame(self, topic: str, payload: dict):
        """
        Process an incoming sensor frame from MQTT.
        Called by MQTT message handler.
        """
        device_id = MQTTTopics.extract_device_id(topic)
        if not device_id:
            logger.warning(f"Could not extract device_id from topic: {topic}")
            return

        # Update frame tracking
        self._frame_counts[device_id] = self._frame_counts.get(device_id, 0) + 1
        self._last_frame_time[device_id] = datetime.utcnow()

        # Store in ring buffer for pre-event context
        self.ring_buffers.push_frame(device_id, {
            "frame_data": payload.get("frame_data", ""),
            "timestamp": payload.get("timestamp", datetime.utcnow().isoformat()),
            "resolution": payload.get("resolution", [640, 480])
        })

        # Push to frame queue for real-time processing (YOLO, etc.)
        if device_id in self._frame_queues:
            try:
                self._frame_queues[device_id].put_nowait(payload)
            except asyncio.QueueFull:
                # Drop oldest frame if queue is full
                try:
                    self._frame_queues[device_id].get_nowait()
                    self._frame_queues[device_id].put_nowait(payload)
                except asyncio.QueueEmpty:
                    pass

        logger.debug(f"Frame {self._frame_counts[device_id]} from {device_id}")

    def process_heartbeat(self, topic: str, payload: dict):
        """Process a heartbeat message from a sensor node."""
        device_id = MQTTTopics.extract_device_id(topic)
        if not device_id:
            return

        try:
            with get_db() as conn:
                conn.execute(
                    "UPDATE sensor_nodes SET last_heartbeat = ?, status = 'active' WHERE id = ?",
                    (datetime.utcnow().isoformat(), device_id)
                )
            logger.debug(f"Heartbeat from {device_id}")
        except Exception as e:
            logger.error(f"Failed to process heartbeat for {device_id}: {e}")

    def process_status_update(self, topic: str, payload: dict):
        """Process a status update from a sensor node."""
        device_id = MQTTTopics.extract_device_id(topic)
        if not device_id:
            return

        new_status = payload.get("status", "active")
        try:
            with get_db() as conn:
                conn.execute(
                    "UPDATE sensor_nodes SET status = ? WHERE id = ?",
                    (new_status, device_id)
                )
            logger.info(f"Status update from {device_id}: {new_status}")
        except Exception as e:
            logger.error(f"Failed to process status for {device_id}: {e}")

    def register_frame_queue(self, device_id: str) -> asyncio.Queue:
        """Register a frame queue for real-time processing."""
        if device_id not in self._frame_queues:
            self._frame_queues[device_id] = asyncio.Queue(maxsize=30)
        return self._frame_queues[device_id]

    def unregister_frame_queue(self, device_id: str):
        """Remove a frame queue."""
        self._frame_queues.pop(device_id, None)

    def get_pre_event_frames(self, sensor_id: str, seconds: float = 5.0) -> list:
        """Get pre-event frames from the ring buffer."""
        return self.ring_buffers.get_pre_event_frames(sensor_id, seconds)

    def get_sensor_stats(self, sensor_id: str) -> dict:
        """Get processing statistics for a sensor."""
        return {
            "sensor_id": sensor_id,
            "total_frames": self._frame_counts.get(sensor_id, 0),
            "buffer_size": self.ring_buffers.get_buffer(sensor_id).size,
            "last_frame": self._last_frame_time.get(sensor_id, None),
            "queue_active": sensor_id in self._frame_queues
        }


# Singleton instance
sensor_pipeline = SensorPipeline()
```

---

## 03.5 — Stream Routes (backend/routers/stream_routes.py)

```python
"""
HomeGuardian AI — Video Stream Routes
Endpoints for live video streaming and frame relay.
"""

import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from auth import get_current_user
from services.sensor_pipeline import sensor_pipeline
from database import get_db

logger = logging.getLogger("homeguardian.stream")

router = APIRouter()


@router.get("/{sensor_id}")
async def get_live_stream(sensor_id: str, user: dict = Depends(get_current_user)):
    """
    Get live video stream from a sensor node (MJPEG format).
    Streams frames as multipart JPEG for browser compatibility.
    """
    # Verify sensor exists
    with get_db() as conn:
        sensor = conn.execute(
            "SELECT * FROM sensor_nodes WHERE id = ?", (sensor_id,)
        ).fetchone()

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor node not found")

    async def frame_generator():
        """Generate MJPEG stream from frame queue."""
        queue = sensor_pipeline.register_frame_queue(sensor_id)
        try:
            while True:
                try:
                    frame_data = await asyncio.wait_for(queue.get(), timeout=10.0)
                    frame_b64 = frame_data.get("frame_data", "")
                    if frame_b64:
                        import base64
                        frame_bytes = base64.b64decode(frame_b64)
                        yield (
                            b"--frame\r\n"
                            b"Content-Type: image/jpeg\r\n\r\n"
                            + frame_bytes
                            + b"\r\n"
                        )
                except asyncio.TimeoutError:
                    # Send keep-alive frame
                    yield b"--frame\r\n\r\n"
        finally:
            sensor_pipeline.unregister_frame_queue(sensor_id)

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get("/{sensor_id}/snapshot")
async def get_snapshot(sensor_id: str, user: dict = Depends(get_current_user)):
    """Get the latest frame from a sensor node."""
    buffer = sensor_pipeline.ring_buffers.get_buffer(sensor_id)
    frames = buffer.get_last_n(1)

    if not frames:
        raise HTTPException(status_code=404, detail="No frames available from this sensor")

    latest = frames[0]
    return {
        "sensor_id": sensor_id,
        "frame_data": latest["data"].get("frame_data", ""),
        "timestamp": latest["timestamp"],
        "resolution": latest["data"].get("resolution", [640, 480])
    }


@router.get("/{sensor_id}/stats")
async def get_stream_stats(sensor_id: str, user: dict = Depends(get_current_user)):
    """Get streaming statistics for a sensor node."""
    stats = sensor_pipeline.get_sensor_stats(sensor_id)
    if stats["total_frames"] == 0:
        raise HTTPException(status_code=404, detail="No data from this sensor")
    return stats
```

---

## 03.6 — Register Pipeline with MQTT (backend/services/pipeline_setup.py)

```python
"""
HomeGuardian AI — Pipeline Setup
Registers MQTT handlers to connect the sensor pipeline.
"""

import logging
from mqtt_client import mqtt_manager
from services.sensor_pipeline import sensor_pipeline
from utils.mqtt_topics import MQTTTopics

logger = logging.getLogger("homeguardian.pipeline_setup")


def setup_sensor_pipeline():
    """Register all MQTT handlers for the sensor pipeline."""

    # Handle incoming video frames
    mqtt_manager.subscribe(
        MQTTTopics.SENSOR_FRAME_PATTERN,
        sensor_pipeline.process_sensor_frame
    )

    # Handle heartbeat messages
    mqtt_manager.subscribe(
        MQTTTopics.SENSOR_HEARTBEAT_PATTERN,
        sensor_pipeline.process_heartbeat
    )

    # Handle status updates
    mqtt_manager.subscribe(
        MQTTTopics.SENSOR_STATUS_PATTERN,
        sensor_pipeline.process_status_update
    )

    logger.info("Sensor pipeline MQTT handlers registered")
```

Add to `main.py` startup (inside the lifespan, after MQTT connect):

```python
# Add after mqtt_manager.connect() in main.py lifespan:
from services.pipeline_setup import setup_sensor_pipeline
setup_sensor_pipeline()
```

---

## Verification

```bash
# 1. Ensure backend is running
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# 2. Register a test sensor (need a token first)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"device_name":"test-sensor","password":"test123456","role":"old_device"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -X POST http://localhost:8000/api/sensors \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Living Room Camera","type":"phone","location_zone":"living_room"}'

# 3. Test stream stats endpoint (will return 404 since no frames yet — correct)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/stream/phone-test/stats

# 4. Verify MQTT handler registration in server logs
# Look for: "Sensor pipeline MQTT handlers registered"

# 5. Test ring buffer independently
python -c "
from utils.ring_buffer import RingBuffer
buf = RingBuffer(10)
for i in range(15):
    buf.push({'frame': i})
print(f'Size: {buf.size}')
print(f'Last 3: {buf.get_last_n(3)}')
print('Ring buffer test PASSED')
"
```

Expected: Server starts with pipeline registration logged. Sensor registration works. Ring buffer test passes, showing correct circular behavior (size=10, last 3 frames are frames 12-14).
