-- LSI Career 360 — hardening do Privacy Gate V1

begin;

create or replace function public.career_normalize_employer_name(input_name text)
returns text
language sql
immutable
set search_path = public
as $$
  select trim(
    regexp_replace(
      regexp_replace(lower(coalesce(input_name, '')), '[^[:alnum:]]+', ' ', 'g'),
      '\s+', ' ', 'g'
    )
  );
$$;

-- Diretório é backend-only. Políticas explícitas tornam o deny auditável.
create policy career_employer_entities_deny_authenticated
on public.career_employer_entities
for all
to authenticated
using (false)
with check (false);

create policy career_employer_aliases_deny_authenticated
on public.career_employer_aliases
for all
to authenticated
using (false)
with check (false);

commit;
