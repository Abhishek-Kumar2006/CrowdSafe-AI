import React, { useState, useEffect } from 'react';
import { X, History, Search, Download, CheckCircle, AlertTriangle, ShieldCheck } from 'lucide-react';
import { Alert, RiskLevel } from '../types';
import { api } from '../services/api';

interface AlertHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  cameraId?: string;
}

const RISK_BADGE_STYLE: Record<RiskLevel, string> = {
  normal: 'bg-emerald-950/80 text-emerald-400 border-emerald-700',
  increasing: 'bg-amber-950/80 text-amber-400 border-amber-700',
  high: 'bg-orange-950/80 text-orange-400 border-orange-700',
  critical: 'bg-red-950/80 text-red-400 border-red-700',
};

export const AlertHistoryModal: React.FC<AlertHistoryModalProps> = ({ isOpen, onClose, cameraId }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [filterLevel, setFilterLevel] = useState<string>('all');

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const data = await api.getAlerts(cameraId, false, 100);
      setAlerts(data.alerts);
    } catch (err) {
      console.error('Failed to fetch alert history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen, cameraId]);

  if (!isOpen) return null;

  const filtered = alerts.filter((a) => {
    const matchSearch =
      a.zone_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.reason.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.camera_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchLevel = filterLevel === 'all' || a.risk_level === filterLevel;
    return matchSearch && matchLevel;
  });

  const exportJSON = () => {
    const blob = new Blob([JSON.stringify(filtered, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `crowdsafe-alert-history-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-dark-850 border border-dark-700 rounded-2xl w-full max-w-4xl p-6 shadow-2xl flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-dark-700">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 bg-dark-800 rounded-lg border border-dark-700 text-amber-400">
              <History className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-mono text-base font-bold text-white">
                Historical Alert Audit Log (SQLite DB)
              </h3>
              <p className="text-xs text-slate-400">
                Persistent observation logs, incidents & operator acknowledgments
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={exportJSON}
              className="px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 bg-dark-800 hover:bg-dark-750 border border-dark-600 flex items-center space-x-1.5 transition-colors"
              title="Export Log as JSON"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export</span>
            </button>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-1 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Search & Filter Controls */}
        <div className="mt-4 flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by zone, reason, camera..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-dark-900 border border-dark-700 rounded-lg pl-9 pr-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
            />
          </div>

          <select
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value)}
            className="bg-dark-900 border border-dark-700 rounded-lg px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none focus:border-emerald-500"
          >
            <option value="all">All Risk Levels</option>
            <option value="critical">Critical Only</option>
            <option value="high">High Only</option>
            <option value="increasing">Increasing Only</option>
            <option value="normal">Normal Only</option>
          </select>
        </div>

        {/* Table View */}
        <div className="mt-4 flex-1 overflow-y-auto border border-dark-750 rounded-xl bg-dark-900">
          {loading ? (
            <div className="py-12 text-center text-slate-400 font-mono text-xs">
              Loading historical database records...
            </div>
          ) : filtered.length === 0 ? (
            <div className="py-12 text-center text-slate-500 font-mono text-xs">
              No matching alert records in database.
            </div>
          ) : (
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-dark-800 text-slate-400 border-b border-dark-700 sticky top-0">
                <tr>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Risk Level</th>
                  <th className="py-2.5 px-3">Zone</th>
                  <th className="py-2.5 px-3">Occupancy / Limit</th>
                  <th className="py-2.5 px-3">Incident Reason</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-800 text-slate-300">
                {filtered.map((item) => {
                  const badge = RISK_BADGE_STYLE[item.risk_level] || RISK_BADGE_STYLE.normal;
                  return (
                    <tr key={item.id} className="hover:bg-dark-800/50">
                      <td className="py-2.5 px-3 whitespace-nowrap text-slate-400">
                        {new Date(item.timestamp).toLocaleString()}
                      </td>
                      <td className="py-2.5 px-3 whitespace-nowrap">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${badge}`}>
                          {item.risk_level}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-semibold text-white">{item.zone_name}</td>
                      <td className="py-2.5 px-3 whitespace-nowrap">
                        <span className="text-white font-bold">{item.person_count}</span>
                        <span className="text-slate-500"> / {item.threshold_exceeded}</span>
                      </td>
                      <td className="py-2.5 px-3 text-[11px] text-slate-300 max-w-xs truncate" title={item.reason}>
                        {item.reason}
                      </td>
                      <td className="py-2.5 px-3 whitespace-nowrap">
                        {item.acknowledged ? (
                          <span className="text-emerald-400 flex items-center space-x-1 text-[11px]">
                            <CheckCircle className="w-3 h-3" />
                            <span>Ack: {item.acknowledged_by || 'Operator'}</span>
                          </span>
                        ) : (
                          <span className="text-amber-400 font-bold text-[11px]">Unacknowledged</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Footer */}
        <div className="mt-4 pt-3 border-t border-dark-700 flex items-center justify-between text-xs font-mono text-slate-400">
          <span>Total Records: {filtered.length}</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg text-xs font-mono bg-dark-800 hover:bg-dark-750 text-white border border-dark-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
