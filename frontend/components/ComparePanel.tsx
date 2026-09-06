import React, { useState } from 'react';
import { GitCompare, Plus, X, Play, Trophy, AlertTriangle } from 'lucide-react';
import { fetchCompare } from '../api/siliconpulseApi';
import { StrategicInsightReport } from './StrategicInsightReport';

interface ComparePanelProps {
  initialCompanies?: string[];
  watchlist?: string[];
  onCompanyClick?: (company: string) => void;
}

export const ComparePanel: React.FC<ComparePanelProps> = ({ initialCompanies, watchlist = [], onCompanyClick }) => {
  const [companies, setCompanies] = useState<string[]>(initialCompanies?.slice(0, 4) ?? ['TSMC', 'Samsung']);
  const [input, setInput] = useState('');
  const [context, setContext] = useState('');
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addCompany = (name: string) => {
    const clean = name.trim();
    if (!clean || companies.length >= 4) return;
    if (companies.some((c) => c.toLowerCase() === clean.toLowerCase())) return;
    setCompanies([...companies, clean.slice(0, 50)]);
    setInput('');
  };

  const runCompare = async () => {
    if (companies.length < 2 || loading) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCompare(companies, context, 5, 2);
      if (!res) setError('Comparison unavailable. Check backend connection and retry.');
      else setData(res);
    } catch {
      setError('Comparison unavailable. Check backend connection and retry.');
    } finally {
      setLoading(false);
    }
  };

  const leader = data?.companies?.length
    ? [...data.companies].sort((a: any, b: any) => b.signal_strength - a.signal_strength)[0]
    : null;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex flex-wrap gap-1.5">
          {companies.map((c) => (
            <span key={c} className="inline-flex items-center gap-1 rounded-full bg-white dark:bg-[#050B1A] border border-slate-300 dark:border-[#1C3553]/60 pl-2.5 pr-1.5 py-1 text-[12px] font-semibold text-slate-800 dark:text-[#E2E8F0]">
              {c}
              <button
                onClick={() => setCompanies(companies.filter((x) => x !== c))}
                className="p-0.5 rounded-full text-[#475569] hover:text-slate-900 dark:hover:text-white transition-colors"
                aria-label={`Remove ${c}`}
              >
                <X size={12} />
              </button>
            </span>
          ))}
        </div>
        {companies.length < 4 && (
          <span className="inline-flex items-center gap-1.5">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') addCompany(input); }}
              placeholder="Add company…"
              className="w-[130px] px-2.5 py-1 rounded-full bg-white dark:bg-[#050B1A] border border-slate-300 dark:border-[#1C3553]/60 text-[12px] text-slate-800 dark:text-[#E2E8F0] placeholder:text-[#475569] focus:outline-none focus:border-[#22D3EE]/40"
              aria-label="Add company"
            />
            <button onClick={() => addCompany(input)} className="p-1.5 rounded-full bg-slate-100 dark:bg-[#0E1E32] border border-slate-300 dark:border-[#1C3553] text-slate-600 dark:text-[#94A3B8] hover:text-slate-900 dark:hover:text-white transition-colors" aria-label="Add">
              <Plus size={13} />
            </button>
          </span>
        )}
      </div>

      {watchlist.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {watchlist.filter((w) => !companies.some((c) => c.toLowerCase() === w.toLowerCase())).slice(0, 6).map((w) => (
            <button key={w} onClick={() => addCompany(w)} disabled={companies.length >= 4} className="px-2 py-1 rounded-full bg-[#E8A253]/10 border border-[#E8A253]/15 text-[11px] font-medium text-[#B45309] dark:text-[#E8A253] hover:bg-[#E8A253]/15 transition-colors disabled:opacity-40">
              + {w}
            </button>
          ))}
        </div>
      )}

      <div className="flex flex-wrap items-center gap-2">
        <input
          value={context}
          onChange={(e) => setContext(e.target.value)}
          placeholder="Shared context (optional): e.g. N2 yield"
          className="flex-1 min-w-[180px] px-3 py-1.5 rounded-full bg-white dark:bg-[#050B1A] border border-slate-300 dark:border-[#1C3553]/60 text-[12px] text-slate-800 dark:text-[#E2E8F0] placeholder:text-[#475569] focus:outline-none focus:border-[#22D3EE]/40"
          aria-label="Comparison context"
        />
        <button
          onClick={runCompare}
          disabled={companies.length < 2 || loading}
          className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-[#E8A253] text-[#050B1A] text-[11px] font-bold tracking-[0.04em] hover:bg-[#F0A85E] transition-colors disabled:opacity-50"
        >
          <Play size={13} /> {loading ? 'Comparing…' : 'Compare'}
        </button>
      </div>

      {error && !loading && (
        <div className="flex items-center gap-2 rounded-[12px] border border-red-500/15 bg-red-500/[0.06] px-3.5 py-2.5 text-[12px] text-red-300">
          <AlertTriangle size={14} /> {error}
        </div>
      )}

      {loading && !data && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-[86px] rounded-[12px] bg-slate-100 dark:bg-[#050B1A] border border-slate-200 dark:border-[#1C3553]/30 animate-pulse" />
          ))}
        </div>
      )}

      {data && (
        <div className="space-y-3">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {data.companies.map((r: any) => (
              <button
                key={r.company}
                onClick={() => onCompanyClick?.(r.company)}
                className={`text-left rounded-[12px] border p-3 transition-colors ${
                  leader?.company === r.company
                    ? 'border-[#E8A253]/40 bg-[#E8A253]/[0.07]'
                    : 'border-slate-300 dark:border-[#1C3553]/40 bg-white dark:bg-[#050B1A] hover:border-[#22D3EE]/25'
                }`}
              >
                <p className="flex items-center gap-1.5 text-[12px] font-bold text-slate-900 dark:text-white">
                  {leader?.company === r.company && <Trophy size={12} className="text-[#E8A253]" />}
                  {r.company}
                </p>
                <p className="display mt-1 text-[20px] font-bold tracking-[-0.02em] text-[#B45309] dark:text-[#E8A253]">{r.signal_strength}<span className="text-[11px] font-medium text-[#64748B]">/100</span></p>
                <p className="mono mt-0.5 text-[10px] tracking-[0.06em] text-[#64748B]">{r.evidence_count} signals • ↓{r.downstream_count} ↑{r.suppliers_count}</p>
                {r.summary?.latest_title && (
                  <p className="mt-1.5 text-[11px] leading-snug text-slate-600 dark:text-[#94A3B8] line-clamp-2">{r.summary.latest_title}</p>
                )}
              </button>
            ))}
          </div>

          {(data.overlap?.shared_downstream?.length > 0 || data.overlap?.shared_upstream?.length > 0) && (
            <div className="rounded-[12px] border border-[#22D3EE]/15 bg-[#22D3EE]/[0.05] px-3.5 py-2.5">
              <p className="mono text-[10px] font-semibold tracking-[0.1em] text-[#0284C7] dark:text-[#22D3EE] mb-1.5">SHARED EXPOSURE</p>
              <div className="flex flex-wrap gap-1.5">
                {(data.overlap.shared_downstream || []).slice(0, 4).map((o: any) => (
                  <span key={`d-${o.company}`} className="px-2 py-1 rounded-full bg-white dark:bg-[#050B1A] border border-slate-300 dark:border-[#1C3553]/40 text-[11px] text-slate-700 dark:text-[#CBD5E1]">
                    ↓ {o.company} <span className="mono text-[10px] text-[#475569]">via {o.shared_by.join(' + ')}</span>
                  </span>
                ))}
                {(data.overlap.shared_upstream || []).slice(0, 4).map((o: any) => (
                  <span key={`u-${o.company}`} className="px-2 py-1 rounded-full bg-white dark:bg-[#050B1A] border border-slate-300 dark:border-[#1C3553]/40 text-[11px] text-slate-700 dark:text-[#CBD5E1]">
                    ↑ {o.company} <span className="mono text-[10px] text-[#475569]">via {o.shared_by.join(' + ')}</span>
                  </span>
                ))}
              </div>
            </div>
          )}

          {data.comparison_report && (
            <div className="rounded-[12px] border border-slate-200 dark:border-[#1C3553]/40 bg-white/60 dark:bg-[#050B1A]/60 p-4">
              <StrategicInsightReport data={data.comparison_report} />
            </div>
          )}
        </div>
      )}

      {!data && !loading && !error && (
        <p className="flex items-center gap-1.5 text-[11px] text-[#475569]">
          <GitCompare size={12} /> Pick 2–4 companies, optionally add shared context, then compare.
        </p>
      )}
    </div>
  );
};
