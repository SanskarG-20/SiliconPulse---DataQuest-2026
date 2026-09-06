-- SiliconPulse Phase 1 — watchlists, briefs
-- Apply in Supabase Dashboard → SQL Editor or via `supabase db push`.

-- Watchlists: one row per (user, company)
create table if not exists public.watchlists (
  id uuid primary key default gen_random_uuid(),
  user_id text not null references public.users(id) on delete cascade,
  company text not null,
  created_at timestamptz default now(),
  unique (user_id, company)
);

-- Briefs: shareable intelligence reports
create table if not exists public.briefs (
  id uuid primary key default gen_random_uuid(),
  user_id text not null references public.users(id) on delete cascade,
  query_text text not null,
  insight text not null,
  evidence jsonb not null default '[]'::jsonb,
  is_public boolean not null default true,
  created_at timestamptz default now()
);

alter table public.watchlists enable row level security;
alter table public.briefs enable row level security;

drop policy if exists "Users can manage own watchlist" on public.watchlists;
create policy "Users can manage own watchlist" on public.watchlists
  for all using (user_id = auth.uid()::text) with check (user_id = auth.uid()::text);

drop policy if exists "Users can manage own briefs" on public.briefs;
create policy "Users can manage own briefs" on public.briefs
  for all using (user_id = auth.uid()::text) with check (user_id = auth.uid()::text);

-- Public read for shared briefs (anon + authenticated can read is_public rows)
drop policy if exists "Anyone can read public briefs" on public.briefs;
create policy "Anyone can read public briefs" on public.briefs
  for select using (is_public = true);

create index if not exists idx_watchlists_user_id on public.watchlists(user_id);
create index if not exists idx_briefs_user_id on public.briefs(user_id);
create index if not exists idx_briefs_created_at on public.briefs(created_at desc);
