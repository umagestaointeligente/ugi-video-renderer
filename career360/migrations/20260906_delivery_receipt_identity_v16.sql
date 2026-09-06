-- LSI Career 360 — delivery receipt identity hardening
-- 2026-09-06
-- A thread reference is not a delivery receipt. Successful delivery requires
-- a separate provider-derived receipt hash, and receipt identities cannot be reused.

alter table public.career_mail_actions
  add column delivery_receipt_hash text;

alter table public.career_mail_actions
  drop constraint career_mail_actions_sent_requires_delivery_evidence;

alter table public.career_mail_actions
  add constraint career_mail_actions_sent_requires_delivery_evidence
  check (
    status <> 'sent'
    or (
      direction = 'outbound'
      and sent_at is not null
      and external_thread_ref_hash is not null
      and length(btrim(external_thread_ref_hash)) > 0
      and delivery_receipt_hash is not null
      and length(btrim(delivery_receipt_hash)) > 0
    )
  );

create unique index uq_career_mail_actions_user_delivery_receipt
  on public.career_mail_actions(user_id, delivery_receipt_hash)
  where delivery_receipt_hash is not null;

create unique index uq_career_applications_user_external_receipt
  on public.career_applications(user_id, external_application_ref_hash)
  where external_application_ref_hash is not null;

comment on column public.career_mail_actions.delivery_receipt_hash is
  'SHA-256 (or equivalent irreversible hash) of provider-derived successful delivery receipt identity. Populate only after provider success.';

comment on constraint career_mail_actions_sent_requires_delivery_evidence on public.career_mail_actions is
  'Fail-closed: sent requires outbound direction, sent timestamp, thread reference, and provider-derived delivery receipt hash.';
