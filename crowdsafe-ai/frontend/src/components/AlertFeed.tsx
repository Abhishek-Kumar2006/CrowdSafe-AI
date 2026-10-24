import React, { useState } from 'react';
import { AlertTriangle, CheckCircle2, Bell, ShieldAlert, Check } from 'lucide-react';
import { Alert, RiskLevel } from '../types';
import { api } from '../services/api';
import { soundManager } from '../utils/audioAlert';

interface AlertFeedProps {
  alerts: Alert[];
  onAlertAcknowledged: () => void;
}

const RISK_BADGE: Record<RiskLevel, { text: string; bg: string; border: string }> = {
  normal: { text: 'text-emerald-400', bg: 'bg-emerald-950/60', border: 'border-emerald-600/40' },
  increasing: { text: 'text-amber-400', bg: 'bg-amber-950/60', border: 'border-amber-600/40' },
  high: { text: 'text-orange-400', bg: 'bg-orange-950/60', border: 'border-orange-600/40' },
  critical: { text: 'text-red-400', bg: 'bg-red-950/80', border: 'border-red-600/60' },
};

export const AlertFeed: React.FC<AlertFeedProps> = ({ alerts, onAlertAcknowledged }) => {
  const [filter, setFilter] = useState<'all' | 'active' | 'critical'>('all');
  const [acknowledgingId, setAcknowledgingId] = useState<string | null>(null);

  const filteredAlerts = alerts.filter((a) => {
    if (filter === 'active') return a.acknowledged === 0;
    if (filter === 'critical') return a.risk_level === 'critical';
    return true;
  });

  const handleAcknowledge = async (alertId: string) => {
    try {
      setAcknowledgingId(alertId);
      await api.acknowledgeAlert(alertId, 'Control Operator');
      soundManager.playAcknowledgeBeep();
      onAlertAcknowledged();
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    } finally {
      setAcknowledgingId(null);
    }
  };

  const formatTimestamp = (ts: string) => {
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString('en-US', { hour12: false });
    } catch {
      return ts;
    }
  };

  return (
    <div className="bg-dark-850 border border-dark-750 rounded-xl p-4 shadow-lg flex flex-col h-full">
      {/* Header & Tabs */}
      <div className="flex items-center justify-between pb-3 border-b border-dark-700/80 mb-3">
        <div className="flex items-center space-x-2">
          <Bell className="w-4 h-4 text-amber-400" />
          <h3 className="font-mono text-xs font-semibold text-white uppercase tracking-wider">
            Safety Alerts & Protocol Feed
          </h3>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center space-x-1 bg-dark-900 p-0.5 rounded-lg border border-dark-700 text-[11px] font-mono">
          <button
            onClick={() => setFilter('all')}
            className={`px-2 py-0.5 rounded ${
              filter === 'all' ? 'bg-dark-750 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('active')}
            className={`px-2 py-0.5 rounded ${
              filter === 'active' ? 'bg-amber-950 text-amber-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Active
          </button>
          <button
            onClick={() => setFilter('critical')}
            className={`px-2 py-0.5 rounded ${
              filter === 'critical' ? 'bg-red-950 text-red-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Critical
          </button>
        </div>
      </div>

      {/* Alert Items List */}
      <div className="space-y-2.5 overflow-y-auto max-h-[380px] pr-1 flex-1">
        {filteredAlerts.length === 0 ? (
          <div className="py-10 text-center text-slate-500 font-mono text-xs">
            <CheckCircle2 className="w-7 h-7 text-emerald-500/60 mx-auto mb-2" />
            No active safety alerts. Monitored zones within standard thresholds.
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const badge = RISK_BADGE[alert.risk_level] || RISK_BADGE.normal;
            const isUnacknowledged = alert.acknowledged === 0;

            return (
              <div
                key={alert.id}
                className={`p-3 rounded-lg border text-xs font-mono transition-all ${
                  isUnacknowledged
                    ? `${badge.bg} ${badge.border} shadow-md`
                    : 'bg-dark-800/40 border-dark-700/60 opacity-60'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${badge.bg} ${badge.text} ${badge.border}`}
                    >
                      {alert.risk_level}
                    </span>
                    <span className="font-semibold text-slate-200">{alert.zone_name}</span>
                  </div>

                  <span className="text-[10px] text-slate-400 shrink-0">
                    {formatTimestamp(alert.timestamp)}
                  </span>
                </div>

                <p className="mt-1.5 text-slate-300 text-[11px] leading-relaxed">
                  {alert.reason}
                </p>

                <div className="mt-2.5 pt-2 border-t border-dark-700/40 flex items-center justify-between text-[11px]">
                  <span className="text-slate-400 text-[10px]">
                    Occupancy: <strong className="text-white">{alert.person_count}</strong> / limit: {alert.threshold_exceeded}
                  </span>

                  {isUnacknowledged ? (
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      disabled={acknowledgingId === alert.id}
                      className="px-2.5 py-1 rounded bg-dark-750 hover:bg-dark-700 text-emerald-400 border border-emerald-600/40 hover:border-emerald-500 text-[10px] font-semibold flex items-center space-x-1 transition-colors"
                    >
                      <Check className="w-3 h-3" />
                      <span>{acknowledgingId === alert.id ? 'Saving...' : 'Acknowledge'}</span>
                    </button>
                  ) : (
                    <span className="text-emerald-400/80 text-[10px] flex items-center space-x-1">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Acknowledged by {alert.acknowledged_by || 'Operator'}</span>
                    </span>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
