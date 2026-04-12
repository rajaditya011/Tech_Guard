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
    mqtt_manager.subscribe(MQTTTopics.SENSOR_FRAME_PATTERN, sensor_pipeline.process_sensor_frame)
    mqtt_manager.subscribe(MQTTTopics.SENSOR_HEARTBEAT_PATTERN, sensor_pipeline.process_heartbeat)
    mqtt_manager.subscribe(MQTTTopics.SENSOR_STATUS_PATTERN, sensor_pipeline.process_status_update)
    logger.info("Sensor pipeline MQTT handlers registered")
