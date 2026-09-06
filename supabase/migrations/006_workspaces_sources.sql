-- SiliconPulse Phase 3.2 — team workspaces, shared watchlists, custom RSS feeds
-- Apply in Supabase Dashboard → SQL Editor or via `supabase db push`.

-- Workspaces (invite code shared out-of-band)
create table if not exists public.workspaces (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  owner_id text not null references public.users(id) on delete cascade,
  invite_code text not null unique,
  created_at timestamptz default now()
);

create table if not exists public.workspace_members (
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  user_id text not null references public.users(id) on delete cascade,
  role text not null default 'member',
  created_at timestamptz default now(),
  primary key (workspace_id, user_id)
);

create table if not exists public.workspace_watchlist (
  workspace_id uuid not null references public.workspaces(id) on delete cascade,
  company text not null,
  added_by text,
  created_at timestamptz default now(),
  primary key (workspace_id, company)
);

-- Link briefs to a workspace for team sharing (nullable: personal briefs unaffected)
alter table public.briefs add column if not exists workspace_id uuid references public.workspaces(id) on delete set null;

-- Custom RSS/Atom feeds per user
create table if not exists public.rss_feeds (
  id uuid primary key default gen_random_uuid(),
  user_id text not null references public.users(id) on delete cascade,
  url text not null,
  label text not null default '',
  enabled boolean not null default true,
  last_fetched_at timestamptz,
  last_error text,
  created_at timestamptz default now(),
  unique (user_id, url)
);

alter table public.workspaces enable row level security;
alter table public.workspace_members enable row level security;
alter table public.workspace_watchlist enable row level security;
alter table public.rss_feeds enable row level security;

drop policy if exists "Users can manage own workspaces" on public.workspaces;
create policy "Users can manage own workspaces" on public.workspaces
  for all using (owner_id = auth.uid()::text) with check (owner_id = auth.uid()::text);

drop policy if exists "Members can read workspaces" on public.workspaces;
create policy "Members can read workspaces" on public.workspaces
  for select using (
    owner_id = auth.uid()::text
    or exists (select 1 from public.workspace_members where workspace_id = id and user_id = auth.uid()::text)
  );

drop policy if exists "Users can manage workspace membership" on public.workspace_members;
create policy "Users can manage workspace membership" on public.workspace_members
  for all using (user_id = auth.uid()::text) with check (user_id = auth.uid()::text);

drop policy if exists "Users can manage own rss feeds" on public.rss_feeds;
create policy "Users can manage own rss feeds" on public.rss_feeds
  for all using (user_id = auth.uid()::text) with check (user_id = auth.uid()::text);

-- Watchlist rows readable/writable by workspace members (service role bypasses; enforced in code too)
drop policy if exists "Members can manage workspace watchlist" on public.workspace_watchlist;
create policy "Members can manage workspace watchlist" on public.workspace_watchlist
  for all using (
    exists (select 1 from public.workspace_members where workspace_id = workspace_watchlist.workspace_id and user_id = auth.uid()::text)
    or exists (select 1 from public.workspaces where id = workspace_watchlist.workspace_id and owner_id = auth.uid()::text)
  ) with check (
    exists (select 1 from public.workspace_members where workspace_id = workspace_watchlist.workspace_id and user_id = auth.uid()::text)
    or exists (select 1 from public.workspaces where id = workspace_watchlist.workspace_id and owner_id = auth.uid()::text)
  );

create index if not exists idx_workspaces_owner on public.workspaces(owner_id);
create index if not exists idx_workspace_members_user on public.workspace_members(user_id);
create index if not exists idx_briefs_workspace on public.briefs(workspace_id);
create index if not exists idx_rss_feeds_user on public.rss_feeds(user_id);
create index if not exists idx_rss_feeds_enabled on public.rss_feeds(enabled);
