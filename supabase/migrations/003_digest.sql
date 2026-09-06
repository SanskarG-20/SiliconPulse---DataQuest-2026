-- SiliconPulse Phase 2.3 — scheduled morning digest prefs
-- Apply in Supabase Dashboard → SQL Editor or via `supabase db push`.

create table if not exists public.digest_prefs (
  user_id text primary key references public.users(id) on delete cascade,
  enabled boolean not null default false,
  hour_utc int not null default 11 check (hour_utc >= 0 and hour_utc <= 23),
  email text,
  webhook_url text,
  last_sent_at timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table public.digest_prefs enable row level security;

drop policy if exists "Users can manage own digest prefs" on public.digest_prefs;
create policy "Users can manage own digest prefs" on public.digest_prefs
  for all using (user_id = auth.uid()::text) with check (user_id = auth.uid()::text);

create index if not exists idx_digest_prefs_enabled_hour on public.digest_prefs(enabled, hour_utc);
