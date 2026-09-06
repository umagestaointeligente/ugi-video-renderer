-- LSI Career 360 — Master metrics champion alignment V16
-- Aggregate matching metrics only from the active champion engine.

create or replace function career_private.refresh_master_metrics()
returns void
language plpgsql
security definer
set search_path to 'pg_catalog','public','career_private'
as $$
declare
  v_engine text;
begin
  select champion_version into v_engine
  from public.career_engine_control
  where component='matching' and status='active';

  v_engine := coalesce(v_engine,'v2.0');

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
    (select count(*) from public.career_matches where engine_version=v_engine),
    (select count(*) from public.career_matches where engine_version=v_engine and classification in ('QUALIFIED','QUALIFIED_SALARY_CONFIRM')),
    (select count(*) from public.career_matches where engine_version=v_engine and classification='BLOCKED_PRIVACY'),
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

select career_private.refresh_master_metrics();
