"""
Person Detection engine using YOLO and OpenCV.
Provides real-time person detection, bounding box extraction, center point estimation,
and high-tech HUD frame annotation.
"""

import cv2
import numpy as np
import os
import time
from typing import List, Dict, Any, Tuple
from .config import RISK_LEVELS, DEFAULT_CONFIDENCE_THRESHOLD

# Try to import YOLO from ultralytics
YOLO_AVAILABLE = False
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class PersonDetector:
    def __init__(self, model_name: str = "yolov8n.pt", confidence: float = DEFAULT_CONFIDENCE_THRESHOLD):
        self.confidence = confidence
        # Locate yolov8n.pt in backend directory if relative
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bundled_pt = os.path.join(backend_dir, "yolov8n.pt")
        if os.path.exists(bundled_pt):
            self.model_name = bundled_pt
        else:
            self.model_name = model_name

        self.model = None
        self.backend_type = "none"
        self._initialize_model()

    def _initialize_model(self):
        """Attempts to load YOLO, falling back to OpenCV HOG if unavailable."""
        if YOLO_AVAILABLE:
            try:
                print(f"[Detector] Loading YOLO model: {self.model_name}...")
                self.model = YOLO(self.model_name)
                self.backend_type = "yolo"
                print(f"[Detector] Successfully initialized YOLO model: {self.model_name}")
                return
            except Exception as e:
                print(f"[Detector] YOLO load failed ({e}), falling back to OpenCV HOG People Detector.")

        # OpenCV HOG Fallback (guaranteed to work offline with 0 dependencies)
        try:
            print("[Detector] Initializing OpenCV HOG Default People Detector...")
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            self.backend_type = "opencv_hog"
            print("[Detector] OpenCV HOG People Detector ready.")
        except Exception as e:
            print(f"[Detector] Error initializing OpenCV HOG: {e}")
            self.backend_type = "error"

        # Warmup model
        try:
            dummy = np.zeros((64, 64, 3), dtype=np.uint8)
            self.detect(dummy)
        except Exception:
            pass

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detects people in a BGR frame.
        Returns a list of dicts:
        [{
            "bbox": [x1, y1, x2, y2],
            "confidence": float,
            "center": [cx, cy],
            "foot": [cx, y2]
        }, ...]
        """
        if frame is None or frame.size == 0:
            return []

        h, w = frame.shape[:2]
        detections = []

        if self.backend_type == "yolo" and self.model is not None:
            try:
                # Run YOLO inference specifically targeting person class (0)
                results = self.model.predict(
                    source=frame,
                    classes=[0],
                    conf=self.confidence,
                    verbose=False
                )

                if results and len(results) > 0:
                    boxes = results[0].boxes
                    for box in boxes:
                        coords = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0].cpu().numpy())
                        x1, y1, x2, y2 = [int(v) for v in coords]
                        # Clamp to frame bounds
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(w, x2), min(h, y2)

                        cx = int((x1 + x2) / 2)
                        cy = int((y1 + y2) / 2)
                        foot_y = int(y2)

                        detections.append({
                            "bbox": [x1, y1, x2, y2],
                            "confidence": round(conf, 3),
                            "center": [cx, cy],
                            "foot": [cx, foot_y]
                        })
                return detections
            except Exception as e:
                print(f"[Detector] YOLO detection exception: {e}")

        # Fallback to OpenCV HOG if YOLO is not active or encountered error
        if self.backend_type == "opencv_hog" or hasattr(self, "hog"):
            try:
                # Resize slightly for faster HOG processing if frame is huge
                scale_w = 640.0 / w if w > 640 else 1.0
                if scale_w < 1.0:
                    small_frame = cv2.resize(frame, (int(w * scale_w), int(h * scale_w)))
                else:
                    small_frame = frame

                rects, weights = self.hog.detectMultiScale(
                    small_frame,
                    winStride=(8, 8),
                    padding=(4, 4),
                    scale=1.05
                )

                inv_scale = 1.0 / scale_w
                for i, (rx, ry, rw, rh) in enumerate(rects):
                    x1 = int(rx * inv_scale)
                    y1 = int(ry * inv_scale)
                    x2 = int((rx + rw) * inv_scale)
                    y2 = int((ry + rh) * inv_scale)

                    # Clamp
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(w, x2), min(h, y2)

                    conf = float(weights[i]) if i < len(weights) else 0.75
                    # Normalize pseudo-confidence
                    norm_conf = min(0.99, max(0.40, 0.5 + conf * 0.2))

                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)

                    detections.append({
                        "bbox": [x1, y1, x2, y2],
                        "confidence": round(norm_conf, 2),
                        "center": [cx, cy],
                        "foot": [cx, y2]
                    })
                return detections
            except Exception as e:
                print(f"[Detector] OpenCV HOG error: {e}")

        return detections

    def annotate_frame(
        self,
        frame: np.ndarray,
        detections: List[Dict[str, Any]],
        zones: List[Dict[str, Any]],
        zone_statuses: Dict[str, Dict[str, Any]],
        system_status_tag: str = "LIVE AI"
    ) -> np.ndarray:
        """
        Draws professional security dashboard overlay on the video frame:
        - Configured zones with status colors & occupancy badges
        - Person bounding boxes with radar tracker dots
        - Top HUD telemetry header (Total count, Risk Level, Engine type)
        """
        annotated = frame.copy()
        h, w = frame.shape[:2]

        # 1. Draw Zones overlay
        zone_overlay = annotated.copy()
        for zone in zones:
            zx1 = int(zone["x_min"] * w)
            zy1 = int(zone["y_min"] * h)
            zx2 = int(zone["x_max"] * w)
            zy2 = int(zone["y_max"] * h)

            z_stat = zone_statuses.get(zone["id"], {})
            risk_level = z_stat.get("risk_level", "normal")
            person_count = z_stat.get("person_count", 0)

            risk_cfg = RISK_LEVELS.get(risk_level, RISK_LEVELS["normal"])
            color_bgr = risk_cfg["color_bgr"]

            # Zone tinted background
            cv2.rectangle(zone_overlay, (zx1, zy1), (zx2, zy2), color_bgr, -1)

            # Zone border
            thickness = 3 if risk_level in ["high", "critical"] else 2
            cv2.rectangle(annotated, (zx1, zy1), (zx2, zy2), color_bgr, thickness)

            # Zone label banner
            badge_text = f"{zone['name']} [{person_count} pax | {risk_cfg['label'].upper()}]"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.45
            (tw, th), baseline = cv2.getTextSize(badge_text, font, font_scale, 1)

            cv2.rectangle(annotated, (zx1, zy1), (zx1 + tw + 10, zy1 + th + 10), (20, 24, 33), -1)
            cv2.rectangle(annotated, (zx1, zy1), (zx1 + tw + 10, zy1 + th + 10), color_bgr, 1)
            cv2.putText(annotated, badge_text, (zx1 + 5, zy1 + th + 4), font, font_scale, (255, 255, 255), 1, cv2.LINE_AA)

        # Alpha blend zone tints (20% opacity)
        cv2.addWeighted(zone_overlay, 0.18, annotated, 0.82, 0, annotated)

        # 2. Draw Detected People Bounding Boxes
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            conf = det["confidence"]
            cx, cy = det["center"]

            # Determine person's zone risk color (foot or center)
            det_color = (0, 255, 128)  # default bright green
            for zone in zones:
                zx1 = int(zone["x_min"] * w)
                zy1 = int(zone["y_min"] * h)
                zx2 = int(zone["x_max"] * w)
                zy2 = int(zone["y_max"] * h)
                if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
                    z_risk = zone_statuses.get(zone["id"], {}).get("risk_level", "normal")
                    det_color = RISK_LEVELS.get(z_risk, RISK_LEVELS["normal"])["color_bgr"]
                    break

            # Box corners styling (tactical HUD brackets)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), det_color, 1)

            # Corner brackets
            corner_len = min(14, int((x2 - x1) / 4), int((y2 - y1) / 4))
            # Top-left
            cv2.line(annotated, (x1, y1), (x1 + corner_len, y1), det_color, 2)
            cv2.line(annotated, (x1, y1), (x1, y1 + corner_len), det_color, 2)
            # Top-right
            cv2.line(annotated, (x2, y1), (x2 - corner_len, y1), det_color, 2)
            cv2.line(annotated, (x2, y1), (x2, y1 + corner_len), det_color, 2)
            # Bottom-left
            cv2.line(annotated, (x1, y2), (x1 + corner_len, y2), det_color, 2)
            cv2.line(annotated, (x1, y2), (x1, y2 - corner_len), det_color, 2)
            # Bottom-right
            cv2.line(annotated, (x2, y2), (x2 - corner_len, y2), det_color, 2)
            cv2.line(annotated, (x2, y2), (x2, y2 - corner_len), det_color, 2)

            # Center position marker
            cv2.circle(annotated, (cx, cy), 3, (0, 255, 255), -1)

            # Small tag
            tag = f"{int(conf * 100)}%"
            cv2.putText(annotated, tag, (x1, max(12, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.35, det_color, 1, cv2.LINE_AA)

        # 3. Top Tactical HUD Bar
        hud_h = 36
        hud_overlay = annotated.copy()
        cv2.rectangle(hud_overlay, (0, 0), (w, hud_h), (15, 20, 28), -1)
        cv2.addWeighted(hud_overlay, 0.85, annotated, 0.15, 0, annotated)
        cv2.line(annotated, (0, hud_h), (w, hud_h), (40, 50, 70), 1)

        # Telemetry Texts
        total_count = len(detections)
        engine_str = "YOLOv8n" if self.backend_type == "yolo" else "OpenCV-HOG"
        hud_left = f"CROWDSAFE AI // {system_status_tag} // MODEL: {engine_str}"
        hud_right = f"DETECTED: {total_count} PAX"

        cv2.putText(annotated, hud_left, (12, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 240, 255), 1, cv2.LINE_AA)
        cv2.putText(annotated, hud_right, (w - 180, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2, cv2.LINE_AA)

        return annotated


# Global detector singleton
_detector_instance: PersonDetector = None

def get_detector() -> PersonDetector:
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = PersonDetector()
    return _detector_instance
