-- Career 360 — Mail Delivery Dispatch Lease V1
-- Exactly-one-intent / no-blind-retry transport contract for external Gmail/Outlook bridges.
-- Raw recipient is encrypted at rest with a database-only Vault key; provider ids remain hash-only.

alter table public.career_mail_actions
  add column if not exists recipient_email_ciphertext bytea,
  add column if not exists recipient_email_hash text,
  add column if not exists delivery_claim_token_hash text,
  add column if not exists delivery_claimed_at timestamptz,
  add column if not exists delivery_claim_expires_at timestamptz,
  add column if not exists delivery_attempt_count integer not null default 0,
  add column if not exists delivery_last_error_safe text,
  add column if not exists delivery_route text;

alter table public.career_mail_actions
  drop constraint if exists career_mail_actions_status_check;
alter table public.career_mail_actions
  add constraint career_mail_actions_status_check
  check (status = any(array[
    'detected'::text,'draft_ready'::text,'awaiting_approval'::text,'approved'::text,
    'dispatching'::text,'delivery_uncertain'::text,'sent'::text,'copied'::text,
    'dismissed'::text,'failed'::text
  ]));

alter table public.career_mail_actions
  add constraint career_mail_actions_dispatching_requires_claim
  check (
    status <> 'dispatching'
    or (
      direction='outbound'
      and recipient_email_ciphertext is not null
      and recipient_email_hash is not null
      and delivery_claim_token_hash is not null
      and delivery_claimed_at is not null
      and delivery_claim_expires_at is not null
      and delivery_attempt_count > 0
    )
  ) not valid;
alter table public.career_mail_actions validate constraint career_mail_actions_dispatching_requires_claim;

create index if not exists idx_career_mail_actions_dispatch_state
  on public.career_mail_actions(status,delivery_claim_expires_at)
  where status in ('approved','dispatching','delivery_uncertain');

comment on column public.career_mail_actions.recipient_email_ciphertext is
  'Recipient mailbox encrypted with pgcrypto using a database-only Vault key. Never expose directly to client roles.';
comment on column public.career_mail_actions.recipient_email_hash is
  'SHA-256 of normalized recipient email for audit/dedupe without exposing the raw mailbox.';
comment on column public.career_mail_actions.delivery_claim_token_hash is
  'Hash of a transient dispatch claim token. Raw token is returned only to the service bridge and is never persisted.';
comment on column public.career_mail_actions.delivery_claim_expires_at is
  'Lease expiry. Expiry never means safe-to-resend: an expired dispatch moves to delivery_uncertain and requires reconciliation.';

-- Defense in depth: client roles do not need encrypted routing material.
revoke select(recipient_email_ciphertext,delivery_claim_token_hash) on public.career_mail_actions from anon, authenticated;

-- Database-only symmetric key for recipient routing data.
do $$
begin
  if not exists (select 1 from vault.decrypted_secrets where name='career_mail_delivery_crypto') then
    perform vault.create_secret(
      encode(extensions.gen_random_bytes(32),'hex'),
      'career_mail_delivery_crypto',
      'Career 360 mail recipient encryption key'
    );
  end if;
end $$;

create or replace function public.career_set_mail_recipient(
  p_user_id uuid,
  p_mail_action_id uuid,
  p_recipient_email text
)
returns table(mail_action_id uuid, recipient_hash text)
language plpgsql
security definer
set search_path = pg_catalog, public, extensions, vault
as $$
declare
  v_email text := lower(btrim(coalesce(p_recipient_email,'')));
  v_key text;
  v_hash text;
  v_status text;
begin
  if p_user_id is null or p_mail_action_id is null then raise exception 'MAIL_ACTION_ID_REQUIRED'; end if;
  if length(v_email) > 320 or v_email !~ '^[^[:space:]@]+@[^[:space:]@]+[.][^[:space:]@]+$' then
    raise exception 'INVALID_RECIPIENT_EMAIL';
  end if;

  select decrypted_secret into v_key from vault.decrypted_secrets where name='career_mail_delivery_crypto' limit 1;
  if nullif(v_key,'') is null then raise exception 'MAIL_CRYPTO_KEY_NOT_AVAILABLE'; end if;

  select status into v_status from public.career_mail_actions
  where id=p_mail_action_id and user_id=p_user_id for update;
  if not found then raise exception 'MAIL_ACTION_NOT_FOUND'; end if;
  if v_status in ('dispatching','delivery_uncertain','sent','dismissed') then
    raise exception 'MAIL_RECIPIENT_LOCKED_FOR_STATUS_%',v_status;
  end if;

  v_hash := encode(extensions.digest(convert_to(v_email,'UTF8'),'sha256'),'hex');
  update public.career_mail_actions
  set recipient_email_ciphertext=extensions.pgp_sym_encrypt(v_email,v_key,'cipher-algo=aes256'),
      recipient_email_hash=v_hash,
      updated_at=now()
  where id=p_mail_action_id and user_id=p_user_id;

  return query select p_mail_action_id,v_hash;
end;
$$;

create or replace function public.career_claim_mail_delivery(
  p_user_id uuid,
  p_mail_action_id uuid,
  p_lease_seconds integer default 900
)
returns table(
  mail_action_id uuid,
  claim_token text,
  recipient_email text,
  subject text,
  body text,
  message_kind text,
  application_id uuid,
  lease_expires_at timestamptz
)
language plpgsql
security definer
set search_path = pg_catalog, public, extensions, vault
as $$
declare
  v_row public.career_mail_actions%rowtype;
  v_bridge_status text;
  v_delivery_status text;
  v_key text;
  v_token text;
  v_token_hash text;
  v_exp timestamptz;
  v_user_approved boolean;
  v_lease integer := greatest(120,least(coalesce(p_lease_seconds,900),3600));
begin
  if p_user_id is null or p_mail_action_id is null then raise exception 'MAIL_ACTION_ID_REQUIRED'; end if;

  select status into v_bridge_status from public.career_engine_control where component='mail_background_bridge';
  select status into v_delivery_status from public.career_engine_control where component='mail_delivery';
  if coalesce(v_bridge_status,'paused') <> 'active' then raise exception 'MAIL_BACKGROUND_BRIDGE_NOT_ACTIVE'; end if;
  if coalesce(v_delivery_status,'paused') <> 'active' then raise exception 'MAIL_DELIVERY_CONTROL_NOT_ACTIVE'; end if;

  select * into v_row from public.career_mail_actions
  where id=p_mail_action_id and user_id=p_user_id for update;
  if not found then raise exception 'MAIL_ACTION_NOT_FOUND'; end if;

  if v_row.status='sent' then raise exception 'MAIL_ACTION_ALREADY_SENT'; end if;
  if v_row.status='delivery_uncertain' then raise exception 'MAIL_DELIVERY_RECONCILIATION_REQUIRED'; end if;
  if v_row.status='dispatching' then
    if v_row.delivery_claim_expires_at is null or v_row.delivery_claim_expires_at > now() then
      raise exception 'MAIL_DELIVERY_ALREADY_CLAIMED';
    end if;
    update public.career_mail_actions set
      status='delivery_uncertain',
      delivery_last_error_safe='Dispatch lease expired before a provider receipt was recorded. Reconcile provider mailbox before any retry.',
      updated_at=now()
    where id=v_row.id;
    raise exception 'MAIL_DELIVERY_RECONCILIATION_REQUIRED';
  end if;
  if v_row.status <> 'approved' then raise exception 'MAIL_ACTION_NOT_APPROVED'; end if;

  select exists(
    select 1 from public.career_activity_ledger l
    where l.user_id=p_user_id
      and l.entity_type='career_mail_actions'
      and l.entity_id=p_mail_action_id
      and l.event_type='mail_approved'
      and l.actor='user'
  ) into v_user_approved;
  if not v_user_approved then raise exception 'EXPLICIT_USER_MAIL_APPROVAL_NOT_PROVEN'; end if;

  if v_row.recipient_email_ciphertext is null or nullif(v_row.recipient_email_hash,'') is null then
    raise exception 'MAIL_RECIPIENT_NOT_CONFIGURED';
  end if;
  if nullif(btrim(coalesce(v_row.proposed_reply,'')),'') is null then raise exception 'MAIL_BODY_NOT_READY'; end if;

  select decrypted_secret into v_key from vault.decrypted_secrets where name='career_mail_delivery_crypto' limit 1;
  if nullif(v_key,'') is null then raise exception 'MAIL_CRYPTO_KEY_NOT_AVAILABLE'; end if;

  v_token := encode(extensions.gen_random_bytes(32),'hex');
  v_token_hash := encode(extensions.digest(convert_to(v_token,'UTF8'),'sha256'),'hex');
  v_exp := now() + make_interval(secs => v_lease);

  update public.career_mail_actions set
    status='dispatching',
    direction='outbound',
    delivery_claim_token_hash=v_token_hash,
    delivery_claimed_at=now(),
    delivery_claim_expires_at=v_exp,
    delivery_attempt_count=delivery_attempt_count+1,
    delivery_last_error_safe=null,
    delivery_route='make-gmail-supabase-v1',
    updated_at=now()
  where id=v_row.id;

  insert into public.career_activity_ledger(
    user_id,event_type,stage,actor,entity_type,entity_id,title,summary_safe,importance,metadata_safe
  ) values(
    p_user_id,'mail_dispatch_claimed','mail_delivery','career_agent','career_mail_actions',p_mail_action_id,
    'Envio em processamento','O transporte recebeu uma autorização temporária de envio. O status só vira enviado após receipt do provedor.',
    'normal',jsonb_build_object('route','make-gmail-supabase-v1','lease_seconds',v_lease,'attempt',v_row.delivery_attempt_count+1)
  );

  return query select
    p_mail_action_id,
    v_token,
    extensions.pgp_sym_decrypt(v_row.recipient_email_ciphertext,v_key),
    coalesce(v_row.subject_safe,''),
    v_row.proposed_reply,
    v_row.message_kind,
    v_row.application_id,
    v_exp;
end;
$$;

create or replace function public.career_record_mail_delivery_receipt_v2(
  p_user_id uuid,
  p_mail_action_id uuid,
  p_claim_token text,
  p_provider text,
  p_message_ref text,
  p_thread_ref text,
  p_sent_at timestamptz
)
returns table(mail_action_id uuid,new_status text,idempotent boolean)
language plpgsql
security definer
set search_path = pg_catalog, public, extensions
as $$
declare
  v_row public.career_mail_actions%rowtype;
  v_provider text := lower(btrim(coalesce(p_provider,'')));
  v_message_ref text := btrim(coalesce(p_message_ref,''));
  v_thread_ref text := btrim(coalesce(p_thread_ref,''));
  v_claim_hash text;
  v_message_hash text;
  v_thread_hash text;
begin
  if p_user_id is null or p_mail_action_id is null then raise exception 'MAIL_ACTION_ID_REQUIRED'; end if;
  if nullif(btrim(coalesce(p_claim_token,'')),'') is null then raise exception 'DELIVERY_CLAIM_TOKEN_REQUIRED'; end if;
  if v_provider='' or v_message_ref='' or v_thread_ref='' or p_sent_at is null then raise exception 'DELIVERY_RECEIPT_INCOMPLETE'; end if;

  v_claim_hash := encode(extensions.digest(convert_to(p_claim_token,'UTF8'),'sha256'),'hex');
  v_message_hash := encode(extensions.digest(convert_to(v_provider || ':' || v_message_ref,'UTF8'),'sha256'),'hex');
  v_thread_hash := encode(extensions.digest(convert_to(v_provider || ':' || v_thread_ref,'UTF8'),'sha256'),'hex');

  select * into v_row from public.career_mail_actions
  where id=p_mail_action_id and user_id=p_user_id for update;
  if not found then raise exception 'MAIL_ACTION_NOT_FOUND'; end if;

  if v_row.status='sent' then
    if v_row.mail_provider=v_provider and v_row.delivery_receipt_hash=v_message_hash and v_row.external_thread_ref_hash=v_thread_hash then
      return query select v_row.id,v_row.status,true; return;
    end if;
    raise exception 'MAIL_ACTION_ALREADY_SENT_WITH_DIFFERENT_RECEIPT';
  end if;

  if v_row.status not in ('dispatching','delivery_uncertain') then raise exception 'MAIL_ACTION_NOT_IN_DELIVERY_STATE'; end if;
  if v_row.delivery_claim_token_hash is distinct from v_claim_hash then raise exception 'DELIVERY_CLAIM_TOKEN_MISMATCH'; end if;

  update public.career_mail_actions set
    mail_provider=v_provider,
    direction='outbound',
    sent_at=p_sent_at,
    external_thread_ref_hash=v_thread_hash,
    delivery_receipt_hash=v_message_hash,
    status='sent',
    delivery_claim_token_hash=null,
    delivery_claim_expires_at=null,
    delivery_last_error_safe=null,
    updated_at=now()
  where id=p_mail_action_id and user_id=p_user_id;

  insert into public.career_activity_ledger(
    user_id,event_type,stage,actor,entity_type,entity_id,title,summary_safe,importance,metadata_safe
  ) values(
    p_user_id,'mail_sent_receipt_recorded','mail_delivery','career_agent','career_mail_actions',p_mail_action_id,
    'E-mail enviado','O provedor confirmou o envio e o Career registrou o receipt externo.','normal',
    jsonb_build_object('provider',v_provider,'route',coalesce(v_row.delivery_route,'unknown'))
  );

  return query select p_mail_action_id,'sent'::text,false;
end;
$$;

create or replace function public.career_mark_mail_delivery_uncertain(
  p_user_id uuid,
  p_mail_action_id uuid,
  p_claim_token text,
  p_error_safe text
)
returns table(mail_action_id uuid,new_status text)
language plpgsql
security definer
set search_path = pg_catalog, public, extensions
as $$
declare
  v_row public.career_mail_actions%rowtype;
  v_claim_hash text;
  v_err text := left(regexp_replace(coalesce(p_error_safe,'transport result unknown'),'[\r\n\t]+',' ','g'),500);
begin
  v_claim_hash := encode(extensions.digest(convert_to(coalesce(p_claim_token,''),'UTF8'),'sha256'),'hex');
  select * into v_row from public.career_mail_actions where id=p_mail_action_id and user_id=p_user_id for update;
  if not found then raise exception 'MAIL_ACTION_NOT_FOUND'; end if;
  if v_row.status='sent' then return query select v_row.id,'sent'::text; return; end if;
  if v_row.status <> 'dispatching' then raise exception 'MAIL_ACTION_NOT_DISPATCHING'; end if;
  if v_row.delivery_claim_token_hash is distinct from v_claim_hash then raise exception 'DELIVERY_CLAIM_TOKEN_MISMATCH'; end if;

  update public.career_mail_actions set
    status='delivery_uncertain',
    delivery_last_error_safe=v_err,
    updated_at=now()
  where id=p_mail_action_id and user_id=p_user_id;

  insert into public.career_activity_ledger(
    user_id,event_type,stage,actor,entity_type,entity_id,title,summary_safe,importance,metadata_safe
  ) values(
    p_user_id,'mail_delivery_uncertain','mail_delivery','career_agent','career_mail_actions',p_mail_action_id,
    'Envio requer reconciliação','O transporte não conseguiu provar se o provedor enviou a mensagem. Nenhum retry automático será feito.','high',
    jsonb_build_object('route',coalesce(v_row.delivery_route,'unknown'))
  );

  return query select p_mail_action_id,'delivery_uncertain'::text;
end;
$$;

revoke all on function public.career_set_mail_recipient(uuid,uuid,text) from public,anon,authenticated;
revoke all on function public.career_claim_mail_delivery(uuid,uuid,integer) from public,anon,authenticated;
revoke all on function public.career_record_mail_delivery_receipt_v2(uuid,uuid,text,text,text,text,timestamptz) from public,anon,authenticated;
revoke all on function public.career_mark_mail_delivery_uncertain(uuid,uuid,text,text) from public,anon,authenticated;
grant execute on function public.career_set_mail_recipient(uuid,uuid,text) to service_role;
grant execute on function public.career_claim_mail_delivery(uuid,uuid,integer) to service_role;
grant execute on function public.career_record_mail_delivery_receipt_v2(uuid,uuid,text,text,text,text,timestamptz) to service_role;
grant execute on function public.career_mark_mail_delivery_uncertain(uuid,uuid,text,text) to service_role;

comment on function public.career_claim_mail_delivery(uuid,uuid,integer) is
  'Service-only fail-closed mail dispatch claim. Requires live bridge + mail_delivery control + explicit user approval. Expired claims become delivery_uncertain and are never blindly retried.';
comment on function public.career_record_mail_delivery_receipt_v2(uuid,uuid,text,text,text,text,timestamptz) is
  'Service-only delivery completion. A mail action becomes sent only from a valid dispatch claim plus provider receipt.';
