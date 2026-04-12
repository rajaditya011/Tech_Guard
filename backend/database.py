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
                type TEXT NOT NULL CHECK(type IN ('phone', 'webcam', 'cctv', 'iot_sensor')),
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
                channel TEXT NOT NULL CHECK(channel IN ('push', 'audio', 'log', 'email')),
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
