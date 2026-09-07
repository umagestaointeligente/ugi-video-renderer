alter table public.career_applications
  add column if not exists submission_confirmed_at timestamptz,
  add column if not exists submission_dispatch_state text not null default 'idle',
  add column if not exists submission_claim_token_hash text,
  add column if not exists submission_claimed_at timestamptz,
  add column if not exists submission_claim_expires_at timestamptz,
  add column if not exists submission_attempt_count integer not null default 0,
  add column if not exists submission_last_error_safe text,
  add column if not exists submission_route text;

do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conrelid='public.career_applications'::regclass
      and conname='career_applications_submission_dispatch_state_check'
  ) then
    alter table public.career_applications
      add constraint career_applications_submission_dispatch_state_check
      check (submission_dispatch_state in ('idle','claimed','uncertain','blocked','receipt_confirmed'));
  end if;
  if not exists (
    select 1 from pg_constraint
    where conrelid='public.career_applications'::regclass
      and conname='career_applications_submission_attempt_count_check'
  ) then
    alter table public.career_applications
      add constraint career_applications_submission_attempt_count_check
      check (submission_attempt_count >= 0);
  end if;
end $$;

create index if not exists career_applications_submission_dispatch_idx
  on public.career_applications(status, submission_dispatch_state, submission_attempt_count, submission_confirmed_at)
  where status='awaiting_user';

create or replace function public.career_claim_application_submission(
  p_limit integer default 10,
  p_lease_seconds integer default 600
)
returns table(
  application_id uuid,
  user_id uuid,
  opportunity_id uuid,
  application_url text,
  provider_route text,
  claim_token text,
  claim_expires_at timestamptz
)
language plpgsql
security definer
set search_path = pg_catalog, public, extensions
as $$
declare
  r record;
  v_token text;
  v_limit integer := greatest(1, least(coalesce(p_limit,10),50));
  v_lease_seconds integer := greatest(60, least(coalesce(p_lease_seconds,600),1800));
begin
  for r in
    select ca.id, ca.user_id, ca.opportunity_id, ca.application_url
    from public.career_applications ca
    join public.career_action_permissions cap on cap.user_id=ca.user_id
    where ca.status='awaiting_user'
      and ca.submission_confirmed_at is not null
      and ca.submission_dispatch_state='idle'
      and ca.submission_attempt_count=0
      and ca.applied_at is null
      and ca.external_application_ref_hash is null
      and ca.application_url like 'https://jobs.quickin.io/%'
      and cap.allow_application_submit is true
    order by ca.submission_confirmed_at asc, ca.created_at asc
    for update of ca skip locked
    limit v_limit
  loop
    v_token := gen_random_uuid()::text;
    update public.career_applications ca
    set submission_dispatch_state='claimed',
        submission_claim_token_hash=encode(digest(v_token,'sha256'),'hex'),
        submission_claimed_at=now(),
        submission_claim_expires_at=now()+make_interval(secs=>v_lease_seconds),
        submission_attempt_count=ca.submission_attempt_count+1,
        submission_last_error_safe=null,
        submission_route='quickin-make-v2',
        updated_at=now()
    where ca.id=r.id;

    application_id := r.id;
    user_id := r.user_id;
    opportunity_id := r.opportunity_id;
    application_url := r.application_url;
    provider_route := 'quickin-make-v2';
    claim_token := v_token;
    claim_expires_at := now()+make_interval(secs=>v_lease_seconds);
    return next;
  end loop;
end;
$$;

revoke all on function public.career_claim_application_submission(integer,integer) from public, anon, authenticated;
grant execute on function public.career_claim_application_submission(integer,integer) to service_role;

create or replace function public.career_mark_application_submission_uncertain(
  p_application_id uuid,
  p_claim_token text,
  p_error_safe text default null
)
returns boolean
language plpgsql
security definer
set search_path = pg_catalog, public, extensions
as $$
declare
  v_hash text := encode(digest(btrim(coalesce(p_claim_token,'')),'sha256'),'hex');
  v_rows integer;
begin
  if p_application_id is null or btrim(coalesce(p_claim_token,''))='' then
    raise exception 'APPLICATION_SUBMISSION_CLAIM_REQUIRED';
  end if;
  update public.career_applications
  set submission_dispatch_state='uncertain',
      submission_last_error_safe=left(nullif(btrim(coalesce(p_error_safe,'')),''),500),
      submission_claim_expires_at=null,
      updated_at=now()
  where id=p_application_id
    and submission_dispatch_state='claimed'
    and submission_claim_token_hash=v_hash;
  get diagnostics v_rows=row_count;
  return v_rows=1;
end;
$$;

revoke all on function public.career_mark_application_submission_uncertain(uuid,text,text) from public, anon, authenticated;
grant execute on function public.career_mark_application_submission_uncertain(uuid,text,text) to service_role;

create or replace function public.career_record_application_submission_receipt_v2(
  p_user_id uuid,
  p_application_id uuid,
  p_claim_token text,
  p_provider text,
  p_external_application_ref text,
  p_applied_at timestamptz,
  p_followup_due_at timestamptz default null
)
returns table(application_id uuid, new_status text, idempotent boolean, followup_id uuid)
language plpgsql
security definer
set search_path = pg_catalog, public, extensions
as $$
declare
  v_provider text := lower(btrim(coalesce(p_provider,'')));
  v_external_ref text := btrim(coalesce(p_external_application_ref,''));
  v_claim_hash text := encode(digest(btrim(coalesce(p_claim_token,'')),'sha256'),'hex');
  v_receipt_hash text;
  v_app public.career_applications%rowtype;
  v_target_status text;
  v_idempotent boolean := false;
  v_followup_id uuid := null;
begin
  if p_user_id is null or p_application_id is null or p_applied_at is null then
    raise exception 'APPLICATION_SUBMISSION_REQUIRED_FIELDS_MISSING';
  end if;
  if btrim(coalesce(p_claim_token,''))='' then
    raise exception 'APPLICATION_SUBMISSION_CLAIM_REQUIRED';
  end if;
  if v_provider='' then raise exception 'APPLICATION_SUBMISSION_PROVIDER_REQUIRED'; end if;
  if v_external_ref='' then raise exception 'APPLICATION_SUBMISSION_EXTERNAL_REF_REQUIRED'; end if;
  if p_applied_at > now()+interval '1 day' then raise exception 'APPLICATION_SUBMISSION_TIME_INVALID'; end if;

  v_receipt_hash := encode(digest(v_provider || E'\n' || v_external_ref,'sha256'),'hex');

  select * into v_app
  from public.career_applications
  where id=p_application_id and user_id=p_user_id
  for update;
  if not found then raise exception 'APPLICATION_NOT_FOUND'; end if;

  if v_app.submission_dispatch_state='receipt_confirmed'
     and v_app.external_application_ref_hash=v_receipt_hash
     and v_app.applied_at is not null then
    v_idempotent := true;
  else
    if v_app.submission_dispatch_state <> 'claimed' then
      raise exception 'APPLICATION_SUBMISSION_NOT_CLAIMED';
    end if;
    if v_app.submission_claim_token_hash is null or v_app.submission_claim_token_hash <> v_claim_hash then
      raise exception 'APPLICATION_SUBMISSION_CLAIM_MISMATCH';
    end if;
  end if;

  if v_app.external_application_ref_hash is not null
     and v_app.external_application_ref_hash <> v_receipt_hash then
    raise exception 'APPLICATION_SUBMISSION_RECEIPT_CONFLICT';
  end if;
  if exists (
    select 1 from public.career_applications ca
    where ca.user_id=p_user_id
      and ca.id<>p_application_id
      and ca.external_application_ref_hash=v_receipt_hash
  ) then
    raise exception 'APPLICATION_SUBMISSION_RECEIPT_ALREADY_USED';
  end if;

  v_target_status := case when v_app.status in ('considered','draft_ready','awaiting_user') then 'applied' else v_app.status end;

  update public.career_applications
  set external_application_ref_hash=v_receipt_hash,
      applied_at=coalesce(applied_at,p_applied_at),
      status=v_target_status,
      submission_dispatch_state='receipt_confirmed',
      submission_claim_expires_at=null,
      submission_last_error_safe=null,
      evidence_safe=coalesce(evidence_safe,'{}'::jsonb) || jsonb_build_object(
        'submission_provider',v_provider,
        'submission_receipt_recorded_at',now(),
        'submission_claim_verified',true,
        'submission_route',coalesce(v_app.submission_route,'unknown')
      ),
      last_activity_at=greatest(coalesce(last_activity_at,p_applied_at),p_applied_at),
      updated_at=now()
  where id=p_application_id;

  if not v_idempotent then
    insert into public.career_activity_ledger(
      user_id,event_type,stage,actor,entity_type,entity_id,title,summary_safe,importance,metadata_safe,occurred_at
    ) values (
      p_user_id,'application_submission_receipt_recorded','application','system','career_applications',p_application_id,
      'Candidatura confirmada por comprovante externo',
      'O estado da candidatura foi atualizado somente após claim autorizado e comprovante externo verificável.',
      'normal',jsonb_build_object('provider',v_provider,'status_after',v_target_status,'claim_verified',true),now()
    );
  end if;

  if p_followup_due_at is not null then
    if p_followup_due_at < coalesce(v_app.applied_at,p_applied_at) then raise exception 'FOLLOWUP_DUE_BEFORE_APPLICATION'; end if;
    if v_target_status='applied' then
      select s.followup_id into v_followup_id
      from public.career_schedule_followup(p_user_id,p_application_id,p_followup_due_at,'application_followup') s
      limit 1;
    end if;
  end if;

  return query select p_application_id,v_target_status,v_idempotent,v_followup_id;
end;
$$;

revoke all on function public.career_record_application_submission_receipt_v2(uuid,uuid,text,text,text,timestamptz,timestamptz) from public, anon, authenticated;
grant execute on function public.career_record_application_submission_receipt_v2(uuid,uuid,text,text,text,timestamptz,timestamptz) to service_role;

revoke execute on function public.career_record_application_submission_receipt(uuid,uuid,text,text,timestamptz,timestamptz) from service_role;

update public.career_engine_control
set champion_version='v2.0-claim-bound-receipt',
    notes_safe=coalesce(notes_safe,'{}'::jsonb) || jsonb_build_object(
      'receipt_infrastructure_state','LIVE_SERVICE_ONLY_V2',
      'dispatch_contract','career_claim_application_submission -> provider -> career_record_application_submission_receipt_v2',
      'legacy_receipt_v1','RETIRED_SERVICE_EXEC_REVOKED',
      'blind_retry_allowed',false,
      'claim_single_attempt_only',true,
      'provider_connector_state','NOT_LIVE',
      'external_submission_side_effects_live',false
    ),
    updated_at=now()
where component='application_submission_receipt';