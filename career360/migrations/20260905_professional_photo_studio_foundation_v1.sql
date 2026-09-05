create table if not exists public.career_profile_photo_versions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  source_media_id uuid not null references public.career_profile_media(id) on delete cascade,
  storage_object_path text,
  mime_type text,
  size_bytes bigint,
  sha256 text,
  style_key text not null,
  style_context jsonb not null default '{}'::jsonb,
  status text not null default 'proposed' check (status in ('proposed','approved','rejected','deleted')),
  is_primary boolean not null default false,
  generated_at timestamptz,
  decided_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check ((storage_object_path is null and generated_at is null) or (storage_object_path is not null and generated_at is not null))
);

alter table public.career_profile_photo_versions enable row level security;

drop policy if exists career_profile_photo_versions_select_own on public.career_profile_photo_versions;
create policy career_profile_photo_versions_select_own
on public.career_profile_photo_versions
for select to authenticated
using ((select auth.uid()) = user_id);

revoke insert, update, delete on public.career_profile_photo_versions from authenticated;
grant select on public.career_profile_photo_versions to authenticated;

create unique index if not exists uq_career_profile_photo_versions_primary
on public.career_profile_photo_versions(user_id)
where is_primary = true and status = 'approved';

create index if not exists idx_career_profile_photo_versions_user_created
on public.career_profile_photo_versions(user_id, created_at desc);

comment on table public.career_profile_photo_versions is 'Professional photo studio variants. Original image remains in career_profile_media; generated variants require explicit approval before becoming primary.';
