import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Activity, AlertCircle } from 'lucide-react';
import { fetchPublicBrief } from '../api/siliconpulseApi';
import { StrategicInsightReport } from './StrategicInsightReport';
import { BackgroundLayer } from './BackgroundLayer';

export const PublicBrief: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [brief, setBrief] = useState<any | null>(null);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!id) { setMissing(true); return; }
      const data = await fetchPublicBrief(id);
      if (!cancelled) {
        if (data) setBrief(data);
        else setMissing(true);
      }
    })();
    return () => { cancelled = true; };
  }, [id]);

  return (
    <div className="min-h-screen flex flex-col text-[#F1F5F9] relative">
      <BackgroundLayer />
      <header className="h-[56px] border-b border-[#1C3553]/50 flex items-center justify-between px-4 md:px-6 bg-[#050B1A]/70 backdrop-blur-xl">
        <Link to="/" className="flex items-center gap-2.5">
          <span className="w-8 h-8 rounded-[8px] bg-[#0E1E32] border border-[#1C3553] flex items-center justify-center">
            <span className="w-[18px] h-[18px] rounded-[5px] bg-[#22D3EE] flex items-center justify-center">
              <Activity size={11} className="text-[#050B1A]" strokeWidth={2.5} />
            </span>
          </span>
          <span className="display text-[13px] font-bold tracking-[-0.02em] text-white">SILICON<span className="text-[#22D3EE]">PULSE</span></span>
          <span className="mono text-[9px] tracking-[0.14em] text-[#475569] border border-[#1C3553]/50 rounded-full px-2 py-0.5 bg-[#0E1E32]">SHARED BRIEF</span>
        </Link>
        <Link to="/" className="px-3.5 py-1.5 rounded-full bg-[#E8A253] text-[#050B1A] text-[11px] font-bold tracking-[0.04em] hover:bg-[#F0A85E] transition-colors">
          Open app
        </Link>
      </header>
      <main className="flex-1 px-4 md:px-6 py-8">
        <div className="max-w-[760px] mx-auto">
          {!brief && !missing && (
            <div className="rounded-[16px] border border-[#1C3553]/40 bg-[#0E1E32]/50 p-8 text-center mono text-[12px] text-[#64748B] animate-pulse">
              Loading shared brief…
            </div>
          )}
          {missing && (
            <div className="rounded-[16px] border border-red-500/15 bg-red-500/[0.06] p-8 text-center">
              <AlertCircle size={20} className="mx-auto text-red-400 mb-2" />
              <p className="text-[14px] font-semibold text-red-200">Brief not found or no longer shared.</p>
              <Link to="/" className="mt-4 inline-block text-[12px] text-[#22D3EE] hover:underline">Back to home</Link>
            </div>
          )}
          {brief && (
            <div className="space-y-4">
              <p className="mono text-[10px] tracking-[0.12em] font-semibold text-[#22D3EE]">SHARED INTELLIGENCE REPORT</p>
              <h1 className="display text-[24px] font-bold tracking-[-0.02em] text-white leading-tight">“{brief.query}”</h1>
              <p className="mono text-[11px] text-[#64748B]">{brief.created_at ? new Date(brief.created_at).toLocaleString() : ''}</p>
              <div className="rounded-[16px] border border-[#1C3553]/50 bg-[#0E1E32]/50 p-5 md:p-6">
                <StrategicInsightReport data={brief.insight} />
              </div>
              {Array.isArray(brief.evidence) && brief.evidence.length > 0 && (
                <div className="rounded-[16px] border border-[#1C3553]/40 bg-[#0B1426]/60 p-5">
                  <p className="mono text-[10px] tracking-[0.12em] font-semibold text-[#64748B] mb-3">EVIDENCE ({brief.evidence.length})</p>
                  <ul className="space-y-2">
                    {brief.evidence.slice(0, 10).map((e: any, i: number) => (
                      <li key={i} className="text-[13px] text-[#CBD5E1]">
                        <span className="font-semibold text-white">{e.title || 'Untitled'}</span>
                        <span className="text-[#64748B]"> • {e.source || 'Unknown'}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
