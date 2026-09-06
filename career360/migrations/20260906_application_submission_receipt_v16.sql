-- Career 360 — Application Submission Receipt V16
-- Service-only, receipt-backed transition to applied. No connector side effects.

create or replace function public.career_record_application_submission_receipt(
  p_user_id uuid,
  p_application_id uuid,
  p_provider text,
  p_external_application_ref text,
  p_applied_at timestamptz,
  p_followup_due_at timestamptz default null
)
returns table(
  application_id uuid,
  new_status text,
  idempotent boolean,
  followup_id uuid
)
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  v_provider text := lower(btrim(coalesce(p_provider,'')));
  v_external_ref text := btrim(coalesce(p_external_application_ref,''));
  v_receipt_hash text;
  v_app public.career_applications%rowtype;
  v_target_status text;
  v_idempotent boolean := false;
  v_followup_id uuid := null;
begin
  if p_user_id is null or p_application_id is null or p_applied_at is null then
    raise exception 'APPLICATION_SUBMISSION_REQUIRED_FIELDS_MISSING';
  end if;
  if v_provider = '' then
    raise exception 'APPLICATION_SUBMISSION_PROVIDER_REQUIRED';
  end if;
  if v_external_ref = '' then
    raise exception 'APPLICATION_SUBMISSION_EXTERNAL_REF_REQUIRED';
  end if;
  if p_applied_at > now() + interval '1 day' then
    raise exception 'APPLICATION_SUBMISSION_TIME_INVALID';
  end if;

  v_receipt_hash := encode(digest(v_provider || E'\n' || v_external_ref, 'sha256'), 'hex');

  select * into v_app
  from public.career_applications
  where id = p_application_id
    and user_id = p_user_id
  for update;

  if not found then
    raise exception 'APPLICATION_NOT_FOUND';
  end if;

  if v_app.external_application_ref_hash is not null
     and v_app.external_application_ref_hash <> v_receipt_hash then
    raise exception 'APPLICATION_SUBMISSION_RECEIPT_CONFLICT';
  end if;

  if exists (
    select 1
    from public.career_applications ca
    where ca.user_id = p_user_id
      and ca.id <> p_application_id
      and ca.external_application_ref_hash = v_receipt_hash
  ) then
    raise exception 'APPLICATION_SUBMISSION_RECEIPT_ALREADY_USED';
  end if;

  v_idempotent := (
    v_app.external_application_ref_hash = v_receipt_hash
    and v_app.applied_at is not null
  );

  v_target_status := case
    when v_app.status in ('considered','draft_ready','awaiting_user') then 'applied'
    else v_app.status
  end;

  update public.career_applications
  set external_application_ref_hash = v_receipt_hash,
      applied_at = coalesce(applied_at, p_applied_at),
      status = v_target_status,
      evidence_safe = coalesce(evidence_safe,'{}'::jsonb) || jsonb_build_object(
        'submission_provider', v_provider,
        'submission_receipt_recorded_at', now()
      ),
      last_activity_at = greatest(coalesce(last_activity_at,p_applied_at),p_applied_at),
      updated_at = now()
  where id = p_application_id;

  if not v_idempotent then
    insert into public.career_activity_ledger(
      user_id,event_type,stage,actor,entity_type,entity_id,title,summary_safe,importance,metadata_safe,occurred_at
    ) values (
      p_user_id,
      'application_submission_receipt_recorded',
      'application',
      'system',
      'career_applications',
      p_application_id,
      'Candidatura confirmada por comprovante externo',
      'O estado da candidatura foi atualizado somente após um comprovante externo verificável. A referência externa bruta não foi armazenada.',
      'normal',
      jsonb_build_object('provider',v_provider,'status_after',v_target_status),
      now()
    );
  end if;

  if p_followup_due_at is not null then
    if p_followup_due_at < coalesce(v_app.applied_at,p_applied_at) then
      raise exception 'FOLLOWUP_DUE_BEFORE_APPLICATION';
    end if;
    if v_target_status = 'applied' then
      select s.followup_id into v_followup_id
      from public.career_schedule_followup(
        p_user_id,
        p_application_id,
        p_followup_due_at,
        'application_followup'
      ) s
      limit 1;
    end if;
  end if;

  return query select p_application_id, v_target_status, v_idempotent, v_followup_id;
end;
$$;

revoke all on function public.career_record_application_submission_receipt(uuid,uuid,text,text,timestamptz,timestamptz)
  from public, anon, authenticated;
grant execute on function public.career_record_application_submission_receipt(uuid,uuid,text,text,timestamptz,timestamptz)
  to service_role;

comment on function public.career_record_application_submission_receipt(uuid,uuid,text,text,timestamptz,timestamptz) is
  'Service-only application submission receipt recorder. Hashes provider-qualified external reference, never stores the raw reference, never submits an application, and schedules follow-up only when an explicit due_at is supplied.';

insert into public.career_engine_control(component,champion_version,rollback_version,status,notes_safe)
values(
  'application_submission_receipt',
  'v1.0',
  null,
  'active',
  jsonb_build_object(
    'receipt_required_before_applied',true,
    'raw_external_ref_persisted',false,
    'followup_due_at_explicit_only',true,
    'submission_side_effects',false
  )
)
on conflict (component) do update
set champion_version=excluded.champion_version,
    status=excluded.status,
    notes_safe=excluded.notes_safe,
    updated_at=now();
