-- LSI Career 360 — Proteção de Carreira / Privacy Gate V1
-- Status: migration canônica Beta 1.0
-- Princípio: empresa bloqueada = SILENT_BLOCK; empresa não resolvida = NO_DISCLOSURE.

begin;

create or replace function public.career_normalize_employer_name(input_name text)
returns text
language sql
immutable
as $$
  select trim(
    regexp_replace(
      regexp_replace(lower(coalesce(input_name, '')), '[^[:alnum:]]+', ' ', 'g'),
      '\s+', ' ', 'g'
    )
  );
$$;

create table if not exists public.career_employer_entities (
  id uuid primary key default gen_random_uuid(),
  canonical_name text not null,
  normalized_name text not null unique,
  employer_group_key text,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.career_employer_aliases (
  id uuid primary key default gen_random_uuid(),
  employer_entity_id uuid not null references public.career_employer_entities(id) on delete cascade,
  alias_name text not null,
  normalized_alias text not null unique,
  created_at timestamptz not null default now()
);

create index if not exists idx_career_employer_entities_group
  on public.career_employer_entities(employer_group_key)
  where employer_group_key is not null and active;
create index if not exists idx_career_employer_aliases_entity
  on public.career_employer_aliases(employer_entity_id);

alter table public.career_employer_entities enable row level security;
alter table public.career_employer_aliases enable row level security;

revoke all on table public.career_employer_entities from anon, authenticated;
revoke all on table public.career_employer_aliases from anon, authenticated;

-- Diretório de empresas/aliases é backend-only. Nenhuma policy para anon/authenticated.

alter table public.career_employer_blocks
  add column if not exists employer_entity_id uuid references public.career_employer_entities(id) on delete set null;

create index if not exists idx_career_blocks_entity_active
  on public.career_employer_blocks(user_id, employer_entity_id, active)
  where employer_entity_id is not null;
create index if not exists idx_career_blocks_group_active
  on public.career_employer_blocks(user_id, employer_group_key, active)
  where employer_group_key is not null;
create index if not exists idx_career_blocks_normalized_active
  on public.career_employer_blocks(user_id, normalized_name, active)
  where normalized_name is not null;

create or replace function public.career_resolve_employer(input_name text)
returns table(
  employer_entity_id uuid,
  canonical_name text,
  normalized_name text,
  employer_group_key text,
  resolution_source text
)
language sql
stable
security definer
set search_path = public
as $$
  with q as (
    select public.career_normalize_employer_name(input_name) as n
  ), direct_match as (
    select e.id, e.canonical_name, e.normalized_name, e.employer_group_key, 'canonical'::text as source, 1 as priority
    from public.career_employer_entities e, q
    where e.active and e.normalized_name = q.n
  ), alias_match as (
    select e.id, e.canonical_name, e.normalized_name, e.employer_group_key, 'alias'::text as source, 2 as priority
    from public.career_employer_aliases a
    join public.career_employer_entities e on e.id = a.employer_entity_id and e.active
    cross join q
    where a.normalized_alias = q.n
  )
  select m.id, m.canonical_name, m.normalized_name, m.employer_group_key, m.source
  from (
    select * from direct_match
    union all
    select * from alias_match
  ) m
  order by m.priority
  limit 1;
$$;

revoke all on function public.career_resolve_employer(text) from public, anon, authenticated;
grant execute on function public.career_resolve_employer(text) to service_role;

create or replace function public.career_privacy_gate(
  p_user_id uuid,
  p_employer_name text
)
returns table(
  decision text,
  reason_code text,
  resolved_employer_entity_id uuid,
  resolved_group_key text,
  identity_disclosure_required boolean
)
language plpgsql
stable
security definer
set search_path = public
as $$
declare
  v_norm text;
  v_entity record;
  v_blocked boolean := false;
  v_require_identity_confirmation boolean := true;
begin
  if p_user_id is null then
    raise exception 'USER_ID_REQUIRED';
  end if;

  v_norm := public.career_normalize_employer_name(p_employer_name);
  if v_norm = '' then
    return query select 'NO_DISCLOSURE', 'EMPLOYER_NAME_EMPTY', null::uuid, null::text, true;
    return;
  end if;

  select * into v_entity from public.career_resolve_employer(p_employer_name) limit 1;

  if v_entity.employer_entity_id is null then
    -- Mesmo sem diretório resolvido, um bloqueio manual pelo nome normalizado continua valendo.
    select exists (
      select 1
      from public.career_employer_blocks b
      where b.user_id = p_user_id
        and b.active
        and coalesce(b.normalized_name, public.career_normalize_employer_name(b.employer_name)) = v_norm
    ) into v_blocked;

    if v_blocked then
      return query select 'SILENT_BLOCK', 'USER_BLOCK_NAME_MATCH', null::uuid, null::text, true;
    else
      return query select 'NO_DISCLOSURE', 'EMPLOYER_UNRESOLVED', null::uuid, null::text, true;
    end if;
    return;
  end if;

  select exists (
    select 1
    from public.career_employer_blocks b
    where b.user_id = p_user_id
      and b.active
      and (
        b.employer_entity_id = v_entity.employer_entity_id
        or coalesce(b.normalized_name, public.career_normalize_employer_name(b.employer_name)) in (v_norm, v_entity.normalized_name)
        or (
          v_entity.employer_group_key is not null
          and b.employer_group_key = v_entity.employer_group_key
        )
      )
  ) into v_blocked;

  if v_blocked then
    return query select 'SILENT_BLOCK', 'EMPLOYER_OR_GROUP_BLOCKED', v_entity.employer_entity_id, v_entity.employer_group_key, true;
    return;
  end if;

  select p.require_confirmation_for_identity_disclosure
    into v_require_identity_confirmation
  from public.career_action_permissions p
  where p.user_id = p_user_id;

  v_require_identity_confirmation := coalesce(v_require_identity_confirmation, true);

  if v_require_identity_confirmation then
    return query select 'ALLOW', 'IDENTITY_CONFIRMATION_REQUIRED', v_entity.employer_entity_id, v_entity.employer_group_key, true;
  else
    return query select 'ALLOW', 'PRIVACY_GATE_CLEAR', v_entity.employer_entity_id, v_entity.employer_group_key, false;
  end if;
end;
$$;

revoke all on function public.career_privacy_gate(uuid, text) from public, anon, authenticated;
grant execute on function public.career_privacy_gate(uuid, text) to service_role;

commit;
