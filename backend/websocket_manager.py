"""
HomeGuardian AI — WebSocket Manager
Manages WebSocket connections for both portal types.
"""

import json
import logging
from typing import Dict
from fastapi import WebSocket

logger = logging.getLogger("homeguardian.websocket")


class ConnectionManager:
    """Manages WebSocket connections for old devices and dashboard users."""

    def __init__(self):
        self.old_devices: Dict[str, WebSocket] = {}
        self.dashboards: Dict[str, WebSocket] = {}

    async def connect_old_device(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.old_devices[device_id] = websocket
        logger.info(f"Old device connected: {device_id}")

    async def connect_dashboard(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.dashboards[user_id] = websocket
        logger.info(f"Dashboard connected: {user_id}")

    def disconnect_old_device(self, device_id: str):
        self.old_devices.pop(device_id, None)
        logger.info(f"Old device disconnected: {device_id}")

    def disconnect_dashboard(self, user_id: str):
        self.dashboards.pop(user_id, None)
        logger.info(f"Dashboard disconnected: {user_id}")

    async def send_to_old_device(self, device_id: str, message: dict):
        ws = self.old_devices.get(device_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to old device {device_id}: {e}")
                self.disconnect_old_device(device_id)

    async def send_to_dashboard(self, user_id: str, message: dict):
        ws = self.dashboards.get(user_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to dashboard {user_id}: {e}")
                self.disconnect_dashboard(user_id)

    async def broadcast_to_dashboards(self, message: dict):
        disconnected = []
        for user_id, ws in self.dashboards.items():
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(user_id)
        for user_id in disconnected:
            self.disconnect_dashboard(user_id)

    async def broadcast_to_old_devices(self, message: dict):
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


connection_manager = ConnectionManager()
