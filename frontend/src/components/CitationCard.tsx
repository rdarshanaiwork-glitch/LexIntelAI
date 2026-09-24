import React from 'react';
import { BookOpen, Scale, CheckCircle2, AlertTriangle, Sparkles } from 'lucide-react';
import { Citation } from '../types';

export const CitationCard: React.FC<{ citation: Citation }> = ({ citation }) => {
  const isPrecedent = citation.source_type === 'precedent';
  const evidenceType = citation.evidence_type || 'SUPPORTED BY SOURCE';

  let badgeColor = 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40';
  let BadgeIcon = CheckCircle2;
  let badgeLabel = 'SUPPORTED BY SOURCE';

  if (evidenceType === 'MODEL INFERENCE') {
    badgeColor = 'bg-amber-950/80 text-amber-300 border-amber-500/40';
    BadgeIcon = Sparkles;
    badgeLabel = 'MODEL INFERENCE';
  } else if (evidenceType === 'INSUFFICIENT EVIDENCE') {
    badgeColor = 'bg-rose-950/80 text-rose-300 border-rose-500/40';
    BadgeIcon = AlertTriangle;
    badgeLabel = 'INSUFFICIENT EVIDENCE';
  }

  return (
    <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-blue-500/40 transition-all duration-200 space-y-3 shadow-lg">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          {isPrecedent ? (
            <Scale className="w-4 h-4 text-amber-400 shrink-0" />
          ) : (
            <BookOpen className="w-4 h-4 text-blue-400 shrink-0" />
          )}
          <h4 className="text-sm font-semibold text-white truncate max-w-xs sm:max-w-md">
            {citation.title}
          </h4>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950/80 text-blue-300 border border-blue-800/40 shrink-0">
          {(citation.relevance_score * 100).toFixed(0)}% Match
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
        <span className="font-mono text-slate-200 font-semibold">{citation.citation_text}</span>
        <span>•</span>
        <span>{citation.jurisdiction}</span>
        <span>•</span>
        <span className="capitalize text-slate-300">{citation.source_type}</span>
      </div>

      {citation.quote && (
        <blockquote className="text-xs italic text-slate-300 bg-slate-950/80 p-3 rounded-lg border-l-2 border-blue-500/60 leading-relaxed">
          "{citation.quote}"
        </blockquote>
      )}

      {/* Evidentiary Grounding Badge */}
      <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between">
        <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-[10px] font-bold tracking-wider font-mono border uppercase ${badgeColor}`}>
          <BadgeIcon className="w-3 h-3" />
          <span>{badgeLabel}</span>
        </div>
        <span className="text-[10px] text-slate-400 font-mono">
          RAG Verified Ground Truth
        </span>
      </div>
    </div>
  );
};