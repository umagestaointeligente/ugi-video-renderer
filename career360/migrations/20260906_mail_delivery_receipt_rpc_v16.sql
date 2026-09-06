-- Career 360 V16 — service-only mail delivery receipt primitive
-- Raw provider identifiers are accepted transiently and stored only as SHA-256 hashes.

alter table public.career_mail_actions
  add column if not exists mail_provider text;

alter table public.career_mail_actions
  drop constraint if exists career_mail_actions_sent_requires_delivery_evidence;

alter table public.career_mail_actions
  add constraint career_mail_actions_sent_requires_delivery_evidence
  check (
    status <> 'sent'
    or (
      direction = 'outbound'
      and sent_at is not null
      and mail_provider is not null
      and length(btrim(mail_provider)) > 0
      and external_thread_ref_hash is not null
      and length(btrim(external_thread_ref_hash)) > 0
      and delivery_receipt_hash is not null
      and length(btrim(delivery_receipt_hash)) > 0
    )
  );

alter table public.career_mail_actions
  drop constraint if exists career_mail_actions_inbound_requires_external_message_evidence;

alter table public.career_mail_actions
  add constraint career_mail_actions_inbound_requires_external_message_evidence
  check (
    direction <> 'inbound'
    or (
      received_at is not null
      and mail_provider is not null
      and length(btrim(mail_provider)) > 0
      and external_thread_ref_hash is not null
      and length(btrim(external_thread_ref_hash)) > 0
      and external_message_ref_hash is not null
      and length(btrim(external_message_ref_hash)) > 0
    )
  );

comment on column public.career_mail_actions.mail_provider is
  'Normalized provider key (for example gmail/outlook) attached only when backed by an external provider event.';

create or replace function public.career_record_mail_delivery_receipt(
  p_user_id uuid,
  p_mail_action_id uuid,
  p_provider text,
  p_message_ref text,
  p_thread_ref text,
  p_sent_at timestamptz
)
returns table(mail_action_id uuid, new_status text, idempotent boolean)
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  v_provider text := lower(btrim(coalesce(p_provider,'')));
  v_message_ref text := btrim(coalesce(p_message_ref,''));
  v_thread_ref text := btrim(coalesce(p_thread_ref,''));
  v_message_hash text;
  v_thread_hash text;
  v_row public.career_mail_actions%rowtype;
begin
  if p_user_id is null or p_mail_action_id is null then
    raise exception 'RECEIPT_ID_REQUIRED';
  end if;
  if v_provider = '' or v_message_ref = '' or v_thread_ref = '' or p_sent_at is null then
    raise exception 'DELIVERY_RECEIPT_INCOMPLETE';
  end if;

  v_message_hash := encode(extensions.digest(convert_to(v_provider || ':' || v_message_ref, 'UTF8'), 'sha256'), 'hex');
  v_thread_hash := encode(extensions.digest(convert_to(v_provider || ':' || v_thread_ref, 'UTF8'), 'sha256'), 'hex');

  select * into v_row
  from public.career_mail_actions
  where id = p_mail_action_id and user_id = p_user_id
  for update;

  if not found then
    raise exception 'MAIL_ACTION_NOT_FOUND';
  end if;

  if v_row.status = 'sent' then
    if v_row.mail_provider = v_provider
       and v_row.delivery_receipt_hash = v_message_hash
       and v_row.external_thread_ref_hash = v_thread_hash then
      return query select v_row.id, v_row.status, true;
      return;
    end if;
    raise exception 'MAIL_ACTION_ALREADY_SENT_WITH_DIFFERENT_RECEIPT';
  end if;

  if v_row.status <> 'approved' then
    raise exception 'MAIL_ACTION_NOT_APPROVED';
  end if;

  update public.career_mail_actions
  set mail_provider = v_provider,
      direction = 'outbound',
      sent_at = p_sent_at,
      external_thread_ref_hash = v_thread_hash,
      delivery_receipt_hash = v_message_hash,
      status = 'sent',
      updated_at = now()
  where id = p_mail_action_id and user_id = p_user_id;

  return query select p_mail_action_id, 'sent'::text, false;
end;
$$;

revoke all on function public.career_record_mail_delivery_receipt(uuid,uuid,text,text,text,timestamptz) from public;
revoke all on function public.career_record_mail_delivery_receipt(uuid,uuid,text,text,text,timestamptz) from anon;
revoke all on function public.career_record_mail_delivery_receipt(uuid,uuid,text,text,text,timestamptz) from authenticated;
grant execute on function public.career_record_mail_delivery_receipt(uuid,uuid,text,text,text,timestamptz) to service_role;

comment on function public.career_record_mail_delivery_receipt(uuid,uuid,text,text,text,timestamptz) is
  'Service-only idempotent receipt recorder. approved becomes sent only after provider message/thread identifiers and sent timestamp are supplied; raw provider identifiers are not persisted.';
