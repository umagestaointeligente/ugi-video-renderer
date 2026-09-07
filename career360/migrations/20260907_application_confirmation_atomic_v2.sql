create or replace function public.career_set_application_submission_confirmation(
  p_user_id uuid,
  p_application_id uuid,
  p_confirmed boolean
)
returns table(
  application_id uuid,
  application_status text,
  submission_confirmed boolean,
  global_submit_permission boolean,
  dispatch_eligible boolean
)
language plpgsql
security definer
set search_path = pg_catalog, public
as $$
declare
  v_app public.career_applications%rowtype;
  v_allow_submit boolean := false;
  v_next_status text;
  v_now timestamptz := now();
begin
  if p_user_id is null or p_application_id is null or p_confirmed is null then
    raise exception 'APPLICATION_CONFIRMATION_REQUIRED_FIELDS_MISSING';
  end if;

  select * into v_app
  from public.career_applications
  where id=p_application_id and user_id=p_user_id
  for update;

  if not found then raise exception 'APPLICATION_NOT_FOUND'; end if;

  if v_app.applied_at is not null
     or v_app.external_application_ref_hash is not null
     or v_app.status='applied'
     or v_app.submission_dispatch_state='receipt_confirmed' then
    raise exception 'APPLICATION_ALREADY_SUBMITTED';
  end if;

  if v_app.submission_dispatch_state in ('claimed','uncertain','blocked')
     or coalesce(v_app.submission_attempt_count,0) > 0 then
    raise exception 'APPLICATION_SUBMISSION_ATTEMPT_ALREADY_STARTED';
  end if;

  if v_app.status not in ('draft_ready','awaiting_user') then
    raise exception 'APPLICATION_STATE_NOT_CONFIRMABLE';
  end if;

  select coalesce(cap.allow_application_submit,false)
    into v_allow_submit
  from public.career_action_permissions cap
  where cap.user_id=p_user_id;
  v_allow_submit := coalesce(v_allow_submit,false);

  v_next_status := case when p_confirmed then 'awaiting_user' else 'draft_ready' end;

  update public.career_applications
  set submission_confirmed_at=case when p_confirmed then v_now else null end,
      status=v_next_status,
      updated_at=v_now
  where id=p_application_id and user_id=p_user_id;

  insert into public.career_audit_events(
    user_id,event_type,entity_type,entity_id,outcome,reason_code,metadata_safe
  ) values (
    p_user_id,
    case when p_confirmed then 'application_submission_confirmed' else 'application_submission_confirmation_revoked' end,
    'career_applications',
    p_application_id,
    case when p_confirmed then 'confirmed' else 'revoked' end,
    case when p_confirmed then 'EXPLICIT_PER_APPLICATION_CONFIRMATION' else 'EXPLICIT_CONFIRMATION_REVOKED' end,
    jsonb_build_object(
      'source','career-application-confirm',
      'dispatch_state','idle',
      'global_submit_permission',v_allow_submit,
      'provider_side_effect',false
    )
  );

  return query select p_application_id,v_next_status,p_confirmed,v_allow_submit,(p_confirmed and v_allow_submit);
end;
$$;

revoke all on function public.career_set_application_submission_confirmation(uuid,uuid,boolean) from public, anon, authenticated;
grant execute on function public.career_set_application_submission_confirmation(uuid,uuid,boolean) to service_role;

update public.career_engine_control
set notes_safe=coalesce(notes_safe,'{}'::jsonb) || jsonb_build_object(
  'per_application_confirmation_contract','career-application-confirm JWT -> career_set_application_submission_confirmation service-only',
  'confirmation_write_atomic',true,
  'confirmation_provider_side_effect',false
), updated_at=now()
where component='application_submission_receipt';
