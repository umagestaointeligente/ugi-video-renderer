-- RETIRED / INTENTIONAL NO-OP
-- This migration briefly introduced an empty parallel `career_professional_photo_jobs` route.
-- The canonical Professional Photo Studio is:
--   career360/migrations/20260905_career_professional_photo_studio_v1.sql
-- with `career_profile_photo_variants` + `career_profile_photo_settings`.
--
-- Do not recreate the jobs route on fresh environments.
select 1;
