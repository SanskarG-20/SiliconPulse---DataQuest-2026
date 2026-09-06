-- SiliconPulse Phase 2.4 — API keys + team webhooks
-- Apply in Supabase Dashboard → SQL Editor or via `supabase db push`.

-- API keys for bots/CI (only sha256 hash stored; raw key shown once at creation)
create table if not exists public.api_keys (
  id uuid primary key default gen_random_uuid(),
  user_id text not null references public.users(id) on delete cascade,
  name text not null default 'default',
  key_hash text not null unique,
  key_prefix text not null default '',
  revoked boolean not null default false,
  last_used_at timestamptz,
  created_at timestamptz default now()
);

-- Team webhooks (Slack/Discord incoming webhooks for spike alerts)
create table if not exists public.team_webhooks (
  id uuid primary key default gen_random_uuid(),
  user_id text not null references public.users(id) on delete cascade,
  url text not null,
  events text[] not null default array['spike.alert'],
  enabled boolean not null default true,
  last_sent_at timestamptz,
  created_at timestamptz default now()
);

alter table public.api_keys enable row level security;
alter table public.team_webhooks enable row level security;

drop policy if exists "Users can manage own api keys" on public.api_keys;
create policy "Users can manage own api keys" on public.api_keys
  for all using (user_id = auth.uid()::text) with check (user_id = auth.uid()::text);

drop policy if exists "Users can manage own team webhooks" on public.team_webhooks;
create policy "Users can manage own team webhooks" on public.team_webhooks
  for all using (user_id = auth.uid()::text) with check (user_id = auth.uid()::text);

create index if not exists idx_api_keys_user_id on public.api_keys(user_id);
create index if not exists idx_api_keys_hash on public.api_keys(key_hash);
create index if not exists idx_team_webhooks_user_id on public.team_webhooks(user_id);
create index if not exists idx_team_webhooks_enabled on public.team_webhooks(enabled);
