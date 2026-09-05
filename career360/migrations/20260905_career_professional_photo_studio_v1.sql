-- LSI Career 360 — Professional Photo Studio V1
-- Canonical model. Replaces the empty legacy career_photo_* parallel route.

create table if not exists public.career_profile_photo_variants (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  source_media_id uuid not null references public.career_profile_media(id) on delete cascade,
  provider text not null check (provider in ('local-studio-v1','cloudflare-flux2-klein-4b','cloudflare-sd15-img2img')),
  style_key text not null check (style_key in ('executive','commercial','modern','creative','professional')),
  prompt_version text not null default 'career-photo-prompt-v1',
  storage_object_path text,
  mime_type text not null check (mime_type in ('image/jpeg','image/png','image/webp')),
  size_bytes bigint not null check (size_bytes > 0 and size_bytes <= 8388608),
  sha256 text not null,
  status text not null default 'generated' check (status in ('generated','accepted','rejected','superseded')),
  metadata_safe jsonb not null default '{}'::jsonb,
  generation_request_id uuid default gen_random_uuid(),
  created_at timestamptz not null default now(),
  decided_at timestamptz
);

create table if not exists public.career_profile_photo_settings (
  user_id uuid primary key references auth.users(id) on delete cascade,
  selected_kind text not null default 'original' check (selected_kind in ('original','variant')),
  selected_variant_id uuid references public.career_profile_photo_variants(id) on delete set null,
  preferred_style_key text check (preferred_style_key in ('executive','commercial','modern','creative','professional')),
  ai_opt_in boolean not null default true,
  updated_at timestamptz not null default now(),
  constraint career_profile_photo_settings_variant_guard
    check ((selected_kind='original' and selected_variant_id is null) or (selected_kind='variant' and selected_variant_id is not null))
);

alter table public.career_profile_photo_variants enable row level security;
alter table public.career_profile_photo_settings enable row level security;

drop policy if exists career_photo_variants_select_own on public.career_profile_photo_variants;
create policy career_photo_variants_select_own on public.career_profile_photo_variants
for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

drop policy if exists career_photo_settings_select_own on public.career_profile_photo_settings;
create policy career_photo_settings_select_own on public.career_profile_photo_settings
for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

revoke insert, update, delete on public.career_profile_photo_variants from authenticated;
revoke insert, update, delete on public.career_profile_photo_settings from authenticated;
grant select on public.career_profile_photo_variants to authenticated;
grant select on public.career_profile_photo_settings to authenticated;

create index if not exists idx_career_photo_variants_user_created on public.career_profile_photo_variants(user_id, created_at desc);
create index if not exists idx_career_photo_variants_source on public.career_profile_photo_variants(source_media_id);
create index if not exists idx_career_photo_variants_status on public.career_profile_photo_variants(user_id,status,created_at desc);
create index if not exists idx_career_photo_variants_path on public.career_profile_photo_variants(storage_object_path) where storage_object_path is not null;
create unique index if not exists uq_career_photo_generation_request on public.career_profile_photo_variants(user_id,generation_request_id) where generation_request_id is not null;

create or replace function public.career_photo_variant_owned_source_guard()
returns trigger language plpgsql security definer set search_path=pg_catalog,public as $$
begin
  if not exists(
    select 1 from public.career_profile_media m
    where m.id=new.source_media_id and m.user_id=new.user_id and m.media_type='profile_photo'
  ) then
    raise exception 'PHOTO_SOURCE_OWNERSHIP_MISMATCH';
  end if;
  return new;
end$$;

drop trigger if exists trg_career_photo_variant_source_guard on public.career_profile_photo_variants;
create trigger trg_career_photo_variant_source_guard
before insert or update of source_media_id,user_id on public.career_profile_photo_variants
for each row execute function public.career_photo_variant_owned_source_guard();
revoke all on function public.career_photo_variant_owned_source_guard() from public, anon, authenticated;

create or replace function public.career_photo_reject_cleanup_guard()
returns trigger language plpgsql security definer set search_path=pg_catalog,public as $$
begin
  if old.status='accepted' and new.status='rejected' then
    raise exception 'ACCEPTED_VARIANT_CANNOT_BE_REJECTED_DIRECTLY';
  end if;
  return new;
end$$;

drop trigger if exists trg_career_photo_reject_guard on public.career_profile_photo_variants;
create trigger trg_career_photo_reject_guard
before update of status on public.career_profile_photo_variants
for each row execute function public.career_photo_reject_cleanup_guard();
revoke all on function public.career_photo_reject_cleanup_guard() from public, anon, authenticated;

create or replace function public.career_photo_setting_variant_owner_guard()
returns trigger language plpgsql security definer set search_path=pg_catalog,public as $$
begin
  if new.selected_kind='variant' then
    if new.selected_variant_id is null or not exists(
      select 1 from public.career_profile_photo_variants v
      where v.id=new.selected_variant_id and v.user_id=new.user_id and v.status='accepted'
    ) then
      raise exception 'SELECTED_VARIANT_INVALID';
    end if;
  end if;
  return new;
end$$;

drop trigger if exists trg_career_photo_setting_variant_guard on public.career_profile_photo_settings;
create trigger trg_career_photo_setting_variant_guard
before insert or update of selected_kind,selected_variant_id,user_id on public.career_profile_photo_settings
for each row execute function public.career_photo_setting_variant_owner_guard();
revoke all on function public.career_photo_setting_variant_owner_guard() from public, anon, authenticated;

insert into public.career_profile_photo_settings(user_id,selected_kind,selected_variant_id)
select distinct user_id,'original'::text,null::uuid from public.career_profile_media
on conflict (user_id) do nothing;

-- The legacy route was empty at migration time and is intentionally retired.
drop table if exists public.career_photo_preferences;
drop table if exists public.career_photo_variants;
