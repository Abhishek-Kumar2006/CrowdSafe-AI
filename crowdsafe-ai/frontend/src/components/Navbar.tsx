import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  UploadCloud,
  FileVideo,
  Flame,
  Volume2,
  VolumeX,
  History,
  Activity,
  Cpu,
  Layers
} from 'lucide-react';
import { soundManager } from '../utils/audioAlert';
import { Camera } from '../types';

interface NavbarProps {
  cameras: Camera[];
  selectedCameraId: string;
  onSelectCamera: (cameraId: string) => void;
  onOpenUpload: () => void;
  onOpenHistory: () => void;
  onLoadSample: () => void;
  onTriggerSurge: () => void;
  isSimulated: boolean;
  surgeActive?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  cameras,
  selectedCameraId,
  onSelectCamera,
  onOpenUpload,
  onOpenHistory,
  onLoadSample,
  onTriggerSurge,
  isSimulated,
  surgeActive
}) => {
  const [timeStr, setTimeStr] = useState<string>('');
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('en-US', { hour12: false }) + ' UTC');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const toggleSound = () => {
    soundManager.enabled = !soundEnabled;
    setSoundEnabled(!soundEnabled);
    if (!soundEnabled) {
      soundManager.playAcknowledgeBeep();
    }
  };

  return (
    <header className="bg-dark-850 border-b border-dark-700/80 px-4 py-2.5 flex items-center justify-between shadow-xl">
      {/* Brand & Status */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2.5">
          <div className="bg-gradient-to-br from-emerald-500 to-teal-700 p-2 rounded-lg shadow-lg shadow-emerald-900/30 border border-emerald-400/30">
            <ShieldAlert className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono font-bold text-base tracking-wider text-white">
                CROWDSAFE<span className="text-emerald-400">.AI</span>
              </span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 font-semibold tracking-wider">
                PROTOTYPE
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Crowd Density & Stampede Early Warning</p>
          </div>
        </div>

        <div className="h-6 w-px bg-dark-700 hidden sm:block" />

        {/* Camera Selector */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400 font-mono hidden md:inline">FEED:</span>
          <select
            value={selectedCameraId}
            onChange={(e) => onSelectCamera(e.target.value)}
            className="bg-dark-800 text-slate-200 text-xs rounded border border-dark-600 px-2.5 py-1.5 focus:outline-none focus:border-emerald-500 font-mono tracking-tight"
          >
            {cameras.map((cam) => (
              <option key={cam.id} value={cam.id}>
                {cam.status === 'simulated' ? '🎮 [DEMO] ' : '📹 [REAL] '}
                {cam.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Center Live Pill & Telemetry */}
      <div className="hidden lg:flex items-center space-x-3">
        {isSimulated ? (
          <div className="flex items-center space-x-2 px-3 py-1 bg-amber-950/40 border border-amber-600/40 rounded-full text-amber-400 text-xs font-mono font-medium">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
            <span>DEMO SIMULATION FEED</span>
          </div>
        ) : (
          <div className="flex items-center space-x-2 px-3 py-1 bg-emerald-950/40 border border-emerald-600/40 rounded-full text-emerald-400 text-xs font-mono font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>REAL YOLOv8 DETECTION ACTIVE</span>
          </div>
        )}

        <div className="text-xs font-mono text-slate-400 bg-dark-900/60 px-2.5 py-1 rounded border border-dark-700">
          {timeStr}
        </div>
      </div>

      {/* Control Actions */}
      <div className="flex items-center space-x-2">
        {/* Judge Demo Surge Trigger Button */}
        {isSimulated && (
          <button
            onClick={onTriggerSurge}
            disabled={surgeActive}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-semibold font-mono tracking-wider transition-all shadow-md ${
              surgeActive
                ? 'bg-rose-950 text-rose-300 border border-rose-600 animate-pulse'
                : 'bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/40 hover:border-rose-400'
            }`}
            title="Inject high crowd surge to demonstrate critical alarm state"
          >
            <Flame className="w-3.5 h-3.5 text-rose-400" />
            <span>{surgeActive ? 'SURGE ACTIVE' : 'TEST SURGE'}</span>
          </button>
        )}

        {/* 1-Click Real Sample Crowd Video */}
        <button
          onClick={onLoadSample}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium font-mono text-cyan-300 bg-cyan-950/40 border border-cyan-800/60 hover:bg-cyan-900/40 hover:border-cyan-500 transition-colors"
          title="Instantly process bundled crowd footage using real YOLOv8"
        >
          <FileVideo className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">SAMPLE YOLO</span>
        </button>

        {/* Upload Custom Video Button */}
        <button
          onClick={onOpenUpload}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded text-xs font-medium font-mono text-emerald-300 bg-emerald-950/40 border border-emerald-800/60 hover:bg-emerald-900/40 hover:border-emerald-500 transition-colors"
          title="Upload prerecorded surveillance video"
        >
          <UploadCloud className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">UPLOAD VIDEO</span>
        </button>

        {/* Alert History Modal Button */}
        <button
          onClick={onOpenHistory}
          className="p-1.5 rounded text-slate-300 bg-dark-800 hover:bg-dark-750 border border-dark-600 hover:border-slate-400 transition-colors"
          title="View Alert History Database"
        >
          <History className="w-4 h-4" />
        </button>

        {/* Audio Mute/Unmute */}
        <button
          onClick={toggleSound}
          className={`p-1.5 rounded border transition-colors ${
            soundEnabled
              ? 'bg-dark-800 text-emerald-400 border-dark-600 hover:border-emerald-500'
              : 'bg-dark-800 text-slate-500 border-dark-700 hover:border-slate-500'
          }`}
          title={soundEnabled ? 'Mute alarm audio' : 'Unmute alarm audio'}
        >
          {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
        </button>
      </div>
    </header>
  );
};
