-- LSI Career 360 — Manual research limit alignment V16
-- Keep the RPC contract aligned with career-opportunity-research V5, which caps source_limit at 5.

create or replace function public.career_request_research_now(
  p_user_id uuid,
  p_source_limit integer default 5
)
returns bigint
language plpgsql
security definer
set search_path to 'public','extensions','vault'
as $$
declare
  v_request_id bigint;
  v_last timestamptz;
  v_limit integer := greatest(1,least(coalesce(p_source_limit,5),5));
  v_secret text;
begin
  if p_user_id is null then raise exception 'USER_REQUIRED'; end if;
  if not exists(select 1 from public.career_profiles where user_id=p_user_id and onboarding_status='agent_ready') then
    raise exception 'AGENT_NOT_READY';
  end if;

  select max(created_at) into v_last
  from public.career_audit_events
  where user_id=p_user_id and event_type='opportunity_research_user';

  if v_last is not null and v_last > now()-interval '2 minutes' then
    raise exception 'RESEARCH_COOLDOWN';
  end if;

  select decrypted_secret into v_secret
  from vault.decrypted_secrets
  where name='career_opportunity_research_cron'
  limit 1;

  if v_secret is null then raise exception 'RESEARCH_SECRET_MISSING'; end if;

  select net.http_post(
    url := 'https://nxjdnzdxclszqyqrkwdk.supabase.co/functions/v1/career-opportunity-research',
    body := jsonb_build_object('source_limit',v_limit),
    params := '{}'::jsonb,
    headers := jsonb_build_object('Content-Type','application/json','x-lsi-research-secret',v_secret),
    timeout_milliseconds := 30000
  ) into v_request_id;

  insert into public.career_audit_events(user_id,event_type,entity_type,outcome,reason_code,metadata_safe)
  values(
    p_user_id,'opportunity_research_user','career_opportunity_research','started','USER_REQUESTED',
    jsonb_build_object('request_id',v_request_id,'source_limit',v_limit,'research_contract','v5-max-5')
  );

  return v_request_id;
end;
$$;
