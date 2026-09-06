-- LSI Career 360 — Radar runtime truth V16
-- Service-only status primitive backed directly by pg_cron state.

create or replace function public.career_radar_runtime_status()
returns table(
  cron_job_id bigint,
  cron_schedule text,
  cron_active boolean,
  source_limit integer,
  cycle_minutes integer,
  matching_engine text,
  rollback_engine text,
  role_search_plan text
)
language plpgsql
stable
security definer
set search_path to 'pg_catalog','public','cron'
as $$
declare
  v_job record;
  v_limit integer;
  v_cycle integer;
  v_match record;
begin
  select j.jobid,j.schedule,j.active,j.command
  into v_job
  from cron.job j
  where j.jobname='career-opportunity-research'
  order by j.jobid desc
  limit 1;

  if not found then
    return query select null::bigint,null::text,false,null::integer,null::integer,null::text,null::text,'role-search-v2'::text;
    return;
  end if;

  begin
    v_limit := nullif((regexp_match(v_job.command,'source_limit[^0-9]+([0-9]+)'))[1],'')::integer;
  exception when others then
    v_limit := null;
  end;

  -- Common pg_cron minute patterns used by Career. Unknown patterns remain null rather than guessed.
  if v_job.schedule ~ '^[0-9]+ \* \* \* \*$' then
    v_cycle := 60;
  elsif v_job.schedule ~ '^\*/[0-9]+ \* \* \* \*$' then
    v_cycle := split_part(split_part(v_job.schedule,' ',1),'/',2)::integer;
  elsif v_job.schedule ~ '^[0-9]+,[0-9]+ \* \* \* \*$' then
    v_cycle := 30;
  else
    v_cycle := null;
  end if;

  select champion_version,rollback_version,status into v_match
  from public.career_engine_control
  where component='matching';

  return query select
    v_job.jobid,
    v_job.schedule,
    coalesce(v_job.active,false),
    v_limit,
    v_cycle,
    case when v_match.status='active' then v_match.champion_version else null end,
    v_match.rollback_version,
    'role-search-v2'::text;
end;
$$;

revoke all on function public.career_radar_runtime_status() from public,anon,authenticated;
grant execute on function public.career_radar_runtime_status() to service_role;

comment on function public.career_radar_runtime_status() is
  'Service-only radar status derived from the live pg_cron job and matching control plane; unknown schedules return null cadence instead of guessing.';
