import { Camera, LiveMetrics, Zone, Alert, Observation, ZoneThresholds } from '../types';

const API_BASE = '/api';

export const api = {
  async getSystemStatus() {
    const res = await fetch(`${API_BASE}/status`);
    if (!res.ok) throw new Error('Failed to fetch system status');
    return res.json();
  },

  async getCameras(): Promise<{ cameras: Camera[] }> {
    const res = await fetch(`${API_BASE}/cameras`);
    if (!res.ok) throw new Error('Failed to fetch cameras');
    return res.json();
  },

  async getCameraDetails(cameraId: string): Promise<{ camera: Camera; zones: Zone[] }> {
    const res = await fetch(`${API_BASE}/cameras/${cameraId}`);
    if (!res.ok) throw new Error('Failed to fetch camera details');
    return res.json();
  },

  async getLiveMetrics(cameraId: string): Promise<LiveMetrics> {
    const res = await fetch(`${API_BASE}/cameras/${cameraId}/live-metrics`);
    if (!res.ok) throw new Error('Failed to fetch live metrics');
    return res.json();
  },

  async updateZoneThresholds(zoneId: string, thresholds: ZoneThresholds) {
    const res = await fetch(`${API_BASE}/zones/${zoneId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        normal_threshold: thresholds.normal,
        increasing_threshold: thresholds.increasing,
        high_threshold: thresholds.high,
        critical_threshold: thresholds.critical,
        congestion_seconds_threshold: thresholds.congestion_seconds,
      }),
    });
    if (!res.ok) throw new Error('Failed to update zone thresholds');
    return res.json();
  },

  async uploadVideo(file: File, cameraName?: string, location?: string) {
    const formData = new FormData();
    formData.append('file', file);
    if (cameraName) formData.append('camera_name', cameraName);
    if (location) formData.append('location', location);

    const res = await fetch(`${API_BASE}/videos/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async loadSampleVideo() {
    const res = await fetch(`${API_BASE}/videos/load-sample`, {
      method: 'POST',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Load sample failed' }));
      throw new Error(err.detail || 'Failed to load sample crowd video');
    }
    return res.json();
  },

  async getAlerts(cameraId?: string, activeOnly: boolean = false, limit: number = 50): Promise<{ alerts: Alert[] }> {
    const params = new URLSearchParams();
    if (cameraId) params.append('camera_id', cameraId);
    if (activeOnly) params.append('active_only', 'true');
    params.append('limit', limit.toString());

    const res = await fetch(`${API_BASE}/alerts?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },

  async acknowledgeAlert(alertId: string, acknowledgedBy: string = 'Security Operator') {
    const res = await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ acknowledged_by: acknowledgedBy }),
    });
    if (!res.ok) throw new Error('Failed to acknowledge alert');
    return res.json();
  },

  async getObservationHistory(cameraId: string, limit: number = 40): Promise<{ observations: Observation[] }> {
    const res = await fetch(`${API_BASE}/observations/history?camera_id=${cameraId}&limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch observations');
    return res.json();
  },

  async triggerDemoSurge(cameraId: string) {
    const res = await fetch(`${API_BASE}/demo/trigger-surge?camera_id=${cameraId}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to trigger demo surge');
    return res.json();
  },

  getVideoStreamUrl(cameraId: string) {
    return `${API_BASE}/cameras/${cameraId}/stream`;
  }
};
