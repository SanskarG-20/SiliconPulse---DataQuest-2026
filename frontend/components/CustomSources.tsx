import React, { useEffect, useState } from 'react';
import { Rss, Plus, Trash2, RefreshCw, Power } from 'lucide-react';
import { fetchRssFeeds, addRssFeed, deleteRssFeed, toggleRssFeed, pullRssNow } from '../api/siliconpulseApi';

export const CustomSources: React.FC = () => {
  const [feeds, setFeeds] = useState<any[]>([]);
  const [url, setUrl] = useState('');
  const [label, setLabel] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [pulling, setPulling] = useState(false);
  const [pullResult, setPullResult] = useState<string | null>(null);

  const refresh = async () => setFeeds(await fetchRssFeeds());

  useEffect(() => {
    refresh().catch(() => {});
  }, []);

  const handleAdd = async () => {
    setError(null);
    if (!url.trim().startsWith('http')) {
      setError('Feed URL must start with http(s)://');
      return;
    }
    const res = await addRssFeed(url.trim(), label.trim());
    if (res === null) setError('Could not save feed (check URL, duplicates, and Supabase setup).');
    else {
      setFeeds(res);
      setUrl('');
      setLabel('');
    }
  };

  const handlePull = async () => {
    setPulling(true);
    setPullResult(null);
    try {
      const res = await pullRssNow();
      setPullResult(res ? `${res.new_added} new signals from ${res.feeds_checked} feeds.` : 'Pull failed.');
      setFeeds(await fetchRssFeeds());
    } finally {
      setPulling(false);
    }
  };

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 sm:grid-cols-[1fr_140px_auto] gap-1.5">
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') handleAdd(); }}
          placeholder="https://example.com/feed.xml"
          className="px-2.5 py-1.5 rounded-full bg-[#050B1A] border border-[#1C3553]/60 text-[12px] mono text-[#E2E8F0] placeholder:text-[#475569] focus:outline-none focus:border-[#22D3EE]/40"
          aria-label="RSS feed URL"
        />
        <input
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') handleAdd(); }}
          placeholder="Label (optional)"
          className="px-2.5 py-1.5 rounded-full bg-[#050B1A] border border-[#1C3553]/60 text-[12px] text-[#E2E8F0] placeholder:text-[#475569] focus:outline-none focus:border-[#22D3EE]/40"
          aria-label="Feed label"
        />
        <button onClick={handleAdd} className="inline-flex items-center justify-center gap-1 px-3 py-1.5 rounded-full bg-[#0E1E32] border border-[#1C3553] text-[11px] font-semibold text-[#94A3B8] hover:text-white transition-colors">
          <Plus size={13} /> Add
        </button>
      </div>
      {error && <p className="text-[11px] text-red-400">{error}</p>}

      <div className="flex items-center gap-2">
        <p className="mono text-[10px] tracking-[0.08em] text-[#475569]">SEC EDGAR 8-K runs daily automatically • RSS polls hourly</p>
        <button onClick={handlePull} disabled={pulling} className="ml-auto inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#0E1E32] border border-[#1C3553] text-[10px] font-semibold uppercase tracking-[0.06em] text-[#94A3B8] hover:text-white transition-colors disabled:opacity-50">
          <RefreshCw size={11} className={pulling ? 'animate-spin' : ''} /> {pulling ? 'Pulling…' : 'Pull now'}
        </button>
      </div>
      {pullResult && <p className="mono text-[11px] text-[#64748B]">{pullResult}</p>}

      {feeds.length > 0 ? (
        <ul className="space-y-1.5">
          {feeds.map((f: any) => (
            <li key={f.id} className="flex items-center gap-2 rounded-[10px] bg-[#050B1A] border border-[#1C3553]/40 px-2.5 py-2">
              <Rss size={12} className={f.enabled ? 'text-[#22D3EE]' : 'text-[#334155]'} />
              <span className="min-w-0 flex-1">
                <span className="block truncate text-[12px] font-semibold text-[#E2E8F0]">{f.label || f.url}</span>
                <span className="block truncate mono text-[10px] text-[#475569]">{f.url}{f.last_error ? ` • err: ${f.last_error.slice(0, 60)}` : ''}</span>
              </span>
              <button
                onClick={async () => setFeeds(await toggleRssFeed(f.id, !f.enabled))}
                className={`p-1.5 rounded-full border transition-colors ${f.enabled ? 'border-emerald-500/20 text-emerald-400 bg-emerald-500/10' : 'border-[#1C3553] text-[#475569]'}`}
                title={f.enabled ? 'Pause feed' : 'Resume feed'}
                aria-label={f.enabled ? 'Pause feed' : 'Resume feed'}
              >
                <Power size={12} />
              </button>
              <button
                onClick={async () => setFeeds(await deleteRssFeed(f.id))}
                className="p-1.5 rounded-full text-[#475569] hover:text-red-400 transition-colors"
                aria-label="Delete feed"
              >
                <Trash2 size={12} />
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-[12px] text-[#475569]">No custom feeds yet. Add a fab blog, analyst RSS, or company newsroom feed.</p>
      )}
    </div>
  );
};
