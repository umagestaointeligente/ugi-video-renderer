create table if not exists public.career_photo_preferences (
  user_id uuid primary key references auth.users(id) on delete cascade,
  offer_professional_photo boolean not null default true,
  preferred_style text not null default 'auto' check (preferred_style in ('auto','executive','corporate','modern','creative')),
  active_variant_id uuid,
  updated_at timestamptz not null default now()
);

create table if not exists public.career_photo_variants (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  source_media_id uuid not null references public.career_profile_media(id) on delete cascade,
  style_key text not null check (style_key in ('executive','corporate','modern','creative')),
  style_reason text,
  generation_mode text not null default 'local_polish' check (generation_mode in ('local_polish','generative')),
  provider text not null default 'browser_local',
  model text,
  prompt_version text not null default 'career-photo-v1',
  prompt_safe jsonb not null default '{}'::jsonb,
  storage_object_path text,
  mime_type text check (mime_type is null or mime_type in ('image/jpeg','image/png','image/webp')),
  size_bytes bigint check (size_bytes is null or (size_bytes > 0 and size_bytes <= 5242880)),
  sha256 text,
  status text not null default 'prepared' check (status in ('prepared','processing','ready','accepted','rejected','stale','failed')),
  created_at timestamptz not null default now(),
  ready_at timestamptz,
  accepted_at timestamptz,
  rejected_at timestamptz
);

alter table public.career_photo_preferences enable row level security;
alter table public.career_photo_variants enable row level security;

create policy career_photo_preferences_select_own on public.career_photo_preferences
for select to authenticated using ((select auth.uid()) = user_id);
create policy career_photo_preferences_insert_own on public.career_photo_preferences
for insert to authenticated with check ((select auth.uid()) = user_id);
create policy career_photo_preferences_update_own on public.career_photo_preferences
for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy career_photo_variants_select_own on public.career_photo_variants
for select to authenticated using ((select auth.uid()) = user_id);

revoke insert, update, delete on public.career_photo_variants from authenticated;
grant select on public.career_photo_variants to authenticated;

create index if not exists idx_career_photo_variants_user_created on public.career_photo_variants(user_id, created_at desc);
create index if not exists idx_career_photo_variants_source on public.career_photo_variants(source_media_id);

alter table public.career_photo_preferences
  add constraint career_photo_preferences_active_variant_id_fkey
  foreign key (active_variant_id) references public.career_photo_variants(id) on delete set null;

create or replace function public.career_photo_source_changed()
returns trigger language plpgsql security definer
set search_path = public, pg_catalog
as $$
begin
  if tg_op = 'UPDATE' and new.storage_object_path is distinct from old.storage_object_path then
    update public.career_photo_variants set status='stale'
      where user_id=new.user_id and source_media_id=old.id and status in ('prepared','processing','ready','accepted');
    update public.career_photo_preferences set active_variant_id=null, updated_at=now()
      where user_id=new.user_id;
  end if;
  return new;
end;
$$;

create trigger trg_career_photo_source_changed
after update of storage_object_path on public.career_profile_media
for each row execute function public.career_photo_source_changed();
