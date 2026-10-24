import React, { useState, useEffect, useRef } from 'react';
import { DisclaimerBanner } from './components/DisclaimerBanner';
import { Navbar } from './components/Navbar';
import { MetricsBar } from './components/MetricsBar';
import { VideoPlayer } from './components/VideoPlayer';
import { ZoneRiskGrid } from './components/ZoneRiskGrid';
import { DensityHeatmap } from './components/DensityHeatmap';
import { AlertFeed } from './components/AlertFeed';
import { ThresholdSettingsModal } from './components/ThresholdSettingsModal';
import { AlertHistoryModal } from './components/AlertHistoryModal';
import { VideoUploaderModal } from './components/VideoUploaderModal';
import { soundManager } from './utils/audioAlert';
import { api } from './services/api';
import { Camera, Zone, LiveMetrics, Alert } from './types';

export const App: React.FC = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selectedCameraId, setSelectedCameraId] = useState<string>('');
  const [zones, setZones] = useState<Zone[]>([]);
  const [metrics, setMetrics] = useState<LiveMetrics | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);

  // Modals
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isThresholdsOpen, setIsThresholdsOpen] = useState(false);
  const [activeEditZoneId, setActiveEditZoneId] = useState<string | null>(null);

  // Audio alert tracking
  const lastCriticalAlertIdRef = useRef<string | null>(null);

  // 1. Initial Load: Fetch cameras list
  const loadCameras = async (preferredId?: string) => {
    try {
      const data = await api.getCameras();
      setCameras(data.cameras);
      if (data.cameras.length > 0) {
        const targetId = preferredId || (selectedCameraId && data.cameras.some((c) => c.id === selectedCameraId))
          ? preferredId || selectedCameraId
          : data.cameras[0].id;
        setSelectedCameraId(targetId);
      }
    } catch (err) {
      console.error('Error fetching cameras:', err);
    }
  };

  useEffect(() => {
    loadCameras();
  }, []);

  // 2. Fetch Zones when selected camera changes
  const loadZones = async (camId: string) => {
    if (!camId) return;
    try {
      const data = await api.getCameraDetails(camId);
      setZones(data.zones);
    } catch (err) {
      console.error('Error fetching zones:', err);
    }
  };

  useEffect(() => {
    if (selectedCameraId) {
      loadZones(selectedCameraId);
    }
  }, [selectedCameraId]);

  // 3. Polling for Live Metrics & Alerts (Every 1000ms)
  useEffect(() => {
    if (!selectedCameraId) return;

    let isMounted = true;
    const fetchMetrics = async () => {
      try {
        const live = await api.getLiveMetrics(selectedCameraId);
        if (!isMounted) return;
        setMetrics(live);

        if (live.recent_alerts) {
          setAlerts(live.recent_alerts);

          // Check for new critical unacknowledged alerts to sound chime
          const newestCrit = live.recent_alerts.find(
            (a) => a.risk_level === 'critical' && a.acknowledged === 0
          );
          if (newestCrit && newestCrit.id !== lastCriticalAlertIdRef.current) {
            lastCriticalAlertIdRef.current = newestCrit.id;
            soundManager.playCriticalAlarm();
          }
        }
      } catch (err) {
        console.warn('Metrics polling error:', err);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 1000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [selectedCameraId]);

  // Handlers
  const handleEditZone = (zoneId: string) => {
    setActiveEditZoneId(zoneId);
    setIsThresholdsOpen(true);
  };

  const handleTriggerSurge = async () => {
    if (!selectedCameraId) return;
    try {
      await api.triggerDemoSurge(selectedCameraId);
    } catch (err) {
      console.error('Surge trigger failed:', err);
    }
  };

  const handleUploadSuccess = async (newCamId: string) => {
    await loadCameras(newCamId);
    setSelectedCameraId(newCamId);
  };

  const handleLoadSample = async () => {
    try {
      await api.loadSampleVideo();
      await loadCameras('cam-sample-crowd');
      setSelectedCameraId('cam-sample-crowd');
    } catch (err) {
      console.error('Load sample failed:', err);
    }
  };

  const currentCam = cameras.find((c) => c.id === selectedCameraId);
  const cameraName = currentCam?.name || 'Gate 4 Main Concourse';
  const isSimulated = metrics?.is_simulated ?? true;

  return (
    <div className="min-h-screen bg-dark-900 text-slate-100 flex flex-col font-sans">
      {/* 1. Mandatory Disclaimer Banner */}
      <DisclaimerBanner />

      {/* 2. Top Tactical Security Navbar */}
      <Navbar
        cameras={cameras}
        selectedCameraId={selectedCameraId}
        onSelectCamera={(id) => setSelectedCameraId(id)}
        onOpenUpload={() => setIsUploadOpen(true)}
        onOpenHistory={() => setIsHistoryOpen(true)}
        onLoadSample={handleLoadSample}
        onTriggerSurge={handleTriggerSurge}
        isSimulated={isSimulated}
        surgeActive={metrics?.surge_active}
      />

      {/* 3. Main Security Control Room Workspace */}
      <main className="flex-1 p-4 max-w-[1720px] w-full mx-auto space-y-4">
        {/* Real-time KPI Metrics Header */}
        <MetricsBar metrics={metrics} />

        {/* Core Split Dashboard View */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 items-start">
          {/* Left Column: Live Video Stream + Zone Assessment Cards (7/12 cols) */}
          <div className="xl:col-span-7 space-y-4">
            <VideoPlayer
              cameraId={selectedCameraId}
              cameraName={cameraName}
              metrics={metrics}
              onOpenThresholds={() => {
                setActiveEditZoneId(null);
                setIsThresholdsOpen(true);
              }}
            />

            <ZoneRiskGrid
              zoneStatuses={metrics?.zone_statuses || {}}
              onEditZone={handleEditZone}
            />
          </div>

          {/* Right Column: Spatial Heatmap + Real-time Alert Feed (5/12 cols) */}
          <div className="xl:col-span-5 space-y-4">
            <DensityHeatmap
              zoneStatuses={metrics?.zone_statuses || {}}
            />

            <AlertFeed
              alerts={alerts}
              onAlertAcknowledged={() => {
                if (selectedCameraId) {
                  api.getLiveMetrics(selectedCameraId).then(setMetrics);
                }
              }}
            />
          </div>
        </div>
      </main>

      {/* Footer System Status Bar */}
      <footer className="bg-dark-850 border-t border-dark-750 px-4 py-2 text-[11px] font-mono text-slate-400 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-3">
          <span className="flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <strong className="text-slate-300">SYSTEM: ONLINE</strong>
          </span>
          <span>•</span>
          <span>SQLite Database: <span className="text-emerald-400">data/crowdsafe.db</span></span>
          <span>•</span>
          <span>YOLO Model: <span className="text-cyan-400">yolov8n.pt</span></span>
        </div>

        <div className="text-slate-500">
          CrowdSafe AI © Hackathon Demonstration Prototype • Decision Support Only
        </div>
      </footer>

      {/* Modals */}
      <ThresholdSettingsModal
        isOpen={isThresholdsOpen}
        onClose={() => setIsThresholdsOpen(false)}
        zones={zones}
        activeZoneId={activeEditZoneId}
        onThresholdsSaved={() => {
          if (selectedCameraId) loadZones(selectedCameraId);
        }}
      />

      <AlertHistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        cameraId={selectedCameraId}
      />

      <VideoUploaderModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={handleUploadSuccess}
        onLoadSampleSuccess={() => loadCameras('cam-sample-crowd')}
      />
    </div>
  );
};

export default App;
