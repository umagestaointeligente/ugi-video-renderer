begin;

revoke all on function public.career_master_status_v1() from public, anon, authenticated;
drop function if exists public.career_master_status_v1();
revoke all on function public.career_score_opportunity_self(uuid, boolean) from public, anon, authenticated;
drop function if exists public.career_score_opportunity_self(uuid, boolean);

create table if not exists public.career_master_metrics (
  id smallint primary key check (id = 1),
  users bigint not null default 0,
  masters bigint not null default 0,
  documents bigint not null default 0,
  quarantined bigint not null default 0,
  rejected bigint not null default 0,
  drafts bigint not null default 0,
  matches bigint not null default 0,
  qualified bigint not null default 0,
  privacy_blocks bigint not null default 0,
  incidents_open bigint not null default 0,
  incidents_external bigint not null default 0,
  updated_at timestamptz not null default now()
);

alter table public.career_master_metrics enable row level security;
revoke all on public.career_master_metrics from anon, authenticated;
grant select on public.career_master_metrics to authenticated;

drop policy if exists career_master_metrics_select_master on public.career_master_metrics;
create policy career_master_metrics_select_master
on public.career_master_metrics
for select to authenticated
using (
  exists (
    select 1
    from public.career_user_roles r
    where r.user_id = (select auth.uid())
      and r.role = 'master'
  )
);

create or replace function career_private.refresh_master_metrics()
returns void
language plpgsql
security definer
set search_path = pg_catalog, public, career_private
as $$
begin
  insert into public.career_master_metrics(
    id, users, masters, documents, quarantined, rejected, drafts, matches,
    qualified, privacy_blocks, incidents_open, incidents_external, updated_at
  )
  values (
    1,
    (select count(*) from public.career_user_roles),
    (select count(*) from public.career_user_roles where role='master'),
    (select count(*) from public.career_documents),
    (select count(*) from public.career_documents where file_status='quarantined'),
    (select count(*) from public.career_documents where file_status='rejected'),
    (select count(*) from public.career_profile_drafts),
    (select count(*) from public.career_matches),
    (select count(*) from public.career_matches where classification in ('QUALIFIED','QUALIFIED_SALARY_CONFIRM')),
    (select count(*) from public.career_matches where classification='BLOCKED_PRIVACY'),
    (select count(*) from public.career_incidents where status in ('open','needs_user')),
    (select count(*) from public.career_incidents where status='external_block'),
    now()
  )
  on conflict (id) do update set
    users=excluded.users,
    masters=excluded.masters,
    documents=excluded.documents,
    quarantined=excluded.quarantined,
    rejected=excluded.rejected,
    drafts=excluded.drafts,
    matches=excluded.matches,
    qualified=excluded.qualified,
    privacy_blocks=excluded.privacy_blocks,
    incidents_open=excluded.incidents_open,
    incidents_external=excluded.incidents_external,
    updated_at=excluded.updated_at;
end;
$$;
revoke all on function career_private.refresh_master_metrics() from public, anon, authenticated;
grant execute on function career_private.refresh_master_metrics() to service_role;

select career_private.refresh_master_metrics();

do $$
declare existing_job bigint;
begin
  select jobid into existing_job from cron.job where jobname='career-master-metrics-refresh' limit 1;
  if existing_job is not null then perform cron.unschedule(existing_job); end if;
  perform cron.schedule('career-master-metrics-refresh','*/5 * * * *','select career_private.refresh_master_metrics();');
end $$;

commit;