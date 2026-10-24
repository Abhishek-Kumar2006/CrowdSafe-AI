export type RiskLevel = 'normal' | 'increasing' | 'high' | 'critical';

export interface Camera {
  id: string;
  name: string;
  location: string;
  status: 'active' | 'offline' | 'analyzing' | 'simulated';
  video_source: string;
  fps: number;
  created_at: string;
}

export interface ZoneThresholds {
  normal: number;
  increasing: number;
  high: number;
  critical: number;
  congestion_seconds: number;
}

export interface Zone {
  id: string;
  camera_id: string;
  name: string;
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  normal_threshold: number;
  increasing_threshold: number;
  high_threshold: number;
  critical_threshold: number;
  congestion_seconds_threshold: number;
}

export interface ZoneStatus {
  zone_id: string;
  name: string;
  person_count: number;
  risk_level: RiskLevel;
  congested_duration: number;
  thresholds: ZoneThresholds;
}

export interface Alert {
  id: string;
  camera_id: string;
  zone_id: string;
  zone_name: string;
  timestamp: string;
  risk_level: RiskLevel;
  person_count: number;
  threshold_exceeded: number;
  reason: string;
  acknowledged: number;
  acknowledged_at?: string;
  acknowledged_by?: string;
}

export interface LiveMetrics {
  camera_id: string;
  camera_name: string;
  is_simulated: boolean;
  detection_engine: string;
  total_people_count: number;
  overall_risk_level: RiskLevel;
  zone_statuses: Record<string, ZoneStatus>;
  active_alerts_count: number;
  recent_alerts: Alert[];
  current_frame?: number;
  total_frames?: number;
  status?: string;
  error?: string | null;
  surge_active?: boolean;
  timestamp: number;
}

export interface Observation {
  id: number;
  camera_id: string;
  zone_id: string;
  timestamp: string;
  person_count: number;
  risk_level: RiskLevel;
  congested_duration_sec: number;
}
