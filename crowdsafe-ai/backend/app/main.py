"""
CrowdSafe AI - FastAPI Backend Server.
Provides REST and streaming endpoints for real-time crowd monitoring,
YOLO person detection, zone risk analysis, and alert dispatching.
"""

import os
import shutil
import time
import uuid
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from .config import UPLOAD_DIR, SAMPLE_DIR, RISK_LEVELS
from .database import (
    init_db,
    get_cameras,
    get_camera,
    save_camera,
    update_camera_status,
    get_zones_for_camera,
    save_zone,
    update_zone_thresholds,
    get_alerts,
    acknowledge_alert,
    get_recent_observations
)
from .detector import get_detector
from .simulator import get_simulator
from .video_processor import get_or_create_session, get_session

# Initialize FastAPI App
app = FastAPI(
    title="CrowdSafe AI API",
    description="Functional AI-powered crowd monitoring & stampede early-warning system prototype",
    version="1.0.0"
)

# Enable CORS for local React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initializes the database schema and ensures directories exist."""
    init_db()
    # Trigger detector load in background thread so it is warm
    try:
        det = get_detector()
        print(f"[CrowdSafe] Detection engine initialized: {det.backend_type}")
    except Exception as e:
        print(f"[CrowdSafe] Warning initializing detector: {e}")


# Pydantic Request Models
class ZoneThresholdUpdate(BaseModel):
    normal_threshold: int
    increasing_threshold: int
    high_threshold: int
    critical_threshold: int
    congestion_seconds_threshold: int


class AcknowledgeRequest(BaseModel):
    acknowledged_by: Optional[str] = "Control Room Operator"


# --- SYSTEM & STATUS ENDPOINTS ---

@app.get("/api/status")
def get_system_status():
    detector = get_detector()
    return {
        "status": "online",
        "system_name": "CrowdSafe AI",
        "version": "1.0.0",
        "detection_engine": detector.backend_type,
        "yolo_model": detector.model_name,
        "disclaimer": "Identifies potential crowd-safety risks and bottleneck congestion rather than predicting stampedes with certainty."
    }


# --- CAMERA ENDPOINTS ---

@app.get("/api/cameras")
def list_cameras():
    cameras = get_cameras()
    return {"cameras": cameras}


@app.get("/api/cameras/{camera_id}")
def get_camera_details(camera_id: str):
    cam = get_camera(camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    zones = get_zones_for_camera(camera_id)
    return {"camera": cam, "zones": zones}


@app.get("/api/cameras/{camera_id}/zones")
def list_zones(camera_id: str):
    zones = get_zones_for_camera(camera_id)
    return {"zones": zones}


@app.put("/api/zones/{zone_id}")
def update_zone(zone_id: str, payload: ZoneThresholdUpdate):
    update_zone_thresholds(
        zone_id=zone_id,
        normal=payload.normal_threshold,
        increasing=payload.increasing_threshold,
        high=payload.high_threshold,
        critical=payload.critical_threshold,
        congestion_sec=payload.congestion_seconds_threshold
    )
    return {"success": True, "zone_id": zone_id, "updated": payload.dict()}


# --- LIVE DASHBOARD METRICS (POLLING ENDPOINT) ---

@app.get("/api/cameras/{camera_id}/live-metrics")
def get_live_metrics(camera_id: str):
    cam = get_camera(camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")

    zones = get_zones_for_camera(camera_id)
    is_simulated = (cam["status"] == "simulated" or cam["video_source"] == "demo_simulation")

    if is_simulated:
        sim = get_simulator(camera_id, cam["name"])
        zone_statuses, overall_risk, _ = sim.step(zones)
        total_pax = sum(zs["person_count"] for zs in zone_statuses.values())
        recent_alerts = get_alerts(camera_id=camera_id, limit=6, active_only=False)
        active_alerts_count = len([a for a in recent_alerts if a["acknowledged"] == 0])

        return {
            "camera_id": camera_id,
            "camera_name": cam["name"],
            "is_simulated": True,
            "detection_engine": "Simulated Flow Model",
            "total_people_count": total_pax,
            "overall_risk_level": overall_risk,
            "zone_statuses": zone_statuses,
            "active_alerts_count": active_alerts_count,
            "recent_alerts": recent_alerts,
            "surge_active": sim.forced_surge,
            "timestamp": time.time()
        }
    else:
        # Real Video Session with YOLO
        session = get_session(camera_id)
        if not session and cam["video_source"] and os.path.exists(cam["video_source"]):
            session = get_or_create_session(camera_id, cam["video_source"])

        if session:
            metrics = session.get_latest_metrics()
            recent_alerts = get_alerts(camera_id=camera_id, limit=6, active_only=False)
            active_alerts_count = len([a for a in recent_alerts if a["acknowledged"] == 0])

            return {
                "camera_id": camera_id,
                "camera_name": cam["name"],
                "is_simulated": False,
                "detection_engine": f"Real YOLO ({metrics['detection_engine']})",
                "total_people_count": metrics["total_people_count"],
                "overall_risk_level": metrics["overall_risk_level"],
                "zone_statuses": metrics["zone_statuses"],
                "active_alerts_count": active_alerts_count,
                "recent_alerts": recent_alerts,
                "current_frame": metrics["current_frame"],
                "total_frames": metrics["total_frames"],
                "status": metrics["status"],
                "error": metrics["error"],
                "timestamp": time.time()
            }
        else:
            return {
                "camera_id": camera_id,
                "camera_name": cam["name"],
                "is_simulated": False,
                "detection_engine": "YOLO (Idle)",
                "total_people_count": 0,
                "overall_risk_level": "normal",
                "zone_statuses": {},
                "active_alerts_count": 0,
                "recent_alerts": [],
                "status": "idle",
                "timestamp": time.time()
            }


# --- MJPEG VIDEO STREAM ENDPOINT ---

@app.get("/api/cameras/{camera_id}/stream")
def video_stream(camera_id: str):
    """
    Streams multipart JPEG frames with real-time HUD annotations.
    Streams synthetic CCTV frames in demo mode, or real YOLO-annotated frames for uploaded videos.
    """
    cam = get_camera(camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")

    is_simulated = (cam["status"] == "simulated" or cam["video_source"] == "demo_simulation")

    def frame_generator():
        if is_simulated:
            sim = get_simulator(camera_id, cam["name"])
            while True:
                try:
                    zones = get_zones_for_camera(camera_id)
                    zone_statuses, overall_risk, _ = sim.step(zones, record_db=False)
                    frame = sim.generate_synthetic_frame(zones, zone_statuses, overall_risk)
                    import cv2
                    ret, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                    if ret:
                        frame_bytes = buf.tobytes()
                        yield (b"--frame\r\n"
                               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
                except Exception as e:
                    print(f"[Stream] Sim frame error: {e}")
                time.sleep(0.06)  # ~16 FPS
        else:
            session = get_session(camera_id)
            if not session and cam["video_source"] and os.path.exists(cam["video_source"]):
                session = get_or_create_session(camera_id, cam["video_source"])

            while True:
                try:
                    if session:
                        frame_bytes = session.get_frame()
                        if frame_bytes:
                            yield (b"--frame\r\n"
                                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
                except Exception as e:
                    print(f"[Stream] Video frame error: {e}")
                time.sleep(0.04)  # ~25 FPS

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# --- VIDEO UPLOAD & REAL DETECTION ---

@app.post("/api/videos/upload")
async def upload_crowd_video(
    file: UploadFile = File(...),
    camera_name: Optional[str] = Form("Uploaded Surveillance Feed"),
    location: Optional[str] = Form("Monitoring Point")
):
    """
    Uploads a prerecorded crowd video (MP4, AVI, MOV, WEBM).
    Initializes a new Camera with 4 zones, and begins real YOLO inference.
    """
    allowed_exts = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported format {ext}. Please upload MP4, AVI, MOV, or WEBM.")

    unique_cam_id = f"cam-upload-{int(time.time())}"
    dest_filename = f"{unique_cam_id}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, dest_filename)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Register camera in SQLite
    save_camera(
        camera_id=unique_cam_id,
        name=camera_name or f"Crowd Camera ({file.filename})",
        location=location or "Zone Area",
        status="active",
        video_source=dest_path,
        fps=25.0
    )

    # Create 4 configurable zones for the video (quadrants)
    default_zones = [
        {
            "id": f"{unique_cam_id}-z1",
            "camera_id": unique_cam_id,
            "name": "Zone A - Primary Ingress",
            "x_min": 0.05, "y_min": 0.05, "x_max": 0.48, "y_max": 0.50,
            "normal_threshold": 4, "increasing_threshold": 8, "high_threshold": 14, "critical_threshold": 20, "congestion_seconds_threshold": 3
        },
        {
            "id": f"{unique_cam_id}-z2",
            "camera_id": unique_cam_id,
            "name": "Zone B - Concourse Center",
            "x_min": 0.52, "y_min": 0.05, "x_max": 0.95, "y_max": 0.50,
            "normal_threshold": 6, "increasing_threshold": 10, "high_threshold": 16, "critical_threshold": 22, "congestion_seconds_threshold": 4
        },
        {
            "id": f"{unique_cam_id}-z3",
            "camera_id": unique_cam_id,
            "name": "Zone C - Turnstile Corridor",
            "x_min": 0.05, "y_min": 0.52, "x_max": 0.48, "y_max": 0.95,
            "normal_threshold": 4, "increasing_threshold": 7, "high_threshold": 12, "critical_threshold": 18, "congestion_seconds_threshold": 3
        },
        {
            "id": f"{unique_cam_id}-z4",
            "camera_id": unique_cam_id,
            "name": "Zone D - Egress Path",
            "x_min": 0.52, "y_min": 0.52, "x_max": 0.95, "y_max": 0.95,
            "normal_threshold": 5, "increasing_threshold": 9, "high_threshold": 15, "critical_threshold": 20, "congestion_seconds_threshold": 3
        }
    ]

    for z in default_zones:
        save_zone(z)

    # Launch Real YOLO Video Session
    session = get_or_create_session(unique_cam_id, dest_path)

    return {
        "success": True,
        "camera_id": unique_cam_id,
        "camera_name": camera_name,
        "message": "Video successfully uploaded. Real YOLO person detection started."
    }


@app.post("/api/videos/load-sample")
def load_sample_video():
    """
    Instant 1-click feature to load bundled crowd sample video and run real YOLO person detection.
    """
    sample_path = os.path.join(SAMPLE_DIR, "crowd_sample.mp4")
    if not os.path.exists(sample_path):
        raise HTTPException(status_code=404, detail="Sample crowd video file not found on disk.")

    sample_cam_id = "cam-sample-crowd"
    save_camera(
        camera_id=sample_cam_id,
        name="Pedestrian Concourse (Real YOLO Feed)",
        location="Public Plaza Entrance",
        status="active",
        video_source=sample_path,
        fps=12.0
    )

    sample_zones = [
        {
            "id": f"{sample_cam_id}-z1",
            "camera_id": sample_cam_id,
            "name": "Zone 1 - Pedestrian Walkway",
            "x_min": 0.05, "y_min": 0.1, "x_max": 0.48, "y_max": 0.9,
            "normal_threshold": 2, "increasing_threshold": 4, "high_threshold": 6, "critical_threshold": 8, "congestion_seconds_threshold": 3
        },
        {
            "id": f"{sample_cam_id}-z2",
            "camera_id": sample_cam_id,
            "name": "Zone 2 - Crossing Area",
            "x_min": 0.52, "y_min": 0.1, "x_max": 0.95, "y_max": 0.9,
            "normal_threshold": 2, "increasing_threshold": 4, "high_threshold": 6, "critical_threshold": 8, "congestion_seconds_threshold": 3
        }
    ]

    for z in sample_zones:
        save_zone(z)

    get_or_create_session(sample_cam_id, sample_path)

    return {
        "success": True,
        "camera_id": sample_cam_id,
        "message": "Loaded sample crowd video for real YOLO person detection."
    }


# --- ALERTS ENDPOINTS ---

@app.get("/api/alerts")
def list_alerts(
    camera_id: Optional[str] = None,
    active_only: bool = False,
    limit: int = Query(50, ge=1, le=200)
):
    alerts = get_alerts(camera_id=camera_id, limit=limit, active_only=active_only)
    return {"alerts": alerts}


@app.post("/api/alerts/{alert_id}/acknowledge")
def acknowledge(alert_id: str, payload: Optional[AcknowledgeRequest] = None):
    by = payload.acknowledged_by if payload else "Operator"
    acknowledge_alert(alert_id, acknowledged_by=by)
    return {"success": True, "alert_id": alert_id, "acknowledged_by": by}


# --- TIME-SERIES OBSERVATIONS ENDPOINT ---

@app.get("/api/observations/history")
def get_observations(camera_id: str, limit: int = 40):
    obs = get_recent_observations(camera_id=camera_id, limit=limit)
    return {"observations": obs}


# --- DEMO SURGE TRIGGER ---

@app.post("/api/demo/trigger-surge")
def trigger_demo_surge(camera_id: Optional[str] = Query("cam-demo-gate-4")):
    """Allows demo presenter to trigger immediate crowd surge for live hackathon judge testing."""
    cam = get_camera(camera_id)
    sim = get_simulator(camera_id, cam["name"] if cam else "Demo Camera")
    sim.trigger_surge(duration_sec=30.0)
    return {
        "success": True,
        "message": f"Simulated crowd surge triggered for {camera_id}! Risk levels will spike for 30s.",
        "camera_id": camera_id
    }


# --- STATIC FRONTEND SERVING (UNIFIED RUN MODE) ---
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "frontend", "dist"))

if os.path.exists(DIST_DIR):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API route not found")
        file_path = os.path.join(DIST_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(DIST_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse({"status": "CrowdSafe AI API Online. Build frontend with 'npm run build'."})

