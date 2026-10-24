import React from 'react';
import { Activity, MapPin, Grid, TrendingUp } from 'lucide-react';
import { ZoneStatus, RiskLevel } from '../types';

interface DensityHeatmapProps {
  zoneStatuses: Record<string, ZoneStatus>;
}

const HEAT_COLORS: Record<RiskLevel, { bg: string; fill: string; border: string; glow: string }> = {
  normal: { bg: 'bg-emerald-950/30', fill: 'bg-emerald-500/20', border: 'border-emerald-600/40', glow: 'shadow-emerald-950/30' },
  increasing: { bg: 'bg-amber-950/40', fill: 'bg-amber-500/30', border: 'border-amber-600/50', glow: 'shadow-amber-950/40' },
  high: { bg: 'bg-orange-950/50', fill: 'bg-orange-500/40', border: 'border-orange-600/60', glow: 'shadow-orange-950/50' },
  critical: { bg: 'bg-red-950/70', fill: 'bg-red-500/60', border: 'border-red-600/80', glow: 'shadow-red-950/70 animate-pulse' },
};

export const DensityHeatmap: React.FC<DensityHeatmapProps> = ({ zoneStatuses }) => {
  const zones = Object.values(zoneStatuses);

  return (
    <div className="bg-dark-850 border border-dark-750 rounded-xl p-4 shadow-lg flex flex-col h-full">
      <div className="flex items-center justify-between pb-3 border-b border-dark-700/80 mb-3">
        <div className="flex items-center space-x-2">
          <Grid className="w-4 h-4 text-cyan-400" />
          <h3 className="font-mono text-xs font-semibold text-white uppercase tracking-wider">
            Spatial Density Heat Matrix
          </h3>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">
          2D Topology Grid
        </span>
      </div>

      {/* 2D Topological Heatmap Grid */}
      <div className="grid grid-cols-2 gap-2.5 flex-1 min-h-[180px]">
        {zones.length === 0 ? (
          <div className="col-span-2 flex items-center justify-center text-slate-500 text-xs font-mono">
            Awaiting zone telemetry...
          </div>
        ) : (
          zones.map((zone) => {
            const heat = HEAT_COLORS[zone.risk_level] || HEAT_COLORS.normal;
            const critThresh = zone.thresholds?.critical || 24;
            const densityRatio = Math.min(1.0, zone.person_count / critThresh);
            const percentage = Math.round(densityRatio * 100);

            return (
              <div
                key={zone.zone_id}
                className={`p-3 rounded-lg border flex flex-col justify-between transition-all ${heat.bg} ${heat.border} ${heat.glow}`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-slate-200 truncate">
                    {zone.name.split('-')[0].trim()}
                  </span>
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-bold uppercase ${
                      zone.risk_level === 'critical'
                        ? 'bg-red-950 text-red-400 border border-red-700 animate-pulse'
                        : zone.risk_level === 'high'
                        ? 'bg-orange-950 text-orange-400 border border-orange-700'
                        : zone.risk_level === 'increasing'
                        ? 'bg-amber-950 text-amber-400 border border-amber-700'
                        : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                    }`}
                  >
                    {zone.risk_level}
                  </span>
                </div>

                {/* Heat Density Visualization Circle / Meter */}
                <div className="my-2 flex items-center space-x-3">
                  <div className="relative w-12 h-12 flex items-center justify-center shrink-0">
                    <svg className="w-12 h-12 transform -rotate-90">
                      <circle
                        cx="24"
                        cy="24"
                        r="18"
                        stroke="currentColor"
                        strokeWidth="3.5"
                        className="text-dark-700"
                        fill="transparent"
                      />
                      <circle
                        cx="24"
                        cy="24"
                        r="18"
                        stroke="currentColor"
                        strokeWidth="3.5"
                        strokeDasharray={113}
                        strokeDashoffset={113 - (113 * percentage) / 100}
                        strokeLinecap="round"
                        className={`transition-all duration-300 ${
                          zone.risk_level === 'critical'
                            ? 'text-red-500'
                            : zone.risk_level === 'high'
                            ? 'text-orange-500'
                            : zone.risk_level === 'increasing'
                            ? 'text-amber-500'
                            : 'text-emerald-500'
                        }`}
                        fill="transparent"
                      />
                    </svg>
                    <span className="absolute text-[10px] font-mono font-bold text-white">
                      {percentage}%
                    </span>
                  </div>

                  <div className="text-xs font-mono">
                    <div className="text-slate-300 font-bold">{zone.person_count} People</div>
                    <div className="text-[10px] text-slate-400">
                      Threshold: {critThresh}
                    </div>
                  </div>
                </div>

                <div className="text-[10px] font-mono text-slate-400 flex items-center justify-between pt-1 border-t border-dark-700/50">
                  <span>Congestion:</span>
                  <span className={zone.congested_duration > 0 ? 'text-amber-400 font-bold' : 'text-slate-400'}>
                    {zone.congested_duration.toFixed(1)}s
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Legend */}
      <div className="mt-3 pt-2.5 border-t border-dark-700/80 flex items-center justify-between text-[10px] font-mono text-slate-400">
        <span className="flex items-center space-x-1">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span>Normal</span>
        </span>
        <span className="flex items-center space-x-1">
          <span className="w-2 h-2 rounded-full bg-amber-500" />
          <span>Increasing</span>
        </span>
        <span className="flex items-center space-x-1">
          <span className="w-2 h-2 rounded-full bg-orange-500" />
          <span>High</span>
        </span>
        <span className="flex items-center space-x-1">
          <span className="w-2 h-2 rounded-full bg-red-500" />
          <span>Critical</span>
        </span>
      </div>
    </div>
  );
};
