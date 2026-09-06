-- LSI Career 360 — delivery/application receipt guards
-- 2026-09-06
-- Principle: approval/preparation is not delivery/application evidence.

alter table public.career_mail_actions
  add constraint career_mail_actions_sent_requires_delivery_evidence
  check (
    status <> 'sent'
    or (
      direction = 'outbound'
      and sent_at is not null
      and external_thread_ref_hash is not null
      and length(btrim(external_thread_ref_hash)) > 0
    )
  );

alter table public.career_applications
  add constraint career_applications_applied_requires_external_evidence
  check (
    status <> 'applied'
    or (
      applied_at is not null
      and external_application_ref_hash is not null
      and length(btrim(external_application_ref_hash)) > 0
    )
  );

comment on constraint career_mail_actions_sent_requires_delivery_evidence on public.career_mail_actions is
  'Fail-closed: status sent requires outbound delivery timestamp and external thread reference evidence.';

comment on constraint career_applications_applied_requires_external_evidence on public.career_applications is
  'Fail-closed: status applied requires application timestamp and external application reference evidence.';
