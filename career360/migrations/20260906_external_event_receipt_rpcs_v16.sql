-- Career 360 V16 — service-only external event receipt primitives
-- Inbound mail and external application milestones are persisted only from provider-backed receipts.

alter table public.career_applications
  add column if not exists external_status_provider text;

alter table public.career_applications
  drop constraint if exists career_applications_external_milestone_requires_receipt;

alter table public.career_applications
  add constraint career_applications_external_milestone_requires_receipt
  check (
    status not in (
      'recruiter_reply',
      'interview_pending',
      'interview_confirmed',
      'finalist',
      'offer',
      'hired',
      'rejected',
      'closed'
    )
    or (
      external_status_provider is not null
      and length(btrim(external_status_provider)) > 0
      and external_status_ref_hash is not null
      and length(btrim(external_status_ref_hash)) > 0
      and external_status_observed_at is not null
    )
  );

comment on column public.career_applications.external_status_provider is
  'Normalized provider/source key attached to a provider-backed external application milestone.';

create or replace function public.career_record_inbound_mail_event(
  p_user_id uuid,
  p_provider text,
  p_message_ref text,
  p_thread_ref text,
  p_received_at timestamptz,
  p_sender_display text default null,
  p_subject_safe text default null,
  p_summary_safe text default null,
  p_message_kind text default 'recruiter',
  p_critical boolean default false,
  p_requires_human boolean default false,
  p_sensitive_category text default null,
  p_application_id uuid default null
)
returns table(mail_action_id uuid, event_status text, idempotent boolean)
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  v_provider text := lower(left(btrim(coalesce(p_provider,'')),40));
  v_message_ref text := btrim(coalesce(p_message_ref,''));
  v_thread_ref text := btrim(coalesce(p_thread_ref,''));
  v_message_hash text;
  v_thread_hash text;
  v_existing public.career_mail_actions%rowtype;
  v_id uuid;
  v_sender text := nullif(left(regexp_replace(coalesce(p_sender_display,''),'[[:cntrl:]]',' ','g'),180),'');
  v_subject text := nullif(left(regexp_replace(coalesce(p_subject_safe,''),'[[:cntrl:]]',' ','g'),240),'');
  v_summary text := nullif(left(regexp_replace(coalesce(p_summary_safe,''),'[[:cntrl:]]',' ','g'),1200),'');
  v_kind text := lower(btrim(coalesce(p_message_kind,'recruiter')));
  v_sensitive text := nullif(left(lower(btrim(coalesce(p_sensitive_category,''))),80),'');
begin
  if p_user_id is null then raise exception 'USER_ID_REQUIRED'; end if;
  if v_provider='' or v_message_ref='' or v_thread_ref='' or p_received_at is null then
    raise exception 'INBOUND_RECEIPT_INCOMPLETE';
  end if;
  if v_kind not in ('recruiter','interview','followup','offer','application','other') then
    raise exception 'INVALID_MESSAGE_KIND';
  end if;
  if p_application_id is not null and not exists (
    select 1 from public.career_applications a where a.id=p_application_id and a.user_id=p_user_id
  ) then
    raise exception 'APPLICATION_NOT_FOUND_FOR_USER';
  end if;

  v_message_hash := encode(extensions.digest(convert_to(v_provider || ':' || v_message_ref,'UTF8'),'sha256'),'hex');
  v_thread_hash := encode(extensions.digest(convert_to(v_provider || ':' || v_thread_ref,'UTF8'),'sha256'),'hex');

  select * into v_existing
  from public.career_mail_actions
  where user_id=p_user_id and external_message_ref_hash=v_message_hash
  limit 1;

  if found then
    if v_existing.direction='inbound'
       and v_existing.mail_provider=v_provider
       and v_existing.external_thread_ref_hash=v_thread_hash then
      return query select v_existing.id, v_existing.status, true;
      return;
    end if;
    raise exception 'INBOUND_MESSAGE_RECEIPT_COLLISION';
  end if;

  insert into public.career_mail_actions(
    user_id,application_id,external_thread_ref_hash,external_message_ref_hash,mail_provider,
    direction,message_kind,sender_display,subject_safe,summary_safe,status,
    critical,requires_human,sensitive_category,received_at
  ) values (
    p_user_id,p_application_id,v_thread_hash,v_message_hash,v_provider,
    'inbound',v_kind,v_sender,v_subject,v_summary,'detected',
    coalesce(p_critical,false),coalesce(p_requires_human,false),v_sensitive,p_received_at
  ) returning id into v_id;

  return query select v_id, 'detected'::text, false;
end;
$$;

revoke all on function public.career_record_inbound_mail_event(uuid,text,text,text,timestamptz,text,text,text,text,boolean,boolean,text,uuid) from public;
revoke all on function public.career_record_inbound_mail_event(uuid,text,text,text,timestamptz,text,text,text,text,boolean,boolean,text,uuid) from anon;
revoke all on function public.career_record_inbound_mail_event(uuid,text,text,text,timestamptz,text,text,text,text,boolean,boolean,text,uuid) from authenticated;
grant execute on function public.career_record_inbound_mail_event(uuid,text,text,text,timestamptz,text,text,text,text,boolean,boolean,text,uuid) to service_role;

comment on function public.career_record_inbound_mail_event(uuid,text,text,text,timestamptz,text,text,text,text,boolean,boolean,text,uuid) is
  'Service-only idempotent inbound mail recorder. Requires provider message/thread identities and received timestamp; persists only hashes of external identifiers.';

create or replace function public.career_record_application_milestone(
  p_user_id uuid,
  p_application_id uuid,
  p_status text,
  p_provider text,
  p_event_ref text,
  p_observed_at timestamptz
)
returns table(application_id uuid, new_status text, idempotent boolean)
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  v_status text := lower(btrim(coalesce(p_status,'')));
  v_provider text := lower(left(btrim(coalesce(p_provider,'')),40));
  v_event_ref text := btrim(coalesce(p_event_ref,''));
  v_event_hash text;
  v_row public.career_applications%rowtype;
begin
  if p_user_id is null or p_application_id is null then raise exception 'APPLICATION_ID_REQUIRED'; end if;
  if v_provider='' or v_event_ref='' or p_observed_at is null then raise exception 'MILESTONE_RECEIPT_INCOMPLETE'; end if;
  if v_status not in ('recruiter_reply','interview_pending','interview_confirmed','finalist','offer','hired','rejected','closed') then
    raise exception 'INVALID_EXTERNAL_APPLICATION_STATUS';
  end if;

  v_event_hash := encode(extensions.digest(convert_to(v_provider || ':' || v_event_ref,'UTF8'),'sha256'),'hex');

  select * into v_row
  from public.career_applications
  where id=p_application_id and user_id=p_user_id
  for update;

  if not found then raise exception 'APPLICATION_NOT_FOUND'; end if;

  if v_row.status=v_status
     and v_row.external_status_provider=v_provider
     and v_row.external_status_ref_hash=v_event_hash then
    return query select v_row.id, v_row.status, true;
    return;
  end if;

  update public.career_applications
  set status=v_status,
      external_status_provider=v_provider,
      external_status_ref_hash=v_event_hash,
      external_status_observed_at=p_observed_at,
      last_activity_at=p_observed_at,
      updated_at=now()
  where id=p_application_id and user_id=p_user_id;

  insert into public.career_audit_events(
    user_id,event_type,entity_type,entity_id,outcome,reason_code,metadata_safe
  ) values (
    p_user_id,'application_external_milestone','career_applications',p_application_id,
    v_status,'EXTERNAL_RECEIPT_VERIFIED',jsonb_build_object('provider',v_provider)
  );

  return query select p_application_id, v_status, false;
end;
$$;

revoke all on function public.career_record_application_milestone(uuid,uuid,text,text,text,timestamptz) from public;
revoke all on function public.career_record_application_milestone(uuid,uuid,text,text,text,timestamptz) from anon;
revoke all on function public.career_record_application_milestone(uuid,uuid,text,text,text,timestamptz) from authenticated;
grant execute on function public.career_record_application_milestone(uuid,uuid,text,text,text,timestamptz) to service_role;

comment on function public.career_record_application_milestone(uuid,uuid,text,text,text,timestamptz) is
  'Service-only idempotent recorder for externally asserted application milestones. Raw provider event identity is hashed server-side before persistence.';
