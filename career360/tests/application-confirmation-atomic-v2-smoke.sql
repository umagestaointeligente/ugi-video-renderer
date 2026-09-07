begin;

do $$
declare
  v_user uuid;
  v_app uuid := gen_random_uuid();
  v_result record;
  v_rejected boolean := false;
begin
  select user_id into v_user
  from public.career_action_permissions
  order by updated_at desc
  limit 1;
  if v_user is null then raise exception 'SMOKE_NO_USER'; end if;

  insert into public.career_applications(id,user_id,status,application_url,evidence_safe)
  values(v_app,v_user,'draft_ready','https://jobs.quickin.io/smoke/jobs/confirm-atomic-v2','{}'::jsonb);

  select * into v_result
  from public.career_set_application_submission_confirmation(v_user,v_app,true)
  limit 1;
  if v_result.application_status <> 'awaiting_user' or not v_result.submission_confirmed then
    raise exception 'SMOKE_CONFIRM_FAILED';
  end if;
  if v_result.global_submit_permission or v_result.dispatch_eligible then
    raise exception 'SMOKE_PERMISSION_FALSE_NOT_PRESERVED';
  end if;
  if (select submission_confirmed_at is null from public.career_applications where id=v_app) then
    raise exception 'SMOKE_CONFIRM_TIMESTAMP_MISSING';
  end if;

  select * into v_result
  from public.career_set_application_submission_confirmation(v_user,v_app,false)
  limit 1;
  if v_result.application_status <> 'draft_ready' or v_result.submission_confirmed then
    raise exception 'SMOKE_REVOKE_FAILED';
  end if;
  if (select submission_confirmed_at is not null from public.career_applications where id=v_app) then
    raise exception 'SMOKE_REVOKE_TIMESTAMP_NOT_CLEARED';
  end if;

  update public.career_applications
  set submission_dispatch_state='claimed', submission_attempt_count=1
  where id=v_app;

  begin
    perform * from public.career_set_application_submission_confirmation(v_user,v_app,true);
  exception when others then
    if position('APPLICATION_SUBMISSION_ATTEMPT_ALREADY_STARTED' in sqlerrm)>0 then
      v_rejected := true;
    else
      raise;
    end if;
  end;
  if not v_rejected then
    raise exception 'SMOKE_CONFIRM_AFTER_CLAIM_NOT_REJECTED';
  end if;

  if (
    select count(*)
    from public.career_audit_events
    where user_id=v_user
      and entity_id=v_app
      and event_type in ('application_submission_confirmed','application_submission_confirmation_revoked')
  ) <> 2 then
    raise exception 'SMOKE_AUDIT_COUNT_FAILED';
  end if;
end $$;

rollback;
