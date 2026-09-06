import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { SignedIn, SignedOut, useAuth } from '@clerk/clerk-react';
import { MessageSquare, Send, Trash2 } from 'lucide-react';
import {
  fetchBriefComments,
  postBriefComment,
  deleteBriefComment,
  setAuthTokenGetter,
} from '../api/siliconpulseApi';

interface BriefCommentsProps {
  briefId: string;
}

export const BriefComments: React.FC<BriefCommentsProps> = ({ briefId }) => {
  const { getToken, userId } = useAuth();
  const [comments, setComments] = useState<any[]>([]);
  const [draft, setDraft] = useState('');
  const [posting, setPosting] = useState(false);

  useEffect(() => {
    setAuthTokenGetter(() => getToken());
    return () => setAuthTokenGetter(null);
  }, [getToken]);

  useEffect(() => {
    let cancelled = false;
    fetchBriefComments(briefId).then((c) => { if (!cancelled) setComments(c); }).catch(() => {});
    return () => { cancelled = true; };
  }, [briefId]);

  const handlePost = async () => {
    const body = draft.trim();
    if (!body || posting) return;
    setPosting(true);
    try {
      const row = await postBriefComment(briefId, body);
      if (row) {
        setComments([...comments, row]);
        setDraft('');
      }
    } finally {
      setPosting(false);
    }
  };

  const handleDelete = async (commentId: string) => {
    const ok = await deleteBriefComment(commentId);
    if (ok) setComments(comments.filter((c) => c.id !== commentId));
  };

  return (
    <div className="rounded-[16px] border border-[#1C3553]/40 bg-[#0B1426]/60 p-5">
      <p className="flex items-center gap-1.5 mono text-[10px] tracking-[0.12em] font-semibold text-[#64748B] mb-3">
        <MessageSquare size={12} /> DISCUSSION ({comments.length})
      </p>
      {comments.length === 0 ? (
        <p className="text-[12px] leading-relaxed text-[#475569]">No comments yet. Signed-in readers can start the thread.</p>
      ) : (
        <ul className="space-y-2.5">
          {comments.map((c: any) => (
            <li key={c.id} className="rounded-[10px] bg-[#050B1A] border border-[#1C3553]/40 p-3">
              <p className="text-[13px] leading-relaxed text-[#E2E8F0] whitespace-pre-wrap break-words">{c.body}</p>
              <p className="mt-1.5 flex items-center gap-2 mono text-[10px] tracking-[0.06em] text-[#475569]">
                <span>{String(c.user_id || 'analyst').slice(0, 12)}</span>
                <span>•</span>
                <span>{c.created_at ? new Date(c.created_at).toLocaleString() : ''}</span>
                {userId && c.user_id === userId && (
                  <button onClick={() => handleDelete(c.id)} className="ml-auto p-1 rounded-full hover:text-red-400 transition-colors" aria-label="Delete comment">
                    <Trash2 size={12} />
                  </button>
                )}
              </p>
            </li>
          ))}
        </ul>
      )}
      <SignedIn>
        <div className="mt-3 flex gap-2">
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handlePost(); }}
            placeholder="Add analysis or a follow-up question… (max 2000 chars)"
            maxLength={2000}
            className="flex-1 min-w-0 px-3 py-2 rounded-full bg-[#050B1A] border border-[#1C3553]/60 text-[12.5px] text-[#E2E8F0] placeholder:text-[#475569] focus:outline-none focus:border-[#22D3EE]/40"
            aria-label="Comment"
          />
          <button
            onClick={handlePost}
            disabled={posting || !draft.trim()}
            className="shrink-0 w-9 h-9 rounded-full flex items-center justify-center bg-[#E8A253] text-[#050B1A] hover:bg-[#F0A85E] transition-colors disabled:opacity-40"
            aria-label="Post comment"
          >
            <Send size={15} />
          </button>
        </div>
      </SignedIn>
      <SignedOut>
        <p className="mt-3 text-[12px] text-[#64748B]">
          <Link to="/sign-in" className="text-[#22D3EE] hover:underline font-medium">Sign in</Link> to join the discussion.
        </p>
      </SignedOut>
    </div>
  );
};
