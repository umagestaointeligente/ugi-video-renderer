-- Career 360 — reproducible O*NET bulk sync V1
-- Pinned taxonomy evidence layer. Does not mutate curated Role Graph aliases or matching.

create table if not exists public.career_onet_sync_state (
  singleton boolean primary key default true check (singleton),
  source_version text not null default '31.0',
  occupation_request_id bigint,
  job_titles_request_id bigint,
  status text not null default 'idle' check (status in ('idle','requested','succeeded','failed')),
  requested_at timestamptz,
  completed_at timestamptz,
  raw_occupation_rows integer,
  raw_job_title_rows integer,
  persisted_occupation_rows integer,
  persisted_job_title_rows integer,
  duplicate_normalized_job_title_rows integer,
  error_safe text,
  updated_at timestamptz not null default now()
);

alter table public.career_onet_sync_state enable row level security;
revoke all on table public.career_onet_sync_state from public, anon, authenticated;
grant select,insert,update,delete on table public.career_onet_sync_state to service_role;

drop policy if exists career_onet_sync_state_no_client_access on public.career_onet_sync_state;
create policy career_onet_sync_state_no_client_access
  on public.career_onet_sync_state
  for all
  to anon, authenticated
  using (false)
  with check (false);

insert into public.career_onet_sync_state(singleton,source_version,status)
values(true,'31.0','idle')
on conflict(singleton) do nothing;

create or replace function public.career_onet_begin_sync(p_source_version text default '31.0')
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, public, extensions, net
as $$
declare
  v_version text := trim(coalesce(p_source_version,''));
  v_slug text;
  v_occ_url text;
  v_titles_url text;
  v_occ_request bigint;
  v_titles_request bigint;
begin
  if v_version !~ '^[0-9]+[.][0-9]+$' then
    raise exception 'INVALID_ONET_VERSION';
  end if;
  v_slug := replace(v_version,'.','_');
  v_occ_url := format('https://www.onetcenter.org/dl_files/database/db_%s_json/occupation_data.json',v_slug);
  v_titles_url := format('https://www.onetcenter.org/dl_files/database/db_%s_json/job_titles.json',v_slug);

  select net.http_get(url := v_occ_url, timeout_milliseconds := 60000) into v_occ_request;
  select net.http_get(url := v_titles_url, timeout_milliseconds := 60000) into v_titles_request;

  insert into public.career_onet_sync_state(
    singleton,source_version,occupation_request_id,job_titles_request_id,status,requested_at,completed_at,
    raw_occupation_rows,raw_job_title_rows,persisted_occupation_rows,persisted_job_title_rows,
    duplicate_normalized_job_title_rows,error_safe,updated_at
  ) values(
    true,v_version,v_occ_request,v_titles_request,'requested',now(),null,
    null,null,null,null,null,null,now()
  )
  on conflict(singleton) do update set
    source_version=excluded.source_version,
    occupation_request_id=excluded.occupation_request_id,
    job_titles_request_id=excluded.job_titles_request_id,
    status='requested',requested_at=excluded.requested_at,completed_at=null,
    raw_occupation_rows=null,raw_job_title_rows=null,persisted_occupation_rows=null,persisted_job_title_rows=null,
    duplicate_normalized_job_title_rows=null,error_safe=null,updated_at=now();

  return jsonb_build_object(
    'status','requested','source_version',v_version,
    'occupation_request_id',v_occ_request,'job_titles_request_id',v_titles_request
  );
end;
$$;

revoke all on function public.career_onet_begin_sync(text) from public, anon, authenticated;
grant execute on function public.career_onet_begin_sync(text) to service_role;

create or replace function public.career_onet_finalize_sync()
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, public, extensions, net
as $$
declare
  s public.career_onet_sync_state%rowtype;
  v_occ_status integer;
  v_titles_status integer;
  v_occ_error text;
  v_titles_error text;
  v_occ jsonb;
  v_titles jsonb;
  v_raw_occ integer;
  v_raw_titles integer;
  v_unique_titles integer;
  v_missing_codes integer;
  v_persist_occ integer;
  v_persist_titles integer;
  v_occ_url text;
  v_titles_url text;
begin
  select * into s from public.career_onet_sync_state where singleton=true for update;
  if not found or s.status <> 'requested' then
    return jsonb_build_object('status',coalesce(s.status,'idle'),'processed',false);
  end if;

  select status_code,error_msg,content::jsonb
    into v_occ_status,v_occ_error,v_occ
  from net._http_response where id=s.occupation_request_id;
  select status_code,error_msg,content::jsonb
    into v_titles_status,v_titles_error,v_titles
  from net._http_response where id=s.job_titles_request_id;

  if v_occ_status is null or v_titles_status is null then
    return jsonb_build_object('status','requested','processed',false,'reason','RESPONSES_NOT_READY');
  end if;

  if v_occ_status <> 200 or v_titles_status <> 200 then
    update public.career_onet_sync_state set
      status='failed',completed_at=now(),error_safe=left(format('HTTP occ=%s titles=%s occ_error=%s titles_error=%s',v_occ_status,v_titles_status,coalesce(v_occ_error,''),coalesce(v_titles_error,'')),500),updated_at=now()
    where singleton=true;
    return jsonb_build_object('status','failed','processed',true,'reason','SOURCE_HTTP_FAILED','occupation_status',v_occ_status,'job_titles_status',v_titles_status);
  end if;

  begin
    select jsonb_array_length(coalesce(v_occ->'row','[]'::jsonb)) into v_raw_occ;
    select jsonb_array_length(coalesce(v_titles->'row','[]'::jsonb)) into v_raw_titles;

    if v_raw_occ < 500 or v_raw_titles < 10000 then
      raise exception 'SOURCE_ROW_COUNT_TOO_LOW occ=% titles=%',v_raw_occ,v_raw_titles;
    end if;

    select count(*) into v_unique_titles
    from (
      select distinct
        x->>'onetsoc_code' as onetsoc_code,
        public.career_normalize_text(x->>'job_title') as normalized_job_title
      from jsonb_array_elements(v_titles->'row') x
      where nullif(x->>'onetsoc_code','') is not null
        and nullif(public.career_normalize_text(x->>'job_title'),'') is not null
    ) d;

    select count(*) into v_missing_codes
    from (
      select distinct x->>'onetsoc_code' as code
      from jsonb_array_elements(v_titles->'row') x
      where nullif(x->>'onetsoc_code','') is not null
    ) jt
    left join (
      select distinct x->>'onetsoc_code' as code
      from jsonb_array_elements(v_occ->'row') x
      where nullif(x->>'onetsoc_code','') is not null
    ) o using(code)
    where o.code is null;

    if v_missing_codes <> 0 then
      raise exception 'SOURCE_REFERENTIAL_MISMATCH missing_codes=%',v_missing_codes;
    end if;

    v_occ_url := format('https://www.onetcenter.org/dl_files/database/db_%s_json/occupation_data.json',replace(s.source_version,'.','_'));
    v_titles_url := format('https://www.onetcenter.org/dl_files/database/db_%s_json/job_titles.json',replace(s.source_version,'.','_'));

    delete from public.career_onet_job_titles;
    delete from public.career_onet_occupations;

    insert into public.career_onet_occupations(
      onetsoc_code,title,normalized_title,description_safe,source_version,source_url,source_fetched_at,updated_at
    )
    select
      x->>'onetsoc_code',
      x->>'title',
      public.career_normalize_text(x->>'title'),
      nullif(x->>'description',''),
      s.source_version,
      v_occ_url,
      now(),now()
    from jsonb_array_elements(v_occ->'row') x
    where nullif(x->>'onetsoc_code','') is not null
      and nullif(x->>'title','') is not null;

    insert into public.career_onet_job_titles(
      onetsoc_code,occupation_title,job_title,normalized_job_title,short_title,source_codes,
      source_version,source_url,source_fetched_at,updated_at
    )
    select onetsoc_code,occupation_title,job_title,normalized_job_title,short_title,source_codes,
           s.source_version,v_titles_url,now(),now()
    from (
      select distinct on(x->>'onetsoc_code',public.career_normalize_text(x->>'job_title'))
        x->>'onetsoc_code' as onetsoc_code,
        x->>'title' as occupation_title,
        x->>'job_title' as job_title,
        public.career_normalize_text(x->>'job_title') as normalized_job_title,
        nullif(x->>'short_title','') as short_title,
        nullif(x->>'sources','') as source_codes
      from jsonb_array_elements(v_titles->'row') x
      where nullif(x->>'onetsoc_code','') is not null
        and nullif(x->>'title','') is not null
        and nullif(x->>'job_title','') is not null
        and nullif(public.career_normalize_text(x->>'job_title'),'') is not null
      order by x->>'onetsoc_code',public.career_normalize_text(x->>'job_title'),x->>'job_title'
    ) d;

    select count(*) into v_persist_occ from public.career_onet_occupations;
    select count(*) into v_persist_titles from public.career_onet_job_titles;

    if v_persist_occ <> v_raw_occ or v_persist_titles <> v_unique_titles then
      raise exception 'PERSISTED_COUNT_MISMATCH occ=%/% titles=%/%',v_persist_occ,v_raw_occ,v_persist_titles,v_unique_titles;
    end if;

    update public.career_role_taxonomy_sources set
      integration_status='live_bulk',
      source_version=s.source_version,
      last_synced_at=now(),
      notes_safe=coalesce(notes_safe,'{}'::jsonb) || jsonb_build_object(
        'mode','diagnostic_evidence_only',
        'auto_promote_to_role_graph',false,
        'raw_occupation_rows',v_raw_occ,
        'raw_job_title_rows',v_raw_titles,
        'persisted_job_title_rows',v_persist_titles,
        'deduplicated_normalized_rows',v_raw_titles-v_persist_titles,
        'sync_engine','pg_net_transactional_v1'
      ),
      updated_at=now()
    where source_key='onet';

    update public.career_onet_sync_state set
      status='succeeded',completed_at=now(),raw_occupation_rows=v_raw_occ,raw_job_title_rows=v_raw_titles,
      persisted_occupation_rows=v_persist_occ,persisted_job_title_rows=v_persist_titles,
      duplicate_normalized_job_title_rows=v_raw_titles-v_persist_titles,error_safe=null,updated_at=now()
    where singleton=true;

  exception when others then
    update public.career_onet_sync_state set
      status='failed',completed_at=now(),error_safe=left(sqlerrm,500),updated_at=now()
    where singleton=true;
    return jsonb_build_object('status','failed','processed',true,'reason',left(sqlerrm,300));
  end;

  return jsonb_build_object(
    'status','succeeded','processed',true,'source_version',s.source_version,
    'raw_occupation_rows',v_raw_occ,'raw_job_title_rows',v_raw_titles,
    'persisted_occupation_rows',v_persist_occ,'persisted_job_title_rows',v_persist_titles,
    'duplicate_normalized_job_title_rows',v_raw_titles-v_persist_titles
  );
end;
$$;

revoke all on function public.career_onet_finalize_sync() from public, anon, authenticated;
grant execute on function public.career_onet_finalize_sync() to service_role;

-- Monthly integrity refresh of the pinned production version, plus a cheap finalizer.
do $$
declare v_jobid bigint;
begin
  select jobid into v_jobid from cron.job where jobname='career-onet-monthly-refresh' limit 1;
  if v_jobid is not null then perform cron.unschedule(v_jobid); end if;
  perform cron.schedule('career-onet-monthly-refresh','17 3 10 * *',$cmd$
    select public.career_onet_begin_sync('31.0');
  $cmd$);

  select jobid into v_jobid from cron.job where jobname='career-onet-sync-finalizer' limit 1;
  if v_jobid is not null then perform cron.unschedule(v_jobid); end if;
  perform cron.schedule('career-onet-sync-finalizer','*/10 * * * *',$cmd$
    select public.career_onet_finalize_sync();
  $cmd$);
end $$;
