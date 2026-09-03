begin;

create schema if not exists career_private;
revoke all on schema career_private from public, anon, authenticated;

create table if not exists career_private.master_email_hashes (
  email_hash text primary key,
  label text not null default 'master',
  created_at timestamptz not null default now()
);

revoke all on table career_private.master_email_hashes from public, anon, authenticated;

insert into career_private.master_email_hashes(email_hash, label)
values ('6f24e325dd9dbd00526f0182aa9e1b9c76fa0e274dffe24877888a4883c19b15', 'owner_master')
on conflict (email_hash) do nothing;

create table if not exists public.career_user_roles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  role text not null default 'candidate' check (role in ('candidate','master')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.career_user_roles enable row level security;
revoke all on table public.career_user_roles from anon, authenticated;
grant select on table public.career_user_roles to authenticated;

drop policy if exists career_user_roles_select_own on public.career_user_roles;
create policy career_user_roles_select_own
on public.career_user_roles
for select
to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create or replace function career_private.bootstrap_career_user()
returns trigger
language plpgsql
security definer
set search_path = pg_catalog, public, career_private, extensions
as $$
declare
  normalized_email text;
  computed_hash text;
  assigned_role text := 'candidate';
begin
  normalized_email := lower(trim(coalesce(new.email, '')));
  if normalized_email <> '' then
    computed_hash := encode(extensions.digest(normalized_email, 'sha256'), 'hex');
    if exists (
      select 1
      from career_private.master_email_hashes m
      where m.email_hash = computed_hash
    ) then
      assigned_role := 'master';
    end if;
  end if;

  insert into public.career_user_roles(user_id, role)
  values (new.id, assigned_role)
  on conflict (user_id) do update set role = excluded.role, updated_at = now();

  insert into public.career_profiles(user_id, onboarding_status)
  values (new.id, 'started')
  on conflict (user_id) do nothing;

  insert into public.career_preferences(user_id)
  values (new.id)
  on conflict (user_id) do nothing;

  insert into public.career_action_permissions(user_id)
  values (new.id)
  on conflict (user_id) do nothing;

  return new;
end;
$$;

revoke all on function career_private.bootstrap_career_user() from public, anon, authenticated;

drop trigger if exists on_auth_user_created_career_bootstrap on auth.users;
create trigger on_auth_user_created_career_bootstrap
after insert on auth.users
for each row execute function career_private.bootstrap_career_user();

commit;
