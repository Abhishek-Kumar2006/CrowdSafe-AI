import React, { useState } from 'react';
import { AlertTriangle, Info, X } from 'lucide-react';

export const DisclaimerBanner: React.FC = () => {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div className="bg-dark-850/90 border-b border-dark-700/80 px-4 py-2 text-xs flex items-center justify-between backdrop-blur-sm">
      <div className="flex items-center space-x-2 text-slate-300">
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
        </span>
        <span className="font-semibold text-amber-400 tracking-wide uppercase">Operational Advisory:</span>
        <span>
          CrowdSafe AI is an AI-assisted decision-support prototype. It identifies potential crowd-density risks and bottleneck congestion rather than predicting stampedes with certainty.
        </span>
      </div>
      <button
        onClick={() => setDismissed(true)}
        className="text-slate-400 hover:text-white transition-colors p-1"
        title="Dismiss notice"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
