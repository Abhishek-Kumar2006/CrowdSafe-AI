import React, { useState, useEffect } from 'react';
import { X, Sliders, Save, Check, RefreshCw } from 'lucide-react';
import { Zone, ZoneThresholds } from '../types';
import { api } from '../services/api';

interface ThresholdSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  zones: Zone[];
  activeZoneId?: string | null;
  onThresholdsSaved: () => void;
}

export const ThresholdSettingsModal: React.FC<ThresholdSettingsModalProps> = ({
  isOpen,
  onClose,
  zones,
  activeZoneId,
  onThresholdsSaved,
}) => {
  const [selectedZoneId, setSelectedZoneId] = useState<string>('');
  const [thresholds, setThresholds] = useState<ZoneThresholds>({
    normal: 6,
    increasing: 12,
    high: 18,
    critical: 24,
    congestion_seconds: 4,
  });
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (zones.length > 0) {
      const targetId = activeZoneId && zones.some((z) => z.id === activeZoneId)
        ? activeZoneId
        : zones[0].id;
      setSelectedZoneId(targetId);
    }
  }, [zones, activeZoneId, isOpen]);

  useEffect(() => {
    const curZone = zones.find((z) => z.id === selectedZoneId);
    if (curZone) {
      setThresholds({
        normal: curZone.normal_threshold,
        increasing: curZone.increasing_threshold,
        high: curZone.high_threshold,
        critical: curZone.critical_threshold,
        congestion_seconds: curZone.congestion_seconds_threshold,
      });
      setSaveSuccess(false);
    }
  }, [selectedZoneId, zones]);

  if (!isOpen) return null;

  const handleSave = async () => {
    if (!selectedZoneId) return;
    try {
      setSaving(true);
      await api.updateZoneThresholds(selectedZoneId, thresholds);
      setSaveSuccess(true);
      onThresholdsSaved();
      setTimeout(() => setSaveSuccess(false), 2000);
    } catch (err) {
      console.error('Error saving thresholds:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-dark-850 border border-dark-700 rounded-2xl w-full max-w-lg p-6 shadow-2xl relative">
        <div className="flex items-center justify-between pb-4 border-b border-dark-700">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-dark-800 rounded-lg border border-dark-700 text-emerald-400">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-mono text-base font-bold text-white">Zone Safety Thresholds</h3>
              <p className="text-xs text-slate-400">Configure occupancy levels & congestion trigger time</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Zone Selector */}
        <div className="mt-4">
          <label className="block text-xs font-mono text-slate-300 mb-1.5 uppercase tracking-wider">
            Select Zone to Configure:
          </label>
          <select
            value={selectedZoneId}
            onChange={(e) => setSelectedZoneId(e.target.value)}
            className="w-full bg-dark-900 border border-dark-700 rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
          >
            {zones.map((z) => (
              <option key={z.id} value={z.id}>
                {z.name} (Current Cap: {z.critical_threshold})
              </option>
            ))}
          </select>
        </div>

        {/* Sliders & Thresholds */}
        <div className="mt-5 space-y-4">
          {/* Green - Normal */}
          <div className="p-3 bg-dark-900/60 rounded-xl border border-emerald-900/40">
            <div className="flex justify-between items-center text-xs font-mono mb-1.5">
              <span className="text-emerald-400 font-bold">● Green (Normal Limit):</span>
              <span className="text-white font-bold">{thresholds.normal} people</span>
            </div>
            <input
              type="range"
              min="1"
              max="50"
              value={thresholds.normal}
              onChange={(e) => setThresholds({ ...thresholds, normal: parseInt(e.target.value) || 1 })}
              className="w-full accent-emerald-500 cursor-pointer"
            />
          </div>

          {/* Yellow - Increasing */}
          <div className="p-3 bg-dark-900/60 rounded-xl border border-amber-900/40">
            <div className="flex justify-between items-center text-xs font-mono mb-1.5">
              <span className="text-amber-400 font-bold">● Yellow (Increasing Limit):</span>
              <span className="text-white font-bold">{thresholds.increasing} people</span>
            </div>
            <input
              type="range"
              min="2"
              max="70"
              value={thresholds.increasing}
              onChange={(e) => setThresholds({ ...thresholds, increasing: parseInt(e.target.value) || 2 })}
              className="w-full accent-amber-500 cursor-pointer"
            />
          </div>

          {/* Orange - High */}
          <div className="p-3 bg-dark-900/60 rounded-xl border border-orange-900/40">
            <div className="flex justify-between items-center text-xs font-mono mb-1.5">
              <span className="text-orange-400 font-bold">● Orange (High Density Limit):</span>
              <span className="text-white font-bold">{thresholds.high} people</span>
            </div>
            <input
              type="range"
              min="3"
              max="100"
              value={thresholds.high}
              onChange={(e) => setThresholds({ ...thresholds, high: parseInt(e.target.value) || 3 })}
              className="w-full accent-orange-500 cursor-pointer"
            />
          </div>

          {/* Red - Critical */}
          <div className="p-3 bg-dark-900/60 rounded-xl border border-red-900/40">
            <div className="flex justify-between items-center text-xs font-mono mb-1.5">
              <span className="text-red-400 font-bold">● Red (Critical Capacity):</span>
              <span className="text-white font-bold">{thresholds.critical} people</span>
            </div>
            <input
              type="range"
              min="5"
              max="150"
              value={thresholds.critical}
              onChange={(e) => setThresholds({ ...thresholds, critical: parseInt(e.target.value) || 5 })}
              className="w-full accent-red-500 cursor-pointer"
            />
          </div>

          {/* Congestion Duration Threshold */}
          <div className="p-3 bg-dark-900/60 rounded-xl border border-cyan-900/40">
            <div className="flex justify-between items-center text-xs font-mono mb-1.5">
              <span className="text-cyan-400 font-bold">⏱ Congestion Duration Trigger:</span>
              <span className="text-white font-bold">{thresholds.congestion_seconds} seconds</span>
            </div>
            <p className="text-[11px] text-slate-400 mb-2">
              Time high/critical density must persist continuously before triggering audible safety alarm.
            </p>
            <input
              type="range"
              min="1"
              max="15"
              value={thresholds.congestion_seconds}
              onChange={(e) => setThresholds({ ...thresholds, congestion_seconds: parseInt(e.target.value) || 1 })}
              className="w-full accent-cyan-500 cursor-pointer"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-6 pt-4 border-t border-dark-700 flex items-center justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg text-xs font-mono text-slate-400 hover:text-white bg-dark-800 hover:bg-dark-750 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-5 py-2 rounded-lg text-xs font-mono font-bold text-white bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 transition-colors flex items-center space-x-1.5 shadow-lg shadow-emerald-950"
          >
            {saveSuccess ? (
              <>
                <Check className="w-4 h-4 text-emerald-200" />
                <span>Updated in Database!</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>{saving ? 'Saving...' : 'Save Configuration'}</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
