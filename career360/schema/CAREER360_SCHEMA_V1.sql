-- LSI Career 360 — Schema lógico Beta 1.0
-- Status: DESIGN EXECUTÁVEL / NÃO APLICADO A PROJETO SUPABASE AINDA
-- Motivo: Career terá projeto Supabase próprio; não reutilizar lsi-revenue-autopilot.
--
-- Regras:
-- 1) RLS em toda tabela exposta;
-- 2) anon sem acesso;
-- 3) ownership sempre por auth.uid() = user_id;
-- 4) nenhuma decisão de autorização baseada em user_metadata;
-- 5) nenhuma service_role no frontend;
-- 6) audit_events não aceita INSERT direto do cliente.

begin;

create table if not exists public.career_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references auth.users(id) on delete cascade,
  display_name text,
  current_role text,
  current_employer text,
  current_employment_confirmed boolean not null default false,
  city text,
  state_code text,
  country_code text not null default 'BR',
  onboarding_status text not null default 'started'
    check (onboarding_status in ('started','draft_ready','privacy_ready','goals_ready','agent_ready')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.career_preferences (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references auth.users(id) on delete cascade,
  target_roles jsonb not null default '[]'::jsonb,
  preferred_locations jsonb not null default '[]'::jsonb,
  work_models jsonb not null default '[]'::jsonb,
  salary_floor_brl numeric(12,2),
  salary_target_brl numeric(12,2),
  alert_channels jsonb not null default '[]'::jsonb,
  autonomy_level text not null default 'one_action'
    check (autonomy_level in ('autopilot','one_action','human_first')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.career_employer_blocks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  employer_name text not null,
  normalized_name text,
  employer_group_key text,
  block_reason text not null
    check (block_reason in ('current_employer','former_employer','user_requested','group_related','other')),
  source text not null default 'user_confirmed'
    check (source in ('user_confirmed','resume_draft','system_group_resolution')),
  user_confirmed boolean not null default false,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  unique(user_id, employer_name)
);

create table if not exists public.career_documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  original_filename_display text not null,
  detected_type text not null check (detected_type in ('pdf','docx')),
  size_bytes bigint not null check (size_bytes > 0),
  sha256 text not null,
  storage_object_path text,
  file_status text not null default 'quarantined'
    check (file_status in ('quarantined','safe_for_parse','parsed','rejected','deleted')),
  parser_version text,
  rejection_code text,
  raw_file_retention_until timestamptz,
  created_at timestamptz not null default now(),
  deleted_at timestamptz
);

create table if not exists public.career_profile_drafts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  document_id uuid references public.career_documents(id) on delete set null,
  draft_version integer not null default 1,
  draft_json jsonb not null,
  parser_version text not null,
  status text not null default 'requires_confirmation'
    check (status in ('requires_confirmation','partially_confirmed','confirmed','superseded','rejected')),
  created_at timestamptz not null default now(),
  confirmed_at timestamptz
);

create table if not exists public.career_confirmed_facts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  draft_id uuid references public.career_profile_drafts(id) on delete set null,
  fact_type text not null,
  fact_value jsonb not null,
  source_document_id uuid references public.career_documents(id) on delete set null,
  confirmation_method text not null
    check (confirmation_method in ('explicit_ui','explicit_voice_confirmation','manual_entry','verified_external_source')),
  confirmed_at timestamptz not null default now(),
  superseded_at timestamptz
);

create table if not exists public.career_action_permissions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references auth.users(id) on delete cascade,
  allow_opportunity_research boolean not null default true,
  allow_cv_customization boolean not null default false,
  allow_application_draft boolean not null default false,
  allow_application_submit boolean not null default false,
  allow_recruiter_contact_draft boolean not null default false,
  allow_recruiter_contact_send boolean not null default false,
  require_confirmation_for_identity_disclosure boolean not null default true,
  updated_at timestamptz not null default now()
);

create table if not exists public.career_audit_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  event_type text not null,
  entity_type text,
  entity_id uuid,
  outcome text not null,
  reason_code text,
  metadata_safe jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- Índices de ownership e consulta seletiva; evitar full scans conforme a base crescer.
create index if not exists idx_career_blocks_user_active on public.career_employer_blocks(user_id, active);
create index if not exists idx_career_documents_user_created on public.career_documents(user_id, created_at desc);
create index if not exists idx_career_drafts_user_created on public.career_profile_drafts(user_id, created_at desc);
create index if not exists idx_career_facts_user_type on public.career_confirmed_facts(user_id, fact_type) where superseded_at is null;
create index if not exists idx_career_audit_user_created on public.career_audit_events(user_id, created_at desc);

-- RLS explícito em todas as tabelas do schema public.
alter table public.career_profiles enable row level security;
alter table public.career_preferences enable row level security;
alter table public.career_employer_blocks enable row level security;
alter table public.career_documents enable row level security;
alter table public.career_profile_drafts enable row level security;
alter table public.career_confirmed_facts enable row level security;
alter table public.career_action_permissions enable row level security;
alter table public.career_audit_events enable row level security;

-- Revogar defaults antes de conceder o mínimo necessário.
revoke all on table public.career_profiles from anon, authenticated;
revoke all on table public.career_preferences from anon, authenticated;
revoke all on table public.career_employer_blocks from anon, authenticated;
revoke all on table public.career_documents from anon, authenticated;
revoke all on table public.career_profile_drafts from anon, authenticated;
revoke all on table public.career_confirmed_facts from anon, authenticated;
revoke all on table public.career_action_permissions from anon, authenticated;
revoke all on table public.career_audit_events from anon, authenticated;

-- Usuário autenticado pode administrar apenas dados que pertencem a ele.
grant select, insert, update, delete on public.career_profiles to authenticated;
grant select, insert, update, delete on public.career_preferences to authenticated;
grant select, insert, update, delete on public.career_employer_blocks to authenticated;
grant select on public.career_documents to authenticated;
grant select on public.career_profile_drafts to authenticated;
grant select, insert, update, delete on public.career_confirmed_facts to authenticated;
grant select, insert, update on public.career_action_permissions to authenticated;
grant select on public.career_audit_events to authenticated;

-- Helper textual repetido de propósito: políticas explícitas por operação facilitam auditoria.

create policy career_profiles_select_own on public.career_profiles for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_profiles_insert_own on public.career_profiles for insert to authenticated
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_profiles_update_own on public.career_profiles for update to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id)
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_profiles_delete_own on public.career_profiles for delete to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy career_preferences_select_own on public.career_preferences for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_preferences_insert_own on public.career_preferences for insert to authenticated
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_preferences_update_own on public.career_preferences for update to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id)
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_preferences_delete_own on public.career_preferences for delete to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy career_blocks_select_own on public.career_employer_blocks for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_blocks_insert_own on public.career_employer_blocks for insert to authenticated
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_blocks_update_own on public.career_employer_blocks for update to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id)
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_blocks_delete_own on public.career_employer_blocks for delete to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy career_documents_select_own on public.career_documents for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy career_drafts_select_own on public.career_profile_drafts for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy career_facts_select_own on public.career_confirmed_facts for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_facts_insert_own on public.career_confirmed_facts for insert to authenticated
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_facts_update_own on public.career_confirmed_facts for update to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id)
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_facts_delete_own on public.career_confirmed_facts for delete to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy career_permissions_select_own on public.career_action_permissions for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_permissions_insert_own on public.career_action_permissions for insert to authenticated
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);
create policy career_permissions_update_own on public.career_action_permissions for update to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id)
with check ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create policy career_audit_select_own on public.career_audit_events for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

commit;
