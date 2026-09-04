alter table public.career_action_permissions
  add column if not exists allow_inbox_monitoring boolean not null default false,
  add column if not exists allow_recruiter_reply_draft boolean not null default false,
  add column if not exists allow_recruiter_reply_send boolean not null default false,
  add column if not exists allow_followup_draft boolean not null default false,
  add column if not exists allow_followup_send boolean not null default false,
  add column if not exists always_confirm_sensitive_email boolean not null default true;

create table if not exists public.career_digest_preferences (
  user_id uuid primary key references auth.users(id) on delete cascade,
  plan_key text not null default 'pilot',
  cadence_hours integer not null default 12 check (cadence_hours in (4,6,8,12)),
  timezone text not null default 'America/Sao_Paulo',
  in_app_enabled boolean not null default true,
  email_enabled boolean not null default false,
  critical_immediate boolean not null default true,
  last_digest_at timestamptz,
  next_digest_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.career_activity_ledger (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  event_type text not null,
  stage text,
  actor text not null default 'career_agent' check (actor in ('career_agent','user','external','system')),
  entity_type text,
  entity_id uuid,
  title text not null,
  summary_safe text,
  importance text not null default 'normal' check (importance in ('low','normal','high','critical')),
  metadata_safe jsonb not null default '{}'::jsonb,
  occurred_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);
create index if not exists idx_career_activity_ledger_user_time on public.career_activity_ledger(user_id, occurred_at desc);
create index if not exists idx_career_activity_ledger_user_type on public.career_activity_ledger(user_id, event_type, occurred_at desc);

create table if not exists public.career_applications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  opportunity_id uuid references public.career_opportunities(id) on delete set null,
  status text not null default 'considered' check (status in ('considered','draft_ready','awaiting_user','applied','recruiter_reply','interview_pending','interview_confirmed','finalist','offer','hired','rejected','withdrawn','closed')),
  external_application_ref_hash text,
  application_url text,
  evidence_safe jsonb not null default '{}'::jsonb,
  applied_at timestamptz,
  last_activity_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, opportunity_id)
);
create index if not exists idx_career_applications_user_status on public.career_applications(user_id, status, last_activity_at desc);

create table if not exists public.career_mail_actions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  application_id uuid references public.career_applications(id) on delete set null,
  external_thread_ref_hash text,
  direction text not null check (direction in ('inbound','outbound','draft')),
  message_kind text not null default 'recruiter' check (message_kind in ('recruiter','interview','followup','offer','application','other')),
  sender_display text,
  subject_safe text,
  summary_safe text,
  proposed_reply text,
  status text not null default 'detected' check (status in ('detected','draft_ready','awaiting_approval','approved','sent','copied','dismissed','failed')),
  critical boolean not null default false,
  requires_human boolean not null default false,
  sensitive_category text,
  received_at timestamptz,
  sent_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists idx_career_mail_actions_user_status on public.career_mail_actions(user_id, status, created_at desc);

create table if not exists public.career_notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  kind text not null check (kind in ('digest','critical','action_required','info')),
  title text not null,
  body text,
  source_event_key text,
  action_type text,
  action_payload_safe jsonb not null default '{}'::jsonb,
  status text not null default 'unread' check (status in ('unread','read','dismissed')),
  created_at timestamptz not null default now(),
  read_at timestamptz,
  unique(user_id, source_event_key)
);
create index if not exists idx_career_notifications_user_status on public.career_notifications(user_id, status, created_at desc);

create table if not exists public.career_digest_runs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  window_start timestamptz not null,
  window_end timestamptz not null,
  cadence_hours integer not null,
  status text not null default 'generated' check (status in ('generated','delivered_in_app','delivered_email','partial','failed')),
  summary_json jsonb not null default '{}'::jsonb,
  generated_at timestamptz not null default now(),
  delivered_at timestamptz
);
create index if not exists idx_career_digest_runs_user_time on public.career_digest_runs(user_id, generated_at desc);

alter table public.career_digest_preferences enable row level security;
alter table public.career_activity_ledger enable row level security;
alter table public.career_applications enable row level security;
alter table public.career_mail_actions enable row level security;
alter table public.career_notifications enable row level security;
alter table public.career_digest_runs enable row level security;

create policy career_digest_preferences_select_own on public.career_digest_preferences for select to authenticated using ((select auth.uid()) = user_id);
create policy career_activity_ledger_select_own on public.career_activity_ledger for select to authenticated using ((select auth.uid()) = user_id);
create policy career_applications_select_own on public.career_applications for select to authenticated using ((select auth.uid()) = user_id);
create policy career_mail_actions_select_own on public.career_mail_actions for select to authenticated using ((select auth.uid()) = user_id);
create policy career_notifications_select_own on public.career_notifications for select to authenticated using ((select auth.uid()) = user_id);
create policy career_notifications_update_own on public.career_notifications for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy career_digest_runs_select_own on public.career_digest_runs for select to authenticated using ((select auth.uid()) = user_id);

revoke insert, update, delete on public.career_digest_preferences from authenticated;
revoke insert, update, delete on public.career_activity_ledger from authenticated;
revoke insert, update, delete on public.career_applications from authenticated;
revoke insert, update, delete on public.career_mail_actions from authenticated;
revoke insert, delete on public.career_notifications from authenticated;
revoke insert, update, delete on public.career_digest_runs from authenticated;
grant select on public.career_digest_preferences, public.career_activity_ledger, public.career_applications, public.career_mail_actions, public.career_digest_runs to authenticated;
grant select, update on public.career_notifications to authenticated;

create or replace function public.career_emit_critical_mail_notification()
returns trigger language plpgsql security definer set search_path=public as $$
begin
  if new.critical = true and new.status in ('detected','draft_ready','awaiting_approval') then
    insert into public.career_notifications(user_id,kind,title,body,source_event_key,action_type,action_payload_safe)
    values(new.user_id,'critical',case when new.sender_display is not null then new.sender_display || ' respondeu' else 'Nova resposta importante' end,coalesce(new.summary_safe,'Há uma atualização importante no seu processo seletivo.'),'mail:'||new.id::text,'open_mail_action',jsonb_build_object('mail_action_id',new.id,'requires_human',new.requires_human,'message_kind',new.message_kind))
    on conflict(user_id,source_event_key) do update set title=excluded.title, body=excluded.body, action_payload_safe=excluded.action_payload_safe, status='unread';
  end if;
  return new;
end;$$;
revoke all on function public.career_emit_critical_mail_notification() from public, anon, authenticated;
create trigger trg_career_critical_mail_notification after insert or update of critical,status,summary_safe on public.career_mail_actions for each row execute function public.career_emit_critical_mail_notification();

insert into public.career_digest_preferences(user_id,plan_key,cadence_hours,next_digest_at)
select p.user_id,'pilot',4,now()+interval '4 hours' from public.career_profiles p where p.onboarding_status='agent_ready'
on conflict(user_id) do nothing;