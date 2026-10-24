"""
Realistic Crowd Simulation Engine for CrowdSafe AI Demo Mode.
Used when no live camera or prerecorded video is active.
Clearly stamps and labels all simulated data with 'SIMULATED / DEMO MODE'.
Never misrepresents simulated data as real.
"""

import time
import math
import random
import uuid
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
from .config import RISK_LEVELS
from .database import record_observation, record_alert


class CrowdSimulator:
    def __init__(self, camera_id: str, camera_name: str):
        self.camera_id = camera_id
        self.camera_name = camera_name
        self.start_time = time.time()
        self.forced_surge = False
        self.surge_end_time = 0.0

        # Dynamic simulated state per zone
        self.zone_states: Dict[str, Dict[str, Any]] = {}

        # Simulated people positions for rendering
        self.simulated_people = []
        self._init_particles()

    def _init_particles(self):
        # Generate 50 simulated particles (people) roaming
        self.simulated_people = []
        for _ in range(50):
            self.simulated_people.append({
                "x": random.uniform(0.1, 0.9),
                "y": random.uniform(0.15, 0.9),
                "vx": random.uniform(-0.005, 0.005),
                "vy": random.uniform(-0.005, 0.005),
                "size": random.randint(18, 28)
            })

    def trigger_surge(self, duration_sec: float = 30.0):
        """Allows demo presenter to trigger an immediate crowd surge across any camera feed."""
        self.forced_surge = True
        self.surge_end_time = time.time() + duration_sec
        # Spike all zone base counts beyond critical thresholds
        for zid, state in self.zone_states.items():
            state["base"] = max(26, state.get("critical_th", 24) + 4)
            state["congested_start"] = time.time() - 3.5  # prime congestion so alarm fires quickly!

    def step(self, zones: List[Dict[str, Any]], record_db: bool = True) -> Tuple[Dict[str, Dict[str, Any]], str, List[Dict[str, Any]]]:
        now = time.time()
        elapsed = now - self.start_time

        # Ensure all zones are registered in zone_states dynamically
        for zone in zones:
            zid = zone["id"]
            if zid not in self.zone_states:
                self.zone_states[zid] = {
                    "base": zone.get("normal_threshold", 6) + 1,
                    "default_base": zone.get("normal_threshold", 6) + 1,
                    "variance": max(2, zone.get("increasing_threshold", 12) - zone.get("normal_threshold", 6)),
                    "critical_th": zone.get("critical_threshold", 24),
                    "congested_start": 0.0
                }

        # Check if surge ended
        if self.forced_surge and now > self.surge_end_time:
            self.forced_surge = False
            for zid, state in self.zone_states.items():
                state["base"] = state.get("default_base", 8)
                state["congested_start"] = 0.0

        # Sinusoidal crowd oscillation pattern (simulates natural crowd waves)
        wave_1 = math.sin(elapsed * 0.15)
        wave_2 = math.cos(elapsed * 0.22)

        zone_statuses = {}
        alerts_generated = []
        highest_code = 0
        overall_risk = "normal"

        for zone in zones:
            zid = zone["id"]
            state = self.zone_states[zid]

            normal_th = zone.get("normal_threshold", 6)
            inc_th = zone.get("increasing_threshold", 12)
            high_th = zone.get("high_threshold", 18)
            crit_th = zone.get("critical_threshold", 24)
            cong_time_th = zone.get("congestion_seconds_threshold", 4)
            state["critical_th"] = crit_th

            # Calculate dynamic count
            noise = random.randint(-1, 2)
            if self.forced_surge:
                count = max(crit_th + 2, int(crit_th + 3 + abs(wave_1) * 4 + noise))
            else:
                count = max(1, int(state["base"] + wave_1 * state["variance"] + noise))

            # Determine risk
            if count <= normal_th:
                risk = "normal"
            elif count <= inc_th:
                risk = "increasing"
            elif count <= high_th:
                risk = "high"
            else:
                risk = "critical"

            # Duration tracking
            if risk in ["high", "critical"]:
                if state["congested_start"] == 0.0:
                    state["congested_start"] = now
                duration = round(now - state["congested_start"], 1)
            else:
                state["congested_start"] = 0.0
                duration = 0.0

            risk_cfg = RISK_LEVELS.get(risk, RISK_LEVELS["normal"])
            if risk_cfg["code"] > highest_code:
                highest_code = risk_cfg["code"]
                overall_risk = risk

            zone_statuses[zid] = {
                "zone_id": zid,
                "name": zone["name"],
                "person_count": count,
                "risk_level": risk,
                "congested_duration": duration,
                "thresholds": {
                    "normal": normal_th,
                    "increasing": inc_th,
                    "high": high_th,
                    "critical": crit_th,
                    "congestion_seconds": cong_time_th
                }
            }

            # Generate alert if conditions met
            if risk in ["high", "critical"] and duration >= cong_time_th:
                alert_id = f"sim-{zid}-{uuid.uuid4().hex[:8]}"
                thresh = crit_th if risk == "critical" else high_th
                reason = (
                    f"[SIMULATED SCENARIO] {zone['name']} occupancy ({count}) exceeded threshold ({thresh}) "
                    f"for {duration:.1f}s. Stampede safety protocol triggered."
                )
                alert_record = {
                    "id": alert_id,
                    "camera_id": self.camera_id,
                    "zone_id": zid,
                    "zone_name": zone["name"],
                    "risk_level": risk,
                    "person_count": count,
                    "threshold_exceeded": thresh,
                    "reason": reason
                }
                alerts_generated.append(alert_record)

                # ONLY write to SQLite if record_db flag is True (avoid doing DB writes 16x/sec during video frame generation)
                if record_db:
                    try:
                        record_alert(
                            alert_id=alert_id,
                            camera_id=self.camera_id,
                            zone_id=zid,
                            zone_name=zone["name"],
                            risk_level=risk,
                            person_count=count,
                            threshold_exceeded=thresh,
                            reason=reason
                        )
                    except Exception as e:
                        print(f"[Sim] Alert insert ignored: {e}")

            if record_db and random.random() < 0.2:
                try:
                    record_observation(self.camera_id, zid, count, risk, duration)
                except Exception:
                    pass

        return zone_statuses, overall_risk, alerts_generated

    def generate_synthetic_frame(
        self,
        zones: List[Dict[str, Any]],
        zone_statuses: Dict[str, Dict[str, Any]],
        overall_risk: str
    ) -> np.ndarray:
        """
        Renders a realistic dark-mode simulation CCTV video frame:
        - Architecture floor plan with designated zones
        - Moving crowd markers / person bounding boxes
        - Clear 'DEMO SIMULATION MODE' banner
        """
        w, h = 960, 540
        frame = np.zeros((h, w, 3), dtype=np.uint8)

        # Background CCTV texture (dark grid floor)
        frame[:] = (18, 22, 28)

        # Floor grid lines
        grid_step = 40
        for gx in range(0, w, grid_step):
            cv2.line(frame, (gx, 0), (gx, h), (26, 32, 42), 1)
        for gy in range(0, h, grid_step):
            cv2.line(frame, (0, gy), (w, gy), (26, 32, 42), 1)

        # Draw structural pillars / architectural features
        cv2.circle(frame, (int(w * 0.3), int(h * 0.35)), 18, (38, 46, 60), -1)
        cv2.circle(frame, (int(w * 0.7), int(h * 0.35)), 18, (38, 46, 60), -1)
        cv2.circle(frame, (int(w * 0.5), int(h * 0.75)), 22, (38, 46, 60), -1)

        # Render zones
        overlay = frame.copy()
        for zone in zones:
            zx1 = int(zone["x_min"] * w)
            zy1 = int(zone["y_min"] * h)
            zx2 = int(zone["x_max"] * w)
            zy2 = int(zone["y_max"] * h)

            z_stat = zone_statuses.get(zone["id"], {})
            risk_level = z_stat.get("risk_level", "normal")
            count = z_stat.get("person_count", 0)

            risk_cfg = RISK_LEVELS.get(risk_level, RISK_LEVELS["normal"])
            color_bgr = risk_cfg["color_bgr"]

            # Tinted zone
            cv2.rectangle(overlay, (zx1, zy1), (zx2, zy2), color_bgr, -1)
            cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), color_bgr, 2)

            # Zone label
            lbl = f"{zone['name']} ({count} PAX)"
            cv2.rectangle(frame, (zx1, zy1), (zx1 + len(lbl) * 8 + 14, zy1 + 22), (15, 18, 24), -1)
            cv2.rectangle(frame, (zx1, zy1), (zx1 + len(lbl) * 8 + 14, zy1 + 22), color_bgr, 1)
            cv2.putText(frame, lbl, (zx1 + 6, zy1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)

        # Move and render simulated people
        total_pax = 0
        for p in self.simulated_people:
            # Move particle
            p["x"] += p["vx"]
            p["y"] += p["vy"]

            # Bounce off bounds
            if p["x"] < 0.08 or p["x"] > 0.92:
                p["vx"] *= -1
            if p["y"] < 0.12 or p["y"] > 0.92:
                p["vy"] *= -1

            px = int(p["x"] * w)
            py = int(p["y"] * h)
            box_sz = p["size"]

            # Check which zone person is in
            p_color = (0, 240, 160)
            for zone in zones:
                zx1 = int(zone["x_min"] * w)
                zy1 = int(zone["y_min"] * h)
                zx2 = int(zone["x_max"] * w)
                zy2 = int(zone["y_max"] * h)
                if zx1 <= px <= zx2 and zy1 <= py <= zy2:
                    z_risk = zone_statuses.get(zone["id"], {}).get("risk_level", "normal")
                    p_color = RISK_LEVELS.get(z_risk, RISK_LEVELS["normal"])["color_bgr"]
                    break

            # Draw person as tactical box + center radar ping
            cv2.rectangle(frame, (px - box_sz // 2, py - box_sz), (px + box_sz // 2, py), p_color, 1)
            cv2.circle(frame, (px, py - box_sz // 2), 3, (255, 255, 255), -1)
            total_pax += 1

        # Clear Top Banner: [DEMO / SIMULATED MODE]
        banner_h = 40
        cv2.rectangle(frame, (0, 0), (w, banner_h), (25, 20, 15), -1)
        cv2.line(frame, (0, banner_h), (w, banner_h), (0, 165, 255), 2)

        # Prominent Simulation Mode Badge
        cv2.rectangle(frame, (10, 8), (210, 32), (0, 120, 255), -1)
        cv2.putText(frame, "SIMULATED DEMO MODE", (18, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2, cv2.LINE_AA)

        cam_text = f"CAM: {self.camera_name} // 30 FPS"
        cv2.putText(frame, cam_text, (225, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 200, 220), 1, cv2.LINE_AA)

        surge_status = "SURGE ACTIVE!" if self.forced_surge else "NOMINAL FLOW"
        surge_col = (0, 68, 255) if self.forced_surge else (0, 240, 120)
        cv2.putText(frame, f"STATUS: {surge_status}", (w - 240, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.48, surge_col, 2, cv2.LINE_AA)

        return frame


_simulators: Dict[str, CrowdSimulator] = {}

def get_simulator(camera_id: str, camera_name: str) -> CrowdSimulator:
    if camera_id not in _simulators:
        _simulators[camera_id] = CrowdSimulator(camera_id, camera_name)
    return _simulators[camera_id]
