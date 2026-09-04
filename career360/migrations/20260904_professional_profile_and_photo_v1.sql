create table if not exists public.career_profile_media (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  media_type text not null default 'profile_photo' check (media_type = 'profile_photo'),
  storage_object_path text not null,
  mime_type text not null check (mime_type in ('image/jpeg','image/png','image/webp')),
  size_bytes bigint not null check (size_bytes > 0 and size_bytes <= 5242880),
  sha256 text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, media_type)
);

alter table public.career_profile_media enable row level security;
drop policy if exists career_profile_media_select_own on public.career_profile_media;
create policy career_profile_media_select_own on public.career_profile_media
for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
revoke insert, update, delete on public.career_profile_media from authenticated;
grant select on public.career_profile_media to authenticated;

create table if not exists public.career_professional_profile_versions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  version integer not null,
  profile_json jsonb not null,
  source_hash text not null,
  status text not null default 'draft' check (status in ('draft','accepted','superseded')),
  created_at timestamptz not null default now(),
  accepted_at timestamptz,
  unique(user_id, version)
);

alter table public.career_professional_profile_versions enable row level security;
drop policy if exists career_professional_profile_versions_select_own on public.career_professional_profile_versions;
create policy career_professional_profile_versions_select_own on public.career_professional_profile_versions
for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
revoke insert, update, delete on public.career_professional_profile_versions from authenticated;
grant select on public.career_professional_profile_versions to authenticated;

create index if not exists idx_career_profile_media_user on public.career_profile_media(user_id);
create index if not exists idx_career_prof_profile_versions_user_created on public.career_professional_profile_versions(user_id, created_at desc);

-- Profile photos remain in a private Storage bucket managed only by authenticated Edge adapters.
-- No client storage.objects policy is granted for that bucket.
