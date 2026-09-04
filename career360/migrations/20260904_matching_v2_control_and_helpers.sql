-- LSI Career 360 — Matching V2 champion control + bilingual role helpers
-- Runtime source reconciled from Supabase project nxjdnzdxclszqyqrkwdk on 2026-09-04.

create table if not exists public.career_engine_control (
  component text primary key,
  champion_version text not null,
  rollback_version text,
  status text not null default 'active',
  updated_at timestamptz not null default now(),
  notes_safe jsonb not null default '{}'::jsonb
);

alter table public.career_engine_control enable row level security;
revoke all on table public.career_engine_control from public, anon, authenticated;
grant all on table public.career_engine_control to service_role;

drop policy if exists career_engine_control_deny_client on public.career_engine_control;
create policy career_engine_control_deny_client
on public.career_engine_control
for all
to anon, authenticated
using (false)
with check (false);

insert into public.career_engine_control(component,champion_version,rollback_version,status,notes_safe)
values ('matching','v2.0','v1.0','active',jsonb_build_object('qa_cases',6,'promotion_reason','bilingual_role_family_and_seniority_QA_passed'))
on conflict(component) do update
set champion_version=excluded.champion_version,
    rollback_version=excluded.rollback_version,
    status=excluded.status,
    notes_safe=excluded.notes_safe,
    updated_at=now();

create or replace function public.career_role_family(p_text text)
returns text
language plpgsql
stable
set search_path to 'public'
as $$
declare n text := public.career_normalize_text(coalesce(p_text,''));
begin
  if n = '' then return 'unknown'; end if;
  if n ~ '(sales|comercial|revenue|business development|bizdev|go to market|gtm|account executive|account director|partnership|parcerias)' then return 'commercial'; end if;
  if n ~ '(compras|procurement|purchasing|sourcing|category|categoria|buyer|buying)' then return 'procurement'; end if;
  if n ~ '(marketing|brand|crm|loyalty|engagement|communications|comunicacao)' then return 'marketing'; end if;
  if n ~ '(finance|financial|financas|financeiro|fp&a|controller|controllership|accounting|contabilidade|treasury|tesouraria)' then return 'finance'; end if;
  if n ~ '(human resources|recursos humanos|people|talent|recruit|payroll|folha)' then return 'hr'; end if;
  if n ~ '(operations|operacoes|operacao|logistics|logistica|supply chain|customer operations)' then return 'operations'; end if;
  if n ~ '(software|engineering|engenharia|developer|desenvolvedor|technology|tecnologia|platform engineering|devops|infrastructure)' then return 'technology'; end if;
  if n ~ '(product manager|product lead|produto)' then return 'product'; end if;
  if n ~ '(data|analytics|analitica|business intelligence|\bbi\b)' then return 'data'; end if;
  if n ~ '(legal|juridico|compliance|aml|regulatory)' then return 'legal_compliance'; end if;
  if n ~ '(medical|clinical|medico|clinico|health|saude)' then return 'health'; end if;
  return 'unknown';
end;
$$;

create or replace function public.career_seniority_rank(p_text text)
returns integer
language plpgsql
stable
set search_path to 'public'
as $$
declare n text := public.career_normalize_text(coalesce(p_text,''));
begin
  if n = '' then return 0; end if;
  if n ~ '(chief executive officer|chief commercial officer|chief revenue officer|chief operating officer|chief financial officer|(^|[[:space:]])ceo([[:space:]]|$)|(^|[[:space:]])cco([[:space:]]|$)|(^|[[:space:]])cro([[:space:]]|$)|(^|[[:space:]])coo([[:space:]]|$)|(^|[[:space:]])cfo([[:space:]]|$))' then return 11; end if;
  if n ~ '(vice president|vice-presidente|vice presidente|(^|[[:space:]])vp([[:space:]]|$))' then return 10; end if;
  if n ~ '(director|diretor|diretora)' and n !~ '(associate director)' then return 9; end if;
  if n ~ '(associate director|head of|(^|[[:space:]])head([[:space:]]|$))' then return 8; end if;
  if n ~ '(senior manager|sr manager|gerente senior|gerente sr)' then return 7; end if;
  if n ~ '(general manager|manager|gerente)' then return 6; end if;
  if n ~ '(coordinator|coordenador|coordenadora|supervisor|supervisora)' then return 5; end if;
  if n ~ '(account executive|executivo de contas|specialist|especialista|consultant|consultor|consultora|senior analyst|analista senior|analista sr)' then return 4; end if;
  if n ~ '(sales development representative|representative|representante|analyst|analista)' then return 3; end if;
  if n ~ '((^|[[:space:]])lead([[:space:]]|$))' then return 7; end if;
  if n ~ '(assistant|assistente)' then return 2; end if;
  if n ~ '(intern|internship|estagio|estagiario|estagiaria)' then return 1; end if;
  return 0;
end;
$$;

revoke all on function public.career_role_family(text) from public, anon, authenticated;
revoke all on function public.career_seniority_rank(text) from public, anon, authenticated;
grant execute on function public.career_role_family(text) to service_role;
grant execute on function public.career_seniority_rank(text) to service_role;
