-- Career 360 — Mail Delivery Dispatch Lease V1 fix
-- Preserve delivery_uncertain on expired leases and retire the unclaimed V1 receipt route.

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
  if v_row.status='delivery_uncertain' then return; end if;
  if v_row.status='dispatching' then
    if v_row.delivery_claim_expires_at is null or v_row.delivery_claim_expires_at > now() then
      raise exception 'MAIL_DELIVERY_ALREADY_CLAIMED';
    end if;
    update public.career_mail_actions set
      status='delivery_uncertain',
      delivery_last_error_safe='Dispatch lease expired before a provider receipt was recorded. Reconcile provider mailbox before any retry.',
      updated_at=now()
    where id=v_row.id;
    insert into public.career_activity_ledger(
      user_id,event_type,stage,actor,entity_type,entity_id,title,summary_safe,importance,metadata_safe
    ) values(
      p_user_id,'mail_delivery_uncertain','mail_delivery','career_agent','career_mail_actions',p_mail_action_id,
      'Envio requer reconciliação','O lease expirou sem receipt do provedor. Nenhum retry automático será feito.','high',
      jsonb_build_object('route',coalesce(v_row.delivery_route,'unknown'),'reason','LEASE_EXPIRED_WITHOUT_RECEIPT')
    );
    return;
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

-- V1 allowed approved -> sent without a dispatch claim. No live consumer exists; retire it so the transport has one completion route.
revoke execute on function public.career_record_mail_delivery_receipt(uuid,uuid,text,text,text,timestamptz) from service_role;
comment on function public.career_record_mail_delivery_receipt(uuid,uuid,text,text,text,timestamptz) is
  'LEGACY V1 RETIRED. Use career_claim_mail_delivery + career_record_mail_delivery_receipt_v2. Kept only for migration/history compatibility.';
