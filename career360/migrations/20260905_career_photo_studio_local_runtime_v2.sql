-- LSI Career 360 — Professional Photo Studio V14 local runtime hardening
-- Applied to production on 2026-09-05.

create index if not exists idx_career_photo_variants_source_status_created
  on public.career_profile_photo_variants(user_id, source_media_id, status, created_at desc);

insert into public.career_profile_photo_settings(user_id,selected_kind,selected_variant_id,ai_opt_in)
select distinct user_id,'original'::text,null::uuid,true
from public.career_profile_media
where media_type='profile_photo'
on conflict (user_id) do nothing;

alter table public.career_profile_photo_settings alter column ai_opt_in set default true;

alter table public.career_profile_photo_variants enable row level security;
alter table public.career_profile_photo_settings enable row level security;
revoke insert, update, delete on public.career_profile_photo_variants from authenticated;
revoke insert, update, delete on public.career_profile_photo_settings from authenticated;

-- Empty experimental routes removed after readback and dependency check.
drop table if exists public.career_photo_studio_versions;
drop table if exists public.career_profile_photo_versions;
