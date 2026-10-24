"""
Video Processing Engine for CrowdSafe AI.
Performs real frame-by-frame YOLO person detection on uploaded prerecorded crowd videos.
Annotates frames with bounding boxes, risk zones, and HUD telemetry,
and logs observations and alerts into SQLite.
"""

import cv2
import os
import time
import threading
from typing import Dict, Any, List, Optional
from .detector import get_detector
from .risk_analyzer import CrowdRiskAnalyzer
from .database import (
    record_observation,
    record_alert,
    get_zones_for_camera,
    update_camera_status
)


class VideoSession:
    def __init__(self, camera_id: str, video_path: str):
        self.camera_id = camera_id
        self.video_path = video_path
        self.detector = get_detector()
        self.risk_analyzer = CrowdRiskAnalyzer()

        self.is_running = False
        self.is_paused = False
        self.current_frame_idx = 0
        self.total_frames = 0
        self.fps = 25.0
        self.width = 640
        self.height = 360

        # Latest processed metrics
        self.latest_frame: Optional[bytes] = None
        self.latest_person_count = 0
        self.latest_detections: List[Dict[str, Any]] = []
        self.latest_zone_statuses: Dict[str, Dict[str, Any]] = {}
        self.latest_overall_risk = "normal"
        self.processing_error: Optional[str] = None
        self.is_completed = False

        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        self._init_video_meta()

    def _init_video_meta(self):
        cap = cv2.VideoCapture(self.video_path)
        if cap.isOpened():
            self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
            self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 360
            cap.release()
        else:
            self.processing_error = f"Cannot open video file: {self.video_path}"

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.is_completed = False
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False

    def _process_loop(self):
        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                self.processing_error = "Failed to open video source"
                self.is_running = False
                return

            update_camera_status(self.camera_id, "analyzing")
            frame_interval = 1.0 / min(self.fps, 25.0)

            while self.is_running:
                start_loop_time = time.time()

                ret, frame = cap.read()
                if not ret:
                    # Loop back to beginning for continuous prototype presentation
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.current_frame_idx = 0
                    ret, frame = cap.read()
                    if not ret:
                        break

                self.current_frame_idx += 1
                h, w = frame.shape[:2]

                # Fetch up-to-date zones for camera
                zones = get_zones_for_camera(self.camera_id)

                # 1. REAL YOLO Person Detection
                detections = self.detector.detect(frame)

                # 2. Risk & Congestion Analysis
                zone_statuses, overall_risk, alerts = self.risk_analyzer.analyze_frame_zones(
                    frame_width=w,
                    frame_height=h,
                    detections=detections,
                    zones=zones,
                    current_time=time.time()
                )

                # 3. Store new alerts in SQLite
                for alert in alerts:
                    alert_id = f"alert-{self.camera_id}-{int(time.time() * 1000)}"
                    record_alert(
                        alert_id=alert_id,
                        camera_id=self.camera_id,
                        zone_id=alert["zone_id"],
                        zone_name=alert["zone_name"],
                        risk_level=alert["risk_level"],
                        person_count=alert["person_count"],
                        threshold_exceeded=alert["threshold_exceeded"],
                        reason=alert["reason"]
                    )

                # 4. Record time-series observation periodically
                if self.current_frame_idx % 15 == 0:
                    for zid, zstat in zone_statuses.items():
                        record_observation(
                            camera_id=self.camera_id,
                            zone_id=zid,
                            person_count=zstat["person_count"],
                            risk_level=zstat["risk_level"],
                            congested_duration=zstat["congested_duration"]
                        )

                # 5. Annotate Frame with HUD overlays
                annotated_frame = self.detector.annotate_frame(
                    frame=frame,
                    detections=detections,
                    zones=zones,
                    zone_statuses=zone_statuses,
                    system_status_tag="REAL YOLO DETECTION"
                )

                # Encode as JPEG for streaming
                ret_enc, buffer = cv2.imencode(".jpg", annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if ret_enc:
                    jpeg_bytes = buffer.tobytes()
                    with self._lock:
                        self.latest_frame = jpeg_bytes
                        self.latest_person_count = len(detections)
                        self.latest_detections = detections
                        self.latest_zone_statuses = zone_statuses
                        self.latest_overall_risk = overall_risk

                # Regulate playback FPS
                elapsed = time.time() - start_loop_time
                sleep_time = max(0.01, frame_interval - elapsed)
                time.sleep(sleep_time)

            cap.release()
            update_camera_status(self.camera_id, "active")
            self.is_completed = True
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.processing_error = str(e)
            self.is_running = False

    def get_latest_metrics(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "camera_id": self.camera_id,
                "is_simulated": False,
                "detection_engine": self.detector.backend_type,
                "total_people_count": self.latest_person_count,
                "overall_risk_level": self.latest_overall_risk,
                "zone_statuses": self.latest_zone_statuses,
                "current_frame": self.current_frame_idx,
                "total_frames": self.total_frames,
                "status": "analyzing" if self.is_running else ("completed" if self.is_completed else "idle"),
                "error": self.processing_error
            }

    def get_frame(self) -> Optional[bytes]:
        with self._lock:
            return self.latest_frame


# Active sessions registry
_sessions: Dict[str, VideoSession] = {}

def get_or_create_session(camera_id: str, video_path: str) -> VideoSession:
    if camera_id not in _sessions:
        session = VideoSession(camera_id, video_path)
        session.start()
        _sessions[camera_id] = session
    return _sessions[camera_id]

def get_session(camera_id: str) -> Optional[VideoSession]:
    return _sessions.get(camera_id)
