-- LSI Career 360 V15 — scale hardening
-- Remove exact duplicate unique indexes and add covering indexes for foreign keys.

drop index if exists public.uq_career_opportunity_fingerprint;
drop index if exists public.uq_career_opportunity_source_job;

create index if not exists idx_career_applications_opportunity_id
  on public.career_applications(opportunity_id);

create index if not exists idx_career_mail_actions_application_id
  on public.career_mail_actions(application_id);

create index if not exists idx_career_profile_photo_settings_selected_variant_id
  on public.career_profile_photo_settings(selected_variant_id)
  where selected_variant_id is not null;

create index if not exists idx_career_profile_photo_variants_source_media_id
  on public.career_profile_photo_variants(source_media_id);

create index if not exists idx_career_role_expansion_audit_plan_id
  on public.career_role_expansion_audit(plan_id);

create index if not exists idx_career_role_expansion_audit_user_id
  on public.career_role_expansion_audit(user_id);

create index if not exists idx_career_role_relations_to_role_key
  on public.career_role_relations(to_role_key);

create index if not exists idx_career_role_unresolved_titles_mapped_role_key
  on public.career_role_unresolved_titles(mapped_role_key)
  where mapped_role_key is not null;
