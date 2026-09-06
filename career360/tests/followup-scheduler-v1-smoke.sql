-- LSI Career 360 — Follow-up Scheduler V1 smoke
-- Safe to run in production: all mutations are wrapped in a transaction and rolled back.

begin;

do $$
declare
  v_user uuid;
  v_app uuid;
  v_first record;
  v_replay record;
  v_eval record;
  v_mail_before bigint;
  v_mail_after bigint;
begin
  select id into v_user from auth.users order by created_at limit 1;
  if v_user is null then raise exception 'SMOKE_REQUIRES_ONE_AUTH_USER'; end if;

  select count(*) into v_mail_before from public.career_mail_actions;

  insert into public.career_action_permissions(user_id,allow_followup_draft)
  values(v_user,false)
  on conflict(user_id) do update set allow_followup_draft=false,updated_at=now();

  insert into public.career_applications(
    user_id,status,external_application_ref_hash,applied_at,last_activity_at,evidence_safe
  ) values (
    v_user,'applied','smoke-app-'||gen_random_uuid()::text,now()-interval '2 minutes',now()-interval '2 minutes',
    jsonb_build_object('smoke',true)
  ) returning id into v_app;

  select * into v_first from public.career_schedule_followup(v_user,v_app,now()-interval '1 minute','application_followup');
  if v_first.followup_status <> 'scheduled' or v_first.idempotent then
    raise exception 'FOLLOWUP_FIRST_SCHEDULE_FAILED';
  end if;

  select * into v_replay from public.career_schedule_followup(v_user,v_app,now()-interval '1 minute','application_followup');
  if not v_replay.idempotent or v_replay.followup_id <> v_first.followup_id then
    raise exception 'FOLLOWUP_IDEMPOTENCY_FAILED';
  end if;

  select * into v_eval from public.career_process_due_followups(100);
  if v_eval.waiting_permission <> 1 or v_eval.ready_for_orchestration <> 0 then
    raise exception 'FOLLOWUP_PERMISSION_GATE_FAILED';
  end if;

  update public.career_action_permissions set allow_followup_draft=true,updated_at=now() where user_id=v_user;
  select * into v_eval from public.career_process_due_followups(100);
  if v_eval.waiting_connector <> 1 or v_eval.ready_for_orchestration <> 0 then
    raise exception 'FOLLOWUP_CONNECTOR_GATE_FAILED';
  end if;

  update public.career_engine_control set status='active',champion_version='smoke-only',updated_at=now() where component='mail_delivery';
  select * into v_eval from public.career_process_due_followups(100);
  if v_eval.ready_for_orchestration <> 1 then
    raise exception 'FOLLOWUP_READY_GATE_FAILED';
  end if;

  update public.career_applications
  set status='recruiter_reply',
      external_status_provider='smoke-provider',
      external_status_ref_hash='smoke-status-'||gen_random_uuid()::text,
      external_status_observed_at=now(),
      last_activity_at=now(),
      updated_at=now()
  where id=v_app;

  select * into v_eval from public.career_process_due_followups(100);
  if v_eval.cancelled <> 1 then raise exception 'FOLLOWUP_EXTERNAL_PROGRESS_CANCEL_FAILED'; end if;

  select count(*) into v_mail_after from public.career_mail_actions;
  if v_mail_after <> v_mail_before then raise exception 'FOLLOWUP_CREATED_MAIL_SIDE_EFFECT'; end if;

  if not exists(
    select 1 from public.career_followups
    where id=v_first.followup_id and status='cancelled' and reason_code='APPLICATION_NO_LONGER_WAITING_RESPONSE'
  ) then raise exception 'FOLLOWUP_FINAL_STATE_FAILED'; end if;

  begin
    insert into public.career_applications(user_id,status,evidence_safe)
    values(v_user,'considered',jsonb_build_object('smoke',true)) returning id into v_app;
    perform * from public.career_schedule_followup(v_user,v_app,now(),'application_followup');
    raise exception 'FOLLOWUP_UNAPPLIED_APPLICATION_WAS_ACCEPTED';
  exception when others then
    if sqlerrm='FOLLOWUP_UNAPPLIED_APPLICATION_WAS_ACCEPTED' then raise; end if;
  end;

  raise notice 'FOLLOWUP_SCHEDULER_V1_SMOKE=PASS';
end $$;

rollback;
