import React from 'react';
import { Users, AlertTriangle, ShieldCheck, Activity, Cpu } from 'lucide-react';
import { LiveMetrics, RiskLevel } from '../types';

interface MetricsBarProps {
  metrics: LiveMetrics | null;
}

const RISK_BADGES: Record<RiskLevel, { label: string; bg: string; text: string; border: string; glow: string }> = {
  normal: {
    label: 'NORMAL',
    bg: 'bg-emerald-950/60',
    text: 'text-emerald-400',
    border: 'border-emerald-600/50',
    glow: 'shadow-emerald-950/50',
  },
  increasing: {
    label: 'INCREASING',
    bg: 'bg-amber-950/60',
    text: 'text-amber-400',
    border: 'border-amber-600/50',
    glow: 'shadow-amber-950/50',
  },
  high: {
    label: 'HIGH DENSITY',
    bg: 'bg-orange-950/60',
    text: 'text-orange-400',
    border: 'border-orange-600/50',
    glow: 'shadow-orange-950/50',
  },
  critical: {
    label: 'CRITICAL RISK',
    bg: 'bg-red-950/80',
    text: 'text-red-400',
    border: 'border-red-600/70',
    glow: 'shadow-red-950/80 animate-pulse',
  },
};

export const MetricsBar: React.FC<MetricsBarProps> = ({ metrics }) => {
  const riskLevel = metrics?.overall_risk_level || 'normal';
  const riskBadge = RISK_BADGES[riskLevel];
  const totalPax = metrics?.total_people_count ?? 0;
  const activeAlerts = metrics?.active_alerts_count ?? 0;
  const engine = metrics?.detection_engine || 'YOLOv8n';

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {/* 1. Total Detected People */}
      <div className="bg-dark-850 border border-dark-750 rounded-xl p-3.5 shadow-lg relative overflow-hidden">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Detected People</span>
          <div className="p-2 bg-dark-800 rounded-lg border border-dark-700">
            <Users className="w-4 h-4 text-emerald-400" />
          </div>
        </div>
        <div className="mt-2 flex items-baseline space-x-2">
          <span className="text-2xl font-bold font-mono text-white tracking-tight">{totalPax}</span>
          <span className="text-xs text-slate-400 font-mono">persons in frame</span>
        </div>
        <div className="mt-1 flex items-center space-x-1.5 text-[11px] text-slate-500 font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span>Real-time tracker</span>
        </div>
      </div>

      {/* 2. Current Risk Level */}
      <div
        className={`bg-dark-850 border rounded-xl p-3.5 shadow-lg relative overflow-hidden transition-all ${riskBadge.border} ${riskBadge.glow}`}
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Crowd Risk Level</span>
          <div className="p-2 bg-dark-800 rounded-lg border border-dark-700">
            {riskLevel === 'critical' ? (
              <AlertTriangle className="w-4 h-4 text-red-400 animate-bounce" />
            ) : riskLevel === 'high' ? (
              <AlertTriangle className="w-4 h-4 text-orange-400" />
            ) : (
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
            )}
          </div>
        </div>
        <div className="mt-2 flex items-center space-x-2">
          <span className={`text-xl font-bold font-mono tracking-tight ${riskBadge.text}`}>
            {riskBadge.label}
          </span>
        </div>
        <div className="mt-1 flex items-center space-x-1.5 text-[11px] text-slate-400 font-mono">
          <span>Threshold & congestion analysis</span>
        </div>
      </div>

      {/* 3. Active Alerts */}
      <div className="bg-dark-850 border border-dark-750 rounded-xl p-3.5 shadow-lg relative overflow-hidden">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">Active Alerts</span>
          <div className="p-2 bg-dark-800 rounded-lg border border-dark-700">
            <Activity className="w-4 h-4 text-amber-400" />
          </div>
        </div>
        <div className="mt-2 flex items-baseline space-x-2">
          <span className={`text-2xl font-bold font-mono tracking-tight ${activeAlerts > 0 ? 'text-amber-400' : 'text-slate-300'}`}>
            {activeAlerts}
          </span>
          <span className="text-xs text-slate-400 font-mono">unacknowledged</span>
        </div>
        <div className="mt-1 text-[11px] text-slate-500 font-mono">
          {activeAlerts > 0 ? 'Action required by operator' : 'All clear / Acknowledged'}
        </div>
      </div>

      {/* 4. Model / Source Status */}
      <div className="bg-dark-850 border border-dark-750 rounded-xl p-3.5 shadow-lg relative overflow-hidden">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">AI Vision Engine</span>
          <div className="p-2 bg-dark-800 rounded-lg border border-dark-700">
            <Cpu className="w-4 h-4 text-cyan-400" />
          </div>
        </div>
        <div className="mt-2 truncate">
          <span className="text-sm font-bold font-mono text-cyan-300 truncate block">
            {engine}
          </span>
        </div>
        <div className="mt-1 flex items-center space-x-1.5 text-[11px] text-slate-400 font-mono">
          <span className={`w-1.5 h-1.5 rounded-full ${metrics?.is_simulated ? 'bg-amber-500' : 'bg-emerald-500'}`} />
          <span>{metrics?.is_simulated ? 'Demo Simulation Mode' : 'Surveillance Stream'}</span>
        </div>
      </div>
    </div>
  );
};
