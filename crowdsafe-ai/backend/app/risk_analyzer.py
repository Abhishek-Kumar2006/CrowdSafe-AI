"""
Crowd Risk Analyzer for CrowdSafe AI.
Evaluates zone-based crowd density, occupancy counts, congestion duration,
and assigns 4-tier risk levels: Normal (Green), Increasing (Yellow), High (Orange), Critical (Red).
"""

import time
from typing import List, Dict, Any, Tuple
from .config import RISK_LEVELS


class ZoneTracker:
    def __init__(self, zone_id: str):
        self.zone_id = zone_id
        self.congested_start_time: float = 0.0
        self.congested_duration: float = 0.0
        self.last_risk_level: str = "normal"
        self.last_alert_time: float = 0.0
        self.history_counts: List[int] = []

    def update(self, count: int, zone_cfg: Dict[str, Any], current_time: float) -> Tuple[str, float, bool, str]:
        """
        Updates the tracker with current count and calculates:
        - risk_level ("normal", "increasing", "high", "critical")
        - congested_duration (seconds)
        - should_alert (bool)
        - alert_reason (str)
        """
        normal_thresh = zone_cfg.get("normal_threshold", 6)
        inc_thresh = zone_cfg.get("increasing_threshold", 12)
        high_thresh = zone_cfg.get("high_threshold", 18)
        crit_thresh = zone_cfg.get("critical_threshold", 24)
        congestion_threshold_sec = zone_cfg.get("congestion_seconds_threshold", 4)

        # 1. Determine instantaneous risk level
        if count <= normal_thresh:
            instant_risk = "normal"
        elif count <= inc_thresh:
            instant_risk = "increasing"
        elif count <= crit_thresh:
            instant_risk = "high"
        else:
            instant_risk = "critical"

        # 2. Track congestion duration
        is_congested = (instant_risk in ["high", "critical"])

        if is_congested:
            if self.congested_start_time == 0.0:
                self.congested_start_time = current_time
            self.congested_duration = max(0.0, current_time - self.congested_start_time)
        else:
            self.congested_start_time = 0.0
            self.congested_duration = 0.0

        # Effective risk level can elevate if congested duration is prolonged
        effective_risk = instant_risk
        if instant_risk == "high" and self.congested_duration >= congestion_threshold_sec * 1.5:
            effective_risk = "critical"

        # 3. Alert Trigger Evaluation
        should_alert = False
        alert_reason = ""

        # Trigger alert if risk is High or Critical AND congestion duration threshold met
        if effective_risk in ["high", "critical"]:
            # Check if duration meets zone threshold
            if self.congested_duration >= congestion_threshold_sec:
                # Rate limit: alert every 8 seconds per zone unless escalation
                escalated = (effective_risk == "critical" and self.last_risk_level != "critical")
                cooldown_passed = (current_time - self.last_alert_time) > 8.0

                if cooldown_passed or escalated:
                    should_alert = True
                    self.last_alert_time = current_time
                    if effective_risk == "critical":
                        alert_reason = (
                            f"CRITICAL: {count} people detected (limit: {crit_thresh}). "
                            f"Congestion sustained for {self.congested_duration:.1f}s. "
                            f"High potential for surge bottleneck."
                        )
                    else:
                        alert_reason = (
                            f"HIGH DENSITY: {count} people in zone (limit: {high_thresh}). "
                            f"Congestion sustained for {self.congested_duration:.1f}s."
                        )

        self.last_risk_level = effective_risk
        self.history_counts.append(count)
        if len(self.history_counts) > 30:
            self.history_counts.pop(0)

        return effective_risk, round(self.congested_duration, 1), should_alert, alert_reason


class CrowdRiskAnalyzer:
    def __init__(self):
        self.zone_trackers: Dict[str, ZoneTracker] = {}

    def get_tracker(self, zone_id: str) -> ZoneTracker:
        if zone_id not in self.zone_trackers:
            self.zone_trackers[zone_id] = ZoneTracker(zone_id)
        return self.zone_trackers[zone_id]

    def analyze_frame_zones(
        self,
        frame_width: int,
        frame_height: int,
        detections: List[Dict[str, Any]],
        zones: List[Dict[str, Any]],
        current_time: float = None
    ) -> Tuple[Dict[str, Dict[str, Any]], str, List[Dict[str, Any]]]:
        """
        Calculates occupancy for each zone, analyzes risk level and flags alerts.
        Returns:
        - zone_statuses: {zone_id: {"risk_level": ..., "person_count": ..., "duration": ...}}
        - overall_camera_risk: highest risk level across all zones
        - alerts_to_generate: list of alert records to persist
        """
        if current_time is None:
            current_time = time.time()

        # Count people per zone
        zone_counts = {z["id"]: 0 for z in zones}

        for det in detections:
            cx, cy = det["center"]
            # Check which zone(s) contain this person
            for zone in zones:
                zx1 = int(zone["x_min"] * frame_width)
                zy1 = int(zone["y_min"] * frame_height)
                zx2 = int(zone["x_max"] * frame_width)
                zy2 = int(zone["y_max"] * frame_height)

                if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
                    zone_counts[zone["id"]] += 1

        zone_statuses = {}
        alerts_to_generate = []
        highest_risk_code = 0
        overall_risk = "normal"

        for zone in zones:
            zid = zone["id"]
            count = zone_counts[zid]
            tracker = self.get_tracker(zid)

            risk_level, duration, should_alert, reason = tracker.update(count, zone, current_time)

            risk_cfg = RISK_LEVELS.get(risk_level, RISK_LEVELS["normal"])
            if risk_cfg["code"] > highest_risk_code:
                highest_risk_code = risk_cfg["code"]
                overall_risk = risk_level

            zone_statuses[zid] = {
                "zone_id": zid,
                "name": zone["name"],
                "person_count": count,
                "risk_level": risk_level,
                "congested_duration": duration,
                "thresholds": {
                    "normal": zone.get("normal_threshold", 6),
                    "increasing": zone.get("increasing_threshold", 12),
                    "high": zone.get("high_threshold", 18),
                    "critical": zone.get("critical_threshold", 24),
                    "congestion_seconds": zone.get("congestion_seconds_threshold", 4)
                }
            }

            if should_alert:
                thresh_val = (zone.get("critical_threshold", 24)
                              if risk_level == "critical"
                              else zone.get("high_threshold", 18))
                alerts_to_generate.append({
                    "camera_id": zone["camera_id"],
                    "zone_id": zid,
                    "zone_name": zone["name"],
                    "risk_level": risk_level,
                    "person_count": count,
                    "threshold_exceeded": thresh_val,
                    "reason": reason
                })

        return zone_statuses, overall_risk, alerts_to_generate
