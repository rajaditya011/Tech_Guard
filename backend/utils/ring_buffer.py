"""
HomeGuardian AI — Ring Buffer
Circular buffer for storing pre-anomaly context frames.
"""

import threading
from collections import deque
from typing import List
from datetime import datetime


class RingBuffer:
    """Thread-safe circular buffer for frame storage."""

    def __init__(self, capacity: int = 150):
        self._buffer: deque = deque(maxlen=capacity)
        self._lock = threading.Lock()
        self.capacity = capacity

    def push(self, frame_data: dict):
        with self._lock:
            self._buffer.append({"data": frame_data, "timestamp": datetime.utcnow().isoformat()})

    def get_all(self) -> List[dict]:
        with self._lock:
            return list(self._buffer)

    def get_last_n(self, n: int) -> List[dict]:
        with self._lock:
            items = list(self._buffer)
            return items[-n:] if len(items) >= n else items

    def get_last_seconds(self, seconds: float, fps: int = 15) -> List[dict]:
        n_frames = int(seconds * fps)
        return self.get_last_n(n_frames)

    def clear(self):
        with self._lock:
            self._buffer.clear()

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._buffer)

    @property
    def is_full(self) -> bool:
        return self.size >= self.capacity


class MultiSensorRingBuffer:
    """Manages individual ring buffers for each sensor node."""

    def __init__(self, capacity_per_sensor: int = 150):
        self._buffers: dict = {}
        self._capacity = capacity_per_sensor
        self._lock = threading.Lock()

    def get_buffer(self, sensor_id: str) -> RingBuffer:
        with self._lock:
            if sensor_id not in self._buffers:
                self._buffers[sensor_id] = RingBuffer(self._capacity)
            return self._buffers[sensor_id]

    def push_frame(self, sensor_id: str, frame_data: dict):
        self.get_buffer(sensor_id).push(frame_data)

    def get_pre_event_frames(self, sensor_id: str, seconds: float, fps: int = 15) -> List[dict]:
        return self.get_buffer(sensor_id).get_last_seconds(seconds, fps)

    def remove_sensor(self, sensor_id: str):
        with self._lock:
            self._buffers.pop(sensor_id, None)
