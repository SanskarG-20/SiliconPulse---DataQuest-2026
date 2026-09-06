import React, { useEffect, useState } from 'react';
import { X, Coffee, RefreshCw, Bell, Send, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { fetchDigestPrefs, saveDigestPrefs, sendDigestNow } from '../../api/siliconpulseApi';

interface DigestModalProps {
  isOpen: boolean;
  onClose: () => void;
  loading: boolean;
  content: string | null;
}

const HOURS = Array.from({ length: 24 }, (_, h) => h);

export const DigestModal: React.FC<DigestModalProps> = ({ isOpen, onClose, loading, content }) => {
  const [prefs, setPrefs] = useState({ enabled: false, hour_utc: 11, email: '', webhook_url: '' });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    setSaved(false);
    setSent(null);
    fetchDigestPrefs().then((p) => {
      setPrefs({ enabled: !!p.enabled, hour_utc: p.hour_utc ?? 11, email: p.email || '', webhook_url: p.webhook_url || '' });
    }).catch(() => {});
  }, [isOpen]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await saveDigestPrefs(prefs);
      if (res) {
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      }
    } finally {
      setSaving(false);
    }
  };

  const handleSendNow = async () => {
    setSending(true);
    setSent(null);
    try {
      const res = await sendDigestNow(true);
      if (!res) {
        setSent('Build failed. Try again.');
      } else if (res.delivered?.email || res.delivered?.slack) {
        const where = [res.delivered.email ? 'email' : null, res.delivered.slack ? 'webhook' : null].filter(Boolean).join(' + ');
        setSent(`Delivered via ${where}.`);
      } else {
        setSent('Briefing built. Add an email or webhook above to deliver it automatically.');
      }
    } finally {
      setSending(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-white/80 dark:bg-slate-950/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-slate-50 dark:bg-[#020617] border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl overflow-hidden relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors"
          aria-label="Close"
        >
          <X size={20} />
        </button>
        <div className="p-4 md:p-6 border-b border-slate-200/50 dark:border-slate-800/50">
          <h3 className="text-lg font-black text-white uppercase tracking-tight flex items-center">
            <Coffee size={20} className="mr-2 text-emerald-500" /> Morning Briefing
          </h3>
        </div>
        <div className="p-4 md:p-6 max-h-[70vh] overflow-y-auto custom-scrollbar space-y-4">
          <div className="rounded-[14px] border border-[#1C3553]/40 bg-[#0B1426]/40 p-4 space-y-3">
            <p className="flex items-center gap-1.5 mono text-[10px] font-bold tracking-[0.12em] text-[#64748B]">
              <Bell size={12} /> DAILY SCHEDULE
            </p>
            <label className="flex items-center gap-2 text-[12px] font-medium text-slate-700 dark:text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={prefs.enabled}
                onChange={(e) => setPrefs({ ...prefs, enabled: e.target.checked })}
                className="w-4 h-4 rounded border-slate-300 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-emerald-500"
              />
              Email / webhook me every morning
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <label className="block">
                <span className="mono text-[10px] tracking-[0.08em] text-[#475569]">HOUR (UTC)</span>
                <select
                  value={prefs.hour_utc}
                  onChange={(e) => setPrefs({ ...prefs, hour_utc: parseInt(e.target.value, 10) })}
                  className="mt-1 w-full rounded-[10px] bg-white dark:bg-[#050B1A] border border-[#1C3553]/50 px-2.5 py-1.5 text-[12px] text-slate-800 dark:text-slate-200 focus:outline-none focus:border-emerald-500/40"
                >
                  {HOURS.map((h) => (
                    <option key={h} value={h}>{String(h).padStart(2, '0')}:00 UTC</option>
                  ))}
                </select>
              </label>
              <label className="block">
                <span className="mono text-[10px] tracking-[0.08em] text-[#475569]">EMAIL</span>
                <input
                  value={prefs.email}
                  onChange={(e) => setPrefs({ ...prefs, email: e.target.value })}
                  placeholder="you@company.com"
                  type="email"
                  className="mt-1 w-full rounded-[10px] bg-white dark:bg-[#050B1A] border border-[#1C3553]/50 px-2.5 py-1.5 text-[12px] text-slate-800 dark:text-slate-200 placeholder:text-[#475569] focus:outline-none focus:border-emerald-500/40"
                />
              </label>
            </div>
            <label className="block">
              <span className="mono text-[10px] tracking-[0.08em] text-[#475569]">SLACK / DISCORD WEBHOOK (OPTIONAL)</span>
              <input
                value={prefs.webhook_url}
                onChange={(e) => setPrefs({ ...prefs, webhook_url: e.target.value })}
                placeholder="https://hooks.slack.com/…"
                className="mt-1 w-full rounded-[10px] bg-white dark:bg-[#050B1A] border border-[#1C3553]/50 px-2.5 py-1.5 text-[12px] text-slate-800 dark:text-slate-200 placeholder:text-[#475569] focus:outline-none focus:border-emerald-500/40 mono"
              />
            </label>
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={handleSave}
                disabled={saving}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-emerald-600 text-white text-[11px] font-bold tracking-[0.04em] hover:bg-emerald-500 transition-colors disabled:opacity-50"
              >
                {saved ? <Check size={13} /> : null} {saving ? 'Saving…' : saved ? 'Saved' : 'Save schedule'}
              </button>
              <button
                onClick={handleSendNow}
                disabled={sending}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#0E1E32] border border-[#1C3553] text-[11px] font-semibold text-slate-600 dark:text-[#94A3B8] hover:text-slate-900 dark:hover:text-white transition-colors disabled:opacity-50"
              >
                <Send size={13} /> {sending ? 'Sending…' : 'Build & deliver now'}
              </button>
              {sent && <span className="text-[11px] text-[#64748B]">{sent}</span>}
            </div>
            <p className="mono text-[10px] tracking-[0.06em] text-[#475569]">11:00 UTC ≈ 7am ET / 4am PT. Delivery needs Resend configured server-side; otherwise briefings stay in-app.</p>
          </div>

          {loading ? (
            <div className="flex flex-col items-center justify-center py-12 space-y-4">
              <RefreshCw size={24} className="text-emerald-500 animate-spin" />
              <p className="text-slate-600 dark:text-slate-400 text-sm font-medium">Brewing your daily digest...</p>
            </div>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none text-slate-700 dark:text-slate-300">
              <ReactMarkdown>{content || ''}</ReactMarkdown>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
