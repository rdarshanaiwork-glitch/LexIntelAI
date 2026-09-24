import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const s = (status || '').toLowerCase();
  let colors = 'bg-slate-800 text-slate-300 border-slate-700';

  if (s === 'completed' || s === 'active' || s === 'passed') {
    colors = 'bg-emerald-950/60 text-emerald-300 border-emerald-500/30';
  } else if (s === 'in_progress' || s === 'running' || s === 'processing') {
    colors = 'bg-blue-950/60 text-blue-300 border-blue-500/30 animate-pulse';
  } else if (s === 'pending' || s === 'waiting') {
    colors = 'bg-amber-950/60 text-amber-300 border-amber-500/30';
  } else if (s === 'failed' || s === 'error') {
    colors = 'bg-rose-950/60 text-rose-300 border-rose-500/30';
  }

  const px = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${colors} ${px}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${s === 'completed' ? 'bg-emerald-400' : s === 'in_progress' ? 'bg-blue-400' : s === 'failed' ? 'bg-rose-400' : 'bg-amber-400'}`} />
      {status.replace('_', ' ').toUpperCase()}
    </span>
  );
};