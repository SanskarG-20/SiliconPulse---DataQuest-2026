import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Plus, Copy, Check, X, LogIn } from 'lucide-react';
import {
  fetchWorkspaces,
  createWorkspace,
  joinWorkspace,
  fetchWorkspaceDetail,
  addWorkspaceCompany,
  removeWorkspaceCompany,
} from '../api/siliconpulseApi';

export const WorkspacesPanel: React.FC<{ onCompanyClick?: (company: string) => void }> = ({ onCompanyClick }) => {
  const [spaces, setSpaces] = useState<any[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [detail, setDetail] = useState<any | null>(null);
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [company, setCompany] = useState('');
  const [copied, setCopied] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const refresh = async () => {
    const list = await fetchWorkspaces();
    setSpaces(list);
    if (!activeId && list.length > 0) setActiveId(list[0].id);
  };

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!activeId) { setDetail(null); return; }
    fetchWorkspaceDetail(activeId).then(setDetail).catch(() => {});
  }, [activeId]);

  const active = spaces.find((s) => s.id === activeId);

  const handleCreate = async () => {
    if (!name.trim()) return;
    const res = await createWorkspace(name.trim());
    if (res?.workspace) {
      setName('');
      await refresh();
      setActiveId(res.workspace.id);
      setDetail(await fetchWorkspaceDetail(res.workspace.id));
      setNotice(`Invite code: ${res.invite_code} — share it with your team.`);
    } else {
      setNotice('Workspace creation needs Supabase configured.');
    }
  };

  const handleJoin = async () => {
    if (!code.trim()) return;
    const res = await joinWorkspace(code.trim());
    if (res?.workspace) {
      setCode('');
      await refresh();
      setActiveId(res.workspace.id);
      setNotice(null);
    } else {
      setNotice('Invalid invite code.');
    }
  };

  const handleAddCompany = async () => {
    if (!activeId || !company.trim()) return;
    const list = await addWorkspaceCompany(activeId, company.trim());
    setDetail({ ...(detail || {}), watchlist: list });
    setCompany('');
  };

  const copyCode = async () => {
    if (!active?.invite_code) return;
    try {
      await navigator.clipboard.writeText(active.invite_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {}
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-1.5">
        {spaces.map((s) => (
          <button
            key={s.id}
            onClick={() => setActiveId(s.id)}
            className={`px-2.5 py-1 rounded-full text-[11px] font-semibold border transition-colors ${
              activeId === s.id
                ? 'bg-[#22D3EE] text-[#050B1A] border-[#22D3EE]'
                : 'bg-slate-100 dark:bg-[#0E1E32] text-slate-600 dark:text-[#94A3B8] border-slate-300 dark:border-[#1C3553]/60 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            {s.name}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <div className="flex gap-1.5">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handleCreate(); }}
            placeholder="New team name…"
            className="flex-1 min-w-0 px-2.5 py-1.5 rounded-full bg-white dark:bg-[#050B1A] border border-slate-300 dark:border-[#1C3553]/60 text-[12px] text-slate-800 dark:text-[#E2E8F0] placeholder:text-[#475569] focus:outline-none focus:border-[#22D3EE]/40"
            aria-label="Workspace name"
          />
          <button onClick={handleCreate} className="p-1.5 rounded-full bg-slate-100 dark:bg-[#0E1E32] border border-slate-300 dark:border-[#1C3553] text-slate-600 dark:text-[#94A3B8] hover:text-slate-900 dark:hover:text-white transition-colors" aria-label="Create workspace">
            <Plus size={13} />
          </button>
        </div>
        <div className="flex gap-1.5">
          <input
            value={code}
            onChange={(e) => setCode(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handleJoin(); }}
            placeholder="Invite code…"
            className="flex-1 min-w-0 px-2.5 py-1.5 rounded-full bg-white dark:bg-[#050B1A] border border-slate-300 dark:border-[#1C3553]/60 text-[12px] mono text-slate-800 dark:text-[#E2E8F0] placeholder:text-[#475569] focus:outline-none focus:border-[#22D3EE]/40"
            aria-label="Invite code"
          />
          <button onClick={handleJoin} className="p-1.5 rounded-full bg-slate-100 dark:bg-[#0E1E32] border border-slate-300 dark:border-[#1C3553] text-slate-600 dark:text-[#94A3B8] hover:text-slate-900 dark:hover:text-white transition-colors" aria-label="Join workspace">
            <LogIn size={13} />
          </button>
        </div>
      </div>
      {notice && <p className="mono text-[11px] tracking-[0.04em] text-[#B45309] dark:text-[#E8A253]">{notice}</p>}

      {active ? (
        <div className="rounded-[12px] border border-slate-200 dark:border-[#1C3553]/40 bg-white dark:bg-[#050B1A]/60 p-3 space-y-2.5">
          <div className="flex items-center gap-2">
            <Users size={13} className="text-[#0284C7] dark:text-[#22D3EE]" />
            <span className="text-[12px] font-bold text-slate-900 dark:text-white">{active.name}</span>
            <span className="mono text-[10px] text-[#475569]">{detail?.members?.length ?? 0} members</span>
            {active.invite_code && (
              <button onClick={copyCode} className="ml-auto inline-flex items-center gap-1 mono text-[10px] text-[#64748B] hover:text-slate-900 dark:hover:text-white transition-colors" title="Copy invite code">
                {copied ? <Check size={12} /> : <Copy size={12} />} {copied ? 'copied' : active.invite_code}
              </button>
            )}
          </div>
          <div>
            <p className="mono text-[10px] tracking-[0.08em] text-[#475569] mb-1.5">SHARED WATCHLIST</p>
            <div className="flex flex-wrap gap-1.5 mb-1.5">
              {(detail?.watchlist || []).map((c: string) => (
                <span key={c} className="inline-flex items-center gap-1 rounded-full bg-[#E8A253]/10 border border-[#E8A253]/15 pl-2.5 pr-1 py-0.5 text-[11px] font-semibold text-[#B45309] dark:text-[#E8A253]">
                  <button onClick={() => onCompanyClick?.(c)} className="hover:text-slate-900 dark:hover:text-white transition-colors">{c}</button>
                  <button
                    onClick={async () => {
                      const list = await removeWorkspaceCompany(active.id, c);
                      setDetail({ ...(detail || {}), watchlist: list });
                    }}
                    className="p-0.5 rounded-full hover:text-slate-900 dark:hover:text-white transition-colors"
                    aria-label={`Remove ${c}`}
                  >
                    <X size={11} />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-1.5">
              <input
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') handleAddCompany(); }}
                placeholder="Add company…"
                className="flex-1 min-w-0 px-2.5 py-1 rounded-full bg-white dark:bg-[#050B1A] border border-slate-300 dark:border-[#1C3553]/60 text-[11px] text-slate-800 dark:text-[#E2E8F0] placeholder:text-[#475569] focus:outline-none focus:border-[#E8A253]/40"
                aria-label="Add shared company"
              />
              <button onClick={handleAddCompany} className="px-2.5 py-1 rounded-full bg-[#E8A253]/10 border border-[#E8A253]/20 text-[11px] font-semibold text-[#B45309] dark:text-[#E8A253] hover:bg-[#E8A253]/15 transition-colors">
                Add
              </button>
            </div>
          </div>
          {(detail?.briefs || []).length > 0 && (
            <div>
              <p className="mono text-[10px] tracking-[0.08em] text-[#475569] mb-1.5">TEAM BRIEFS</p>
              <ul className="space-y-1">
                {detail.briefs.map((b: any) => (
                  <li key={b.id}>
                    <Link to={`/b/${b.id}`} className="block truncate rounded-[8px] bg-slate-100 dark:bg-[#0E1E32] border border-slate-300 dark:border-[#1C3553]/40 px-2.5 py-1.5 text-[11px] text-slate-700 dark:text-[#CBD5E1] hover:text-slate-900 dark:hover:text-white hover:border-[#22D3EE]/25 transition-colors">
                      {b.query_text}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <p className="text-[12px] text-[#475569]">Create a team or join with an invite code to share a watchlist and briefs.</p>
      )}
    </div>
  );
};
