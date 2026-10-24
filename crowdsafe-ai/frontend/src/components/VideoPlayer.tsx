import React, { useState, useRef, useEffect } from 'react';
import {
  Video,
  Maximize2,
  RefreshCw,
  Sliders,
  Shield,
  Eye,
  Camera as CameraIcon,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { LiveMetrics } from '../types';

interface VideoPlayerProps {
  cameraId: string;
  cameraName: string;
  metrics: LiveMetrics | null;
  onOpenThresholds: () => void;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
  cameraId,
  cameraName,
  metrics,
  onOpenThresholds
}) => {
  const [streamKey, setStreamKey] = useState<number>(Date.now());
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const retryTimeoutRef = useRef<any>(null);

  // Switch stream immediately when camera changes
  useEffect(() => {
    setStreamKey(Date.now());
  }, [cameraId]);

  const streamUrl = `${api.getVideoStreamUrl(cameraId)}?t=${streamKey}`;
  const isSimulated = metrics?.is_simulated ?? true;
  const currentRisk = metrics?.overall_risk_level || 'normal';

  const handleRefreshStream = () => {
    setStreamKey(Date.now());
  };

  const handleImageError = () => {
    console.warn('Stream interrupted, auto-reconnecting in 1.5s...');
    if (retryTimeoutRef.current) clearTimeout(retryTimeoutRef.current);
    retryTimeoutRef.current = setTimeout(() => {
      setStreamKey(Date.now());
    }, 1500);
  };

  const handleToggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().catch((err) => {
        console.error('Fullscreen error:', err);
      });
      setIsFullscreen(true);
    } else {
      document.exitFullscreen().catch((err) => {
        console.error('Exit fullscreen error:', err);
      });
      setIsFullscreen(false);
    }
  };

  return (
    <div
      ref={containerRef}
      className="bg-dark-850 border border-dark-750 rounded-xl overflow-hidden shadow-2xl flex flex-col relative group"
    >
      {/* Top Feed Header */}
      <div className="bg-dark-900/90 border-b border-dark-700/80 px-4 py-2.5 flex items-center justify-between z-10 backdrop-blur-md">
        <div className="flex items-center space-x-2.5">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-mono text-xs font-semibold text-white tracking-wide">
            FEED: {cameraName}
          </span>
          <span className="text-[10px] text-slate-400 font-mono hidden md:inline">
            [{cameraId}]
          </span>
        </div>

        {/* Clear Truth-in-AI Mode Badge */}
        <div className="flex items-center space-x-2">
          {isSimulated ? (
            <div className="px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/40 text-amber-400 text-[11px] font-mono font-medium flex items-center space-x-1.5 shadow-sm">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping" />
              <span>SIMULATED DEMO DATA</span>
            </div>
          ) : (
            <div className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/40 text-emerald-400 text-[11px] font-mono font-medium flex items-center space-x-1.5 shadow-sm">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>REAL YOLOv8 INFERENCE</span>
            </div>
          )}

          <div className="h-4 w-px bg-dark-700" />

          {/* Quick Actions */}
          <button
            onClick={onOpenThresholds}
            className="p-1.5 rounded text-slate-400 hover:text-slate-200 hover:bg-dark-800 transition-colors"
            title="Configure Zone Thresholds"
          >
            <Sliders className="w-4 h-4" />
          </button>
          <button
            onClick={handleRefreshStream}
            className="p-1.5 rounded text-slate-400 hover:text-slate-200 hover:bg-dark-800 transition-colors"
            title="Refresh Video Stream"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={handleToggleFullscreen}
            className="p-1.5 rounded text-slate-400 hover:text-slate-200 hover:bg-dark-800 transition-colors"
            title="Toggle Fullscreen"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Video Stream Container */}
      <div className="relative bg-black flex-1 min-h-[360px] max-h-[560px] flex items-center justify-center overflow-hidden">
        {cameraId ? (
          <img
            key={streamKey}
            src={streamUrl}
            alt={`CCTV Stream - ${cameraName}`}
            className="w-full h-full object-contain"
            onError={handleImageError}
          />
        ) : (
          <div className="text-slate-500 font-mono text-xs flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            <span>Connecting to camera feed...</span>
          </div>
        )}

        {/* Tactical Crosshair / Corner Brackets */}
        <div className="absolute top-3 left-3 pointer-events-none text-emerald-500/30 text-xs font-mono">
          ┌ REC [SEC-01]
        </div>
        <div className="absolute top-3 right-3 pointer-events-none text-emerald-500/30 text-xs font-mono">
          YOLO-AI ┐
        </div>
        <div className="absolute bottom-3 left-3 pointer-events-none text-emerald-500/30 text-xs font-mono">
          └ 30 FPS
        </div>
        <div className="absolute bottom-3 right-3 pointer-events-none text-emerald-500/30 text-xs font-mono">
          CROWDSAFE ┘
        </div>

        {/* Video Processing Status Badge if any */}
        {metrics?.status === 'analyzing' && (
          <div className="absolute bottom-4 left-4 bg-dark-900/80 border border-emerald-500/40 text-emerald-400 px-3 py-1 rounded text-xs font-mono backdrop-blur-sm flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            <span>Analyzing Frame {metrics.current_frame} / {metrics.total_frames || 'Live'}</span>
          </div>
        )}

        {metrics?.error && (
          <div className="absolute inset-0 bg-dark-900/90 flex flex-col items-center justify-center p-6 text-center z-20">
            <AlertCircle className="w-10 h-10 text-rose-500 mb-2" />
            <h4 className="text-white font-mono font-bold text-sm">Stream Processing Error</h4>
            <p className="text-slate-400 text-xs mt-1 max-w-md">{metrics.error}</p>
            <button
              onClick={handleRefreshStream}
              className="mt-4 px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-mono"
            >
              Retry Connection
            </button>
          </div>
        )}
      </div>

      {/* Bottom Feed Status Bar */}
      <div className="bg-dark-900 border-t border-dark-700/80 px-4 py-2 flex items-center justify-between text-xs font-mono text-slate-400">
        <div className="flex items-center space-x-3">
          <span className="flex items-center space-x-1.5">
            <Eye className="w-3.5 h-3.5 text-cyan-400" />
            <span>Detection: <strong className="text-slate-200">{metrics?.detection_engine || 'YOLOv8'}</strong></span>
          </span>
          <span>•</span>
          <span>Total People: <strong className="text-emerald-400">{metrics?.total_people_count ?? 0}</strong></span>
        </div>

        <div className="flex items-center space-x-2">
          <span>Risk Status:</span>
          <span
            className={`font-bold uppercase ${
              currentRisk === 'critical'
                ? 'text-red-400 animate-pulse'
                : currentRisk === 'high'
                ? 'text-orange-400'
                : currentRisk === 'increasing'
                ? 'text-amber-400'
                : 'text-emerald-400'
            }`}
          >
            {currentRisk}
          </span>
        </div>
      </div>
    </div>
  );
};
