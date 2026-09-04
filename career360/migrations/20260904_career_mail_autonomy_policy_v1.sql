alter table public.career_action_permissions
  add column if not exists email_autonomy_mode text not null default 'suggestion' check (email_autonomy_mode in ('suggestion','one_tap','controlled_autopilot')),
  add column if not exists allow_simple_ack_auto_send boolean not null default false,
  add column if not exists allow_simple_availability_auto_send boolean not null default false,
  add column if not exists allow_followup_auto_send boolean not null default false;

comment on column public.career_action_permissions.email_autonomy_mode is 'suggestion=copy only; one_tap=explicit approval; controlled_autopilot=safe categories only. Sensitive categories always require confirmation.';