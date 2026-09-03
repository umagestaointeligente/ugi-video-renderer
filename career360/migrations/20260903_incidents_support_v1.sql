begin;

create table if not exists public.career_incidents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  category text not null check (category in ('document','auth','privacy','matching','opportunity','agent','external','other')),
  status text not null default 'open' check (status in ('open','resolved','needs_user','external_block')),
  reason_code text not null,
  summary_safe text not null,
  resolution_safe text,
  correlation_id uuid not null default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  resolved_at timestamptz
);

create index if not exists idx_career_incidents_user_status
  on public.career_incidents(user_id, status, created_at desc);

alter table public.career_incidents enable row level security;
revoke all on table public.career_incidents from anon, authenticated;
grant select on table public.career_incidents to authenticated;

create policy career_incidents_select_own
on public.career_incidents
for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

commit;
