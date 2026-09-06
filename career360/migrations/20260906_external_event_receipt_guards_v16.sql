-- Career 360 V16 — external event receipt guards
-- Fail-closed evidence contract for externally observed events.

alter table public.career_mail_actions
  add column if not exists external_message_ref_hash text;

alter table public.career_applications
  add column if not exists external_status_ref_hash text,
  add column if not exists external_status_observed_at timestamptz;

alter table public.career_mail_actions
  drop constraint if exists career_mail_actions_inbound_requires_external_message_evidence;

alter table public.career_mail_actions
  add constraint career_mail_actions_inbound_requires_external_message_evidence
  check (
    direction <> 'inbound'
    or (
      received_at is not null
      and external_thread_ref_hash is not null
      and length(btrim(external_thread_ref_hash)) > 0
      and external_message_ref_hash is not null
      and length(btrim(external_message_ref_hash)) > 0
    )
  );

create unique index if not exists uq_career_mail_actions_user_external_message
  on public.career_mail_actions(user_id, external_message_ref_hash)
  where external_message_ref_hash is not null;

comment on column public.career_mail_actions.external_message_ref_hash is
  'Hash of provider message identity used as evidence for an inbound message. Distinct from thread identity.';

comment on constraint career_mail_actions_inbound_requires_external_message_evidence on public.career_mail_actions is
  'Fail-closed: inbound mail requires received_at plus external thread and message identities.';

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
      external_status_ref_hash is not null
      and length(btrim(external_status_ref_hash)) > 0
      and external_status_observed_at is not null
    )
  );

create unique index if not exists uq_career_applications_user_external_status_receipt
  on public.career_applications(user_id, external_status_ref_hash)
  where external_status_ref_hash is not null;

comment on column public.career_applications.external_status_ref_hash is
  'Hash of external provider event/message/application-state identity supporting an external application milestone.';

comment on column public.career_applications.external_status_observed_at is
  'Timestamp when the supporting external milestone evidence was observed.';

comment on constraint career_applications_external_milestone_requires_receipt on public.career_applications is
  'Fail-closed: externally asserted application milestones require external receipt identity and observed timestamp.';
