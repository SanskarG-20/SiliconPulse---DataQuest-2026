import React, { useEffect, useMemo, useState } from 'react';
import { TrendingUp, Flame } from 'lucide-react';
import { fetchTrends } from '../api/siliconpulseApi';

interface TrendsPanelProps {
  company?: string;
  days?: number;
  onCompanyClick?: (company: string) => void;
}

const W = 268;
const H = 64;

function toPoints(daily: Array<{ date: string; count: number }>): string {
  if (!daily.length) return '';
  const max = Math.max(1, ...daily.map((d) => d.count));
  return daily
    .map((d, i) => {
      const x = (i / Math.max(1, daily.length - 1)) * (W - 4) + 2;
      const y = H - 4 - (d.count / max) * (H - 12);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');
}

export const TrendsPanel: React.FC<TrendsPanelProps> = ({ company, days = 30, onCompanyClick }) => {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchTrends(company, days)
      .then((res) => { if (!cancelled) setData(res); })
      .catch(() => {})
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [company, days]);

  const points = useMemo(() => toPoints(data?.daily || []), [data]);
  const area = useMemo(() => (points ? `2,${H - 2} ${points} ${W - 2},${H - 2}` : ''), [points]);
  const spikeDates = useMemo(() => new Set((data?.spikes || []).map((s: any) => s.date)), [data]);

  return (
    <div className="rounded-[14px] border border-slate-200 dark:border-[#1C3553]/50 bg-white/70 dark:bg-[#0E1E32]/50 p-4 space-y-3">
      <div className="flex items-center gap-1.5">
        <TrendingUp size={12} className="text-[#0284C7] dark:text-[#22D3EE]" />
        <span className="mono text-[10px] font-semibold tracking-[0.12em] text-[#0284C7] dark:text-[#22D3EE]">SIGNAL TRENDS</span>
        <span className="ml-auto mono text-[10px] tracking-[0.06em] text-[#475569]">{days}d{company ? ` • ${company}` : ''}</span>
      </div>

      {loading && !data ? (
        <div className="h-[64px] rounded-[10px] bg-slate-100 dark:bg-[#050B1A] border border-slate-200 dark:border-[#1C3553]/30 animate-pulse" />
      ) : !data || data.total === 0 ? (
        <p className="text-[12px] leading-relaxed text-[#475569]">No signals in this window yet.</p>
      ) : (
        <>
          <div>
            <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-[64px] block" role="img" aria-label="Signal trend sparkline">
              {area && <polygon points={area} fill="rgba(34,211,238,0.10)" />}
              {points && <polyline points={points} fill="none" stroke="#22D3EE" strokeWidth="1.6" strokeLinejoin="round" strokeLinecap="round" />}
              {(data.daily || []).map((d: any, i: number) => {
                if (!spikeDates.has(d.date) || d.count === 0) return null;
                const x = (i / Math.max(1, data.daily.length - 1)) * (W - 4) + 2;
                const max = Math.max(1, ...data.daily.map((p: any) => p.count));
                const y = H - 4 - (d.count / max) * (H - 12);
                return <circle key={d.date} cx={x} cy={y} r={3} fill="#E8A253" stroke="#050B1A" strokeWidth={1.2} />;
              })}
            </svg>
            <div className="mt-1 flex items-center justify-between mono text-[10px] tracking-[0.06em] text-[#475569]">
              <span>{data.total} signals • avg {data.mean}/day</span>
              {(data.spikes || []).length > 0 && (
                <span className="inline-flex items-center gap-1 font-bold text-[#B45309] dark:text-[#E8A253]">
                  <Flame size={11} /> {data.spikes.length} spike{data.spikes.length > 1 ? 's' : ''}
                </span>
              )}
            </div>
          </div>

          {(data.spikes || []).length > 0 && (
            <ul className="space-y-1">
              {data.spikes.slice(0, 3).map((s: any) => (
                <li key={s.date} className="flex items-center justify-between rounded-full bg-white dark:bg-[#050B1A] border border-[#E8A253]/25 px-2.5 py-1">
                  <span className="mono text-[10px] tracking-[0.06em] text-[#B45309] dark:text-[#E8A253] font-bold">{s.date}</span>
                  <span className="mono text-[10px] text-slate-500 dark:text-[#94A3B8]">{s.count} signals • z {s.z}</span>
                </li>
              ))}
            </ul>
          )}

          {(data.by_company || []).length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {data.by_company.slice(0, 4).map((c: any) => (
                <button
                  key={c.company}
                  onClick={() => onCompanyClick?.(c.company)}
                  className="px-2 py-1 rounded-full bg-white dark:bg-[#050B1A] border border-slate-300 dark:border-[#1C3553]/40 text-[11px] font-medium text-slate-700 dark:text-[#CBD5E1] hover:text-slate-900 dark:hover:text-white hover:border-[#22D3EE]/25 transition-colors"
                  title={`${c.count} signals`}
                >
                  {c.company} <span className="mono text-[10px] text-[#475569]">{c.count}</span>
                </button>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};
