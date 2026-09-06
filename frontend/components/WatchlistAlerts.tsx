import React from 'react';
import { Bell } from 'lucide-react';
import { getRelativeTimeLabel } from '../utils/feedUtils';

interface WatchlistAlertsProps {
  alerts: any[];
  watchlist: string[];
  onCompanyClick: (company: string) => void;
}

export const WatchlistAlerts: React.FC<WatchlistAlertsProps> = ({ alerts, watchlist, onCompanyClick }) => {
  if (watchlist.length === 0) return null;
  return (
    <div className="rounded-[14px] border border-[#E8A253]/15 bg-[#E8A253]/[0.06] p-4 space-y-3">
      <p className="flex items-center gap-1.5 mono text-[10px] font-bold tracking-[0.12em] text-[#B45309] dark:text-[#E8A253]">
        <Bell size={12} /> WATCHLIST ALERTS
        <span className="ml-auto px-1.5 py-0.5 rounded-full bg-[#E8A253]/10 text-[9px]">{watchlist.length} tracked</span>
      </p>
      {alerts.length === 0 ? (
        <p className="text-[12px] leading-relaxed text-[#64748B]">No fresh signals for {watchlist.slice(0, 3).join(', ')}{watchlist.length > 3 ? ` +${watchlist.length - 3}` : ''} yet. New matches appear here automatically.</p>
      ) : (
        <ul className="space-y-2">
          {alerts.slice(0, 5).map((a: any, i: number) => (
            <li key={`${a.title}-${i}`}>
              <button onClick={() => onCompanyClick(a.matched_company || a.company)} className="w-full text-left rounded-[10px] bg-white dark:bg-[#050B1A] border border-slate-300 dark:border-[#1C3553]/40 hover:border-[#E8A253]/30 p-2.5 transition-colors group">
                <p className="text-[12px] font-semibold leading-snug text-slate-800 dark:text-[#E2E8F0] group-hover:text-slate-900 dark:group-hover:text-white line-clamp-2">{a.title}</p>
                <p className="mt-1 mono text-[10px] tracking-[0.06em] text-[#64748B]">
                  <span className="text-[#E8A253] font-bold">{a.matched_company || a.company}</span> • {getRelativeTimeLabel(a.timestamp)} • {a.source}
                </p>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
