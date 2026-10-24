import React from 'react';
import { Layers, Clock, AlertTriangle, ShieldCheck, Sliders } from 'lucide-react';
import { ZoneStatus, RiskLevel } from '../types';

interface ZoneRiskGridProps {
  zoneStatuses: Record<string, ZoneStatus>;
  onEditZone: (zoneId: string) => void;
}

const RISK_MAP: Record<RiskLevel, { text: string; bg: string; border: string; bar: string }> = {
  normal: {
    text: 'text-emerald-400',
    bg: 'bg-emerald-950/40',
    border: 'border-emerald-600/30',
    bar: 'bg-emerald-500',
  },
  increasing: {
    text: 'text-amber-400',
    bg: 'bg-amber-950/40',
    border: 'border-amber-600/40',
    bar: 'bg-amber-500',
  },
  high: {
    text: 'text-orange-400',
    bg: 'bg-orange-950/40',
    border: 'border-orange-600/50',
    bar: 'bg-orange-500',
  },
  critical: {
    text: 'text-red-400',
    bg: 'bg-red-950/60',
    border: 'border-red-600/70',
    bar: 'bg-red-500 animate-pulse',
  },
};

export const ZoneRiskGrid: React.FC<ZoneRiskGridProps> = ({ zoneStatuses, onEditZone }) => {
  const zoneList = Object.values(zoneStatuses);

  if (zoneList.length === 0) {
    return (
      <div className="bg-dark-850 border border-dark-750 rounded-xl p-6 text-center text-slate-400 font-mono text-xs">
        <Layers className="w-8 h-8 text-slate-600 mx-auto mb-2" />
        No active zones configured for this camera feed.
      </div>
    );
  }

  return (
    <div className="bg-dark-850 border border-dark-750 rounded-xl p-4 shadow-lg">
      <div className="flex items-center justify-between mb-3 border-b border-dark-700/80 pb-2">
        <div className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-emerald-400" />
          <h3 className="font-mono text-xs font-semibold text-white uppercase tracking-wider">
            Zone Risk & Occupancy Assessment
          </h3>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">
          {zoneList.length} Monitored Sectors
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {zoneList.map((z) => {
          const riskStyle = RISK_MAP[z.risk_level] || RISK_MAP.normal;
          const critThresh = z.thresholds?.critical || 24;
          const normalThresh = z.thresholds?.normal || 6;
          const percent = Math.min(100, Math.round((z.person_count / critThresh) * 100));
          const isCongested = z.congested_duration > 0;
          const congThresh = z.thresholds?.congestion_seconds || 4;

          return (
            <div
              key={z.zone_id}
              className={`p-3 rounded-lg border bg-dark-800/80 transition-all ${riskStyle.border} hover:border-slate-500`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-mono text-xs font-semibold text-slate-100">{z.name}</h4>
                  <div className="flex items-center space-x-2 mt-0.5">
                    <span className={`text-[10px] font-mono font-bold uppercase tracking-wider ${riskStyle.text}`}>
                      ● {z.risk_level} Risk
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="text-[10px] font-mono text-slate-400">
                      Capacity limit: {critThresh} pax
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => onEditZone(z.zone_id)}
                  className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-dark-700 transition-colors"
                  title="Configure Thresholds"
                >
                  <Sliders className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Occupancy Counter & Meter */}
              <div className="mt-3">
                <div className="flex items-baseline justify-between text-xs font-mono mb-1">
                  <span className="text-slate-400">
                    Occupancy: <strong className="text-white text-sm">{z.person_count}</strong> people
                  </span>
                  <span className="text-slate-400">{percent}% load</span>
                </div>

                <div className="w-full bg-dark-900 rounded-full h-2 overflow-hidden border border-dark-700">
                  <div
                    className={`h-full transition-all duration-300 ${riskStyle.bar}`}
                    style={{ width: `${percent}%` }}
                  />
                </div>
              </div>

              {/* Congestion Duration Tag */}
              <div className="mt-2.5 pt-2 border-t border-dark-700/60 flex items-center justify-between text-[11px] font-mono">
                <div className="flex items-center space-x-1.5 text-slate-400">
                  <Clock className="w-3 h-3 text-slate-500" />
                  <span>
                    Congestion Duration:{' '}
                    <strong className={isCongested ? 'text-amber-400 font-bold' : 'text-slate-400'}>
                      {z.congested_duration.toFixed(1)}s
                    </strong>
                  </span>
                </div>
                {isCongested && (
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] ${
                      z.congested_duration >= congThresh
                        ? 'bg-red-950/80 text-red-300 border border-red-700'
                        : 'bg-amber-950/80 text-amber-300 border border-amber-700'
                    }`}
                  >
                    {z.congested_duration >= congThresh ? 'ALARM TRIGGERED' : `> ${congThresh}s limit`}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
