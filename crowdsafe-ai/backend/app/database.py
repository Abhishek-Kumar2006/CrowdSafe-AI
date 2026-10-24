"""
SQLite Database module for CrowdSafe AI.
Handles schema initialization, seeding default cameras/zones, and CRUD operations.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "crowdsafe.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Cameras Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cameras (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        status TEXT NOT NULL,
        video_source TEXT,
        fps REAL DEFAULT 30.0,
        created_at TEXT NOT NULL
    )
    """)

    # Zones Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS zones (
        id TEXT PRIMARY KEY,
        camera_id TEXT NOT NULL,
        name TEXT NOT NULL,
        x_min REAL NOT NULL,
        y_min REAL NOT NULL,
        x_max REAL NOT NULL,
        y_max REAL NOT NULL,
        normal_threshold INTEGER NOT NULL DEFAULT 6,
        increasing_threshold INTEGER NOT NULL DEFAULT 12,
        high_threshold INTEGER NOT NULL DEFAULT 18,
        critical_threshold INTEGER NOT NULL DEFAULT 24,
        congestion_seconds_threshold INTEGER NOT NULL DEFAULT 4,
        FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE CASCADE
    )
    """)

    # Observations Table (time series crowd metrics)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        camera_id TEXT NOT NULL,
        zone_id TEXT,
        timestamp TEXT NOT NULL,
        person_count INTEGER NOT NULL,
        risk_level TEXT NOT NULL,
        congested_duration_sec REAL DEFAULT 0.0
    )
    """)

    # Alerts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        camera_id TEXT NOT NULL,
        zone_id TEXT NOT NULL,
        zone_name TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        risk_level TEXT NOT NULL,
        person_count INTEGER NOT NULL,
        threshold_exceeded INTEGER NOT NULL,
        reason TEXT NOT NULL,
        acknowledged INTEGER NOT NULL DEFAULT 0,
        acknowledged_at TEXT,
        acknowledged_by TEXT
    )
    """)

    conn.commit()

    # Seed initial demo camera & zones if not exists
    cursor.execute("SELECT COUNT(*) FROM cameras")
    if cursor.fetchone()[0] == 0:
        seed_default_data(cursor)
        conn.commit()

    conn.close()


def seed_default_data(cursor: sqlite3.Cursor):
    now = datetime.utcnow().isoformat() + "Z"

    # Default Cameras
    default_cameras = [
        ("cam-demo-gate-4", "Gate 4 Main Concourse", "North Stadium Plaza", "simulated", "demo_simulation", 30.0, now),
        ("cam-demo-south-corridor", "Corridor B - South Exit", "Grand Arena Tunnel", "simulated", "demo_simulation", 30.0, now),
        ("cam-demo-metro-hub", "Metro Interchange Level 1", "Central Station Platform", "simulated", "demo_simulation", 30.0, now),
    ]

    cursor.executemany("""
    INSERT INTO cameras (id, name, location, status, video_source, fps, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, default_cameras)

    # Zones for cam-demo-gate-4 (4 zones covering quadrants)
    default_zones = [
        ("zone-g4-a", "cam-demo-gate-4", "Zone A - Turnstiles Bottleneck", 0.05, 0.1, 0.48, 0.52, 6, 12, 18, 24, 3),
        ("zone-g4-b", "cam-demo-gate-4", "Zone B - Central Gathering Area", 0.52, 0.1, 0.95, 0.52, 8, 14, 20, 26, 4),
        ("zone-g4-c", "cam-demo-gate-4", "Zone C - Escalator Access Lane", 0.05, 0.55, 0.48, 0.95, 5, 10, 15, 20, 3),
        ("zone-g4-d", "cam-demo-gate-4", "Zone D - Emergency Egress Path", 0.52, 0.55, 0.95, 0.95, 4, 8, 12, 16, 2),

        # Zones for cam-demo-south-corridor
        ("zone-sc-a", "cam-demo-south-corridor", "Zone 1 - Funnel Chokepoint", 0.1, 0.15, 0.5, 0.85, 5, 10, 16, 22, 3),
        ("zone-sc-b", "cam-demo-south-corridor", "Zone 2 - Wide Dispersion Hall", 0.52, 0.15, 0.92, 0.85, 10, 18, 25, 32, 5),

        # Zones for cam-demo-metro-hub
        ("zone-mh-a", "cam-demo-metro-hub", "Zone A - Platform Edge 1-3", 0.05, 0.05, 0.95, 0.48, 8, 15, 22, 28, 4),
        ("zone-mh-b", "cam-demo-metro-hub", "Zone B - Concourse Staging", 0.05, 0.52, 0.95, 0.95, 10, 20, 28, 35, 5),
    ]

    cursor.executemany("""
    INSERT INTO zones (id, camera_id, name, x_min, y_min, x_max, y_max,
                       normal_threshold, increasing_threshold, high_threshold, critical_threshold, congestion_seconds_threshold)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, default_zones)


# Camera DB operations
def get_cameras() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cameras ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_camera(camera_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cameras WHERE id = ?", (camera_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_camera(camera_id: str, name: str, location: str, status: str, video_source: str, fps: float = 30.0):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat() + "Z"
    cursor.execute("""
    INSERT OR REPLACE INTO cameras (id, name, location, status, video_source, fps, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (camera_id, name, location, status, video_source, fps, now))
    conn.commit()
    conn.close()


def update_camera_status(camera_id: str, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE cameras SET status = ? WHERE id = ?", (status, camera_id))
    conn.commit()
    conn.close()


# Zone DB operations
def get_zones_for_camera(camera_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM zones WHERE camera_id = ?", (camera_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def save_zone(zone_data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO zones (id, camera_id, name, x_min, y_min, x_max, y_max,
                                   normal_threshold, increasing_threshold, high_threshold, critical_threshold, congestion_seconds_threshold)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        zone_data["id"],
        zone_data["camera_id"],
        zone_data["name"],
        zone_data["x_min"],
        zone_data["y_min"],
        zone_data["x_max"],
        zone_data["y_max"],
        zone_data.get("normal_threshold", 6),
        zone_data.get("increasing_threshold", 12),
        zone_data.get("high_threshold", 18),
        zone_data.get("critical_threshold", 24),
        zone_data.get("congestion_seconds_threshold", 4)
    ))
    conn.commit()
    conn.close()


def update_zone_thresholds(zone_id: str, normal: int, increasing: int, high: int, critical: int, congestion_sec: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE zones
    SET normal_threshold = ?, increasing_threshold = ?, high_threshold = ?, critical_threshold = ?, congestion_seconds_threshold = ?
    WHERE id = ?
    """, (normal, increasing, high, critical, congestion_sec, zone_id))
    conn.commit()
    conn.close()


# Observations
def record_observation(camera_id: str, zone_id: Optional[str], person_count: int, risk_level: str, congested_duration: float = 0.0):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat() + "Z"
    cursor.execute("""
    INSERT INTO observations (camera_id, zone_id, timestamp, person_count, risk_level, congested_duration_sec)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (camera_id, zone_id, now, person_count, risk_level, congested_duration))
    conn.commit()
    conn.close()


def get_recent_observations(camera_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM observations
    WHERE camera_id = ?
    ORDER BY id DESC LIMIT ?
    """, (camera_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in reversed(rows)]


# Alerts
def record_alert(alert_id: str, camera_id: str, zone_id: str, zone_name: str, risk_level: str, person_count: int, threshold_exceeded: int, reason: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat() + "Z"
        cursor.execute("""
        INSERT OR IGNORE INTO alerts (id, camera_id, zone_id, zone_name, timestamp, risk_level, person_count, threshold_exceeded, reason, acknowledged)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (alert_id, camera_id, zone_id, zone_name, now, risk_level, person_count, threshold_exceeded, reason))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Error recording alert: {e}")


def acknowledge_alert(alert_id: str, acknowledged_by: str = "Operator"):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat() + "Z"
    cursor.execute("""
    UPDATE alerts
    SET acknowledged = 1, acknowledged_at = ?, acknowledged_by = ?
    WHERE id = ?
    """, (now, acknowledged_by, alert_id))
    conn.commit()
    conn.close()


def get_alerts(camera_id: Optional[str] = None, limit: int = 50, active_only: bool = False) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM alerts"
    params = []
    conditions = []

    if camera_id:
        conditions.append("camera_id = ?")
        params.append(camera_id)
    if active_only:
        conditions.append("acknowledged = 0")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
