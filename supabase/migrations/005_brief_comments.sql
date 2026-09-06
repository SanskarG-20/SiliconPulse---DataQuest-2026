-- SiliconPulse Phase 3.1 — brief annotations (comments on shared briefs)
-- Apply in Supabase Dashboard → SQL Editor or via `supabase db push`.

create table if not exists public.brief_comments (
  id uuid primary key default gen_random_uuid(),
  brief_id uuid not null references public.briefs(id) on delete cascade,
  user_id text not null references public.users(id) on delete cascade,
  body text not null check (char_length(body) >= 1 and char_length(body) <= 2000),
  created_at timestamptz default now()
);

alter table public.brief_comments enable row level security;

-- Authors manage their own comments
drop policy if exists "Users can manage own brief comments" on public.brief_comments;
create policy "Users can manage own brief comments" on public.brief_comments
  for all using (user_id = auth.uid()::text) with check (user_id = auth.uid()::text);

-- Anyone can read comments on public briefs
drop policy if exists "Anyone can read comments on public briefs" on public.brief_comments;
create policy "Anyone can read comments on public briefs" on public.brief_comments
  for select using (
    exists (select 1 from public.briefs where public.briefs.id = brief_id and public.briefs.is_public = true)
  );

create index if not exists idx_brief_comments_brief_id on public.brief_comments(brief_id, created_at);
create index if not exists idx_brief_comments_user_id on public.brief_comments(user_id);
