"""
HomeGuardian AI — Sensor Data Pipeline
Handles MQTT message ingestion, frame buffering, and health tracking.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict

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
        self._loops: Dict[str, asyncio.AbstractEventLoop] = {}

    def process_sensor_frame(self, topic: str, payload: dict):
        device_id = MQTTTopics.extract_device_id(topic)
        if not device_id:
            logger.warning(f"Could not extract device_id from topic: {topic}")
            return

        self._frame_counts[device_id] = self._frame_counts.get(device_id, 0) + 1
        self._last_frame_time[device_id] = datetime.utcnow()

        self.ring_buffers.push_frame(device_id, {
            "frame_data": payload.get("frame_data", ""),
            "timestamp": payload.get("timestamp", datetime.utcnow().isoformat()),
            "resolution": payload.get("resolution", [640, 480])
        })

        if device_id in self._frame_queues and device_id in self._loops:
            loop = self._loops[device_id]
            if not loop.is_closed():
                def _enqueue():
                    try:
                        self._frame_queues[device_id].put_nowait(payload)
                    except asyncio.QueueFull:
                        try:
                            self._frame_queues[device_id].get_nowait()
                            self._frame_queues[device_id].put_nowait(payload)
                        except asyncio.QueueEmpty:
                            pass
                loop.call_soon_threadsafe(_enqueue)

        logger.debug(f"Frame {self._frame_counts[device_id]} from {device_id}")

    def process_heartbeat(self, topic: str, payload: dict):
        device_id = MQTTTopics.extract_device_id(topic)
        if not device_id:
            return
        try:
            with get_db() as conn:
                conn.execute(
                    "UPDATE sensor_nodes SET last_heartbeat = ?, status = 'active' WHERE id = ?",
                    (datetime.utcnow().isoformat(), device_id)
                )
        except Exception as e:
            logger.error(f"Failed to process heartbeat for {device_id}: {e}")

    def process_status_update(self, topic: str, payload: dict):
        device_id = MQTTTopics.extract_device_id(topic)
        if not device_id:
            return
        new_status = payload.get("status", "active")
        try:
            with get_db() as conn:
                conn.execute("UPDATE sensor_nodes SET status = ? WHERE id = ?", (new_status, device_id))
            logger.info(f"Status update from {device_id}: {new_status}")
        except Exception as e:
            logger.error(f"Failed to process status for {device_id}: {e}")

    def register_frame_queue(self, device_id: str) -> asyncio.Queue:
        if device_id not in self._frame_queues:
            self._frame_queues[device_id] = asyncio.Queue(maxsize=30)
            self._loops[device_id] = asyncio.get_running_loop()
        return self._frame_queues[device_id]

    def unregister_frame_queue(self, device_id: str):
        self._frame_queues.pop(device_id, None)
        self._loops.pop(device_id, None)

    def get_pre_event_frames(self, sensor_id: str, seconds: float = 5.0) -> list:
        return self.ring_buffers.get_pre_event_frames(sensor_id, seconds)

    def get_sensor_stats(self, sensor_id: str) -> dict:
        return {
            "sensor_id": sensor_id,
            "total_frames": self._frame_counts.get(sensor_id, 0),
            "buffer_size": self.ring_buffers.get_buffer(sensor_id).size,
            "last_frame": self._last_frame_time.get(sensor_id, None),
            "queue_active": sensor_id in self._frame_queues
        }


sensor_pipeline = SensorPipeline()
