-- Cleanup after transient duplicate photo-studio route.
-- Canonical schema is career_profile_photo_variants + career_profile_photo_settings.
alter table public.career_profiles drop column if exists active_professional_photo_job_id;
drop table if exists public.career_professional_photo_jobs;
