-- LSI Career 360 — Motor de Aderência V1
-- PRIVACIDADE ANTES DO SCORE. Apenas dados confirmados/preferências explícitas.

begin;

create extension if not exists pg_trgm;

create or replace function public.career_normalize_text(input_text text)
returns text
language sql
immutable
set search_path = public
as $$
  select trim(
    regexp_replace(
      regexp_replace(lower(coalesce(input_text, '')), '[^[:alnum:]]+', ' ', 'g'),
      '\s+', ' ', 'g'
    )
  );
$$;

create table if not exists public.career_opportunities (
  id uuid primary key default gen_random_uuid(),
  source_name text not null,
  source_job_id text,
  source_url text,
  employer_name text not null,
  employer_entity_id uuid references public.career_employer_entities(id) on delete set null,
  title text not null,
  description_text text,
  seniority text,
  sector text,
  city text,
  state_code text,
  country_code text not null default 'BR',
  work_model text not null default 'unknown'
    check (work_model in ('remote','hybrid','onsite','unknown')),
  salary_min numeric(12,2),
  salary_max numeric(12,2),
  salary_currency text not null default 'BRL',
  salary_evidence_class text not null default 'unknown'
    check (salary_evidence_class in ('explicit','estimated','hidden','unknown')),
  required_skills jsonb not null default '[]'::jsonb,
  preferred_skills jsonb not null default '[]'::jsonb,
  evidence_safe jsonb not null default '{}'::jsonb,
  published_at timestamptz,
  fetched_at timestamptz not null default now(),
  expires_at timestamptz,
  status text not null default 'active'
    check (status in ('active','expired','closed')),
  dedupe_fingerprint text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists uq_career_opportunity_source_job
  on public.career_opportunities(source_name, source_job_id)
  where source_job_id is not null;
create unique index if not exists uq_career_opportunity_fingerprint
  on public.career_opportunities(dedupe_fingerprint)
  where dedupe_fingerprint is not null;
create index if not exists idx_career_opportunities_active_fetched
  on public.career_opportunities(status, fetched_at desc);
create index if not exists idx_career_opportunities_employer
  on public.career_opportunities(employer_entity_id);

alter table public.career_opportunities enable row level security;
revoke all on table public.career_opportunities from anon, authenticated;
create policy career_opportunities_deny_authenticated
on public.career_opportunities
for all to authenticated
using (false)
with check (false);

alter table public.career_preferences
  add column if not exists preferred_sectors jsonb not null default '[]'::jsonb;

create table if not exists public.career_matches (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  opportunity_id uuid not null references public.career_opportunities(id) on delete cascade,
  engine_version text not null,
  score numeric(5,2),
  classification text not null
    check (classification in (
      'QUALIFIED',
      'QUALIFIED_SALARY_CONFIRM',
      'PENDING_DATA',
      'BLOCKED_PRIVACY',
      'BLOCKED_REQUIREMENT',
      'BELOW_FIT',
      'EXPIRED'
    )),
  privacy_decision text,
  salary_state text,
  breakdown jsonb not null default '{}'::jsonb,
  explanation_safe jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(user_id, opportunity_id, engine_version)
);

create index if not exists idx_career_matches_user_created
  on public.career_matches(user_id, created_at desc);
create index if not exists idx_career_matches_opportunity
  on public.career_matches(opportunity_id);

alter table public.career_matches enable row level security;
revoke all on table public.career_matches from anon, authenticated;
grant select on public.career_matches to authenticated;
create policy career_matches_select_own
on public.career_matches
for select to authenticated
using ((select auth.uid()) is not null and (select auth.uid()) = user_id);

create or replace function public.career_score_opportunity(
  p_user_id uuid,
  p_opportunity_id uuid,
  p_persist boolean default false
)
returns table(
  score numeric,
  classification text,
  privacy_decision text,
  salary_state text,
  breakdown jsonb,
  explanation_safe jsonb
)
language plpgsql
volatile
security definer
set search_path = public
as $$
declare
  v_o public.career_opportunities%rowtype;
  v_p public.career_preferences%rowtype;
  v_priv record;
  v_role_similarity numeric := null;
  v_role_points numeric := 0;
  v_skill_ratio numeric := null;
  v_skill_points numeric := 0;
  v_work_points numeric := 0;
  v_location_points numeric := 0;
  v_sector_points numeric := 0;
  v_total_points numeric := 0;
  v_total_weight numeric := 0;
  v_score numeric := null;
  v_classification text;
  v_salary_state text := 'NOT_APPLICABLE';
  v_breakdown jsonb;
  v_explanation jsonb;
  v_work_models_count int := 0;
  v_locations_count int := 0;
  v_sectors_count int := 0;
  v_required_skills_count int := 0;
  v_candidate_skills_count int := 0;
  v_skill_matches int := 0;
  v_role_count int := 0;
  v_location_known boolean := false;
  v_location_match boolean := false;
  v_sector_match boolean := false;
  v_work_match boolean := false;
  v_hard_block_reason text := null;
  v_threshold numeric := 72;
begin
  if p_user_id is null or p_opportunity_id is null then
    raise exception 'USER_AND_OPPORTUNITY_REQUIRED';
  end if;

  select * into v_o from public.career_opportunities where id = p_opportunity_id;
  if not found then raise exception 'OPPORTUNITY_NOT_FOUND'; end if;

  select * into v_p from public.career_preferences where user_id = p_user_id;
  if not found then
    -- Perfil sem preferências suficientes deve continuar pendente, nunca receber match inventado.
    return query select null::numeric, 'PENDING_DATA', null::text, 'UNKNOWN',
      jsonb_build_object('reason','PREFERENCES_NOT_FOUND'),
      jsonb_build_object('message','Preferências de carreira ainda não configuradas.');
    return;
  end if;

  if v_o.status <> 'active' or (v_o.expires_at is not null and v_o.expires_at <= now()) then
    v_classification := 'EXPIRED';
    v_breakdown := jsonb_build_object('gate','OPPORTUNITY_EXPIRED');
    v_explanation := jsonb_build_object('message','A oportunidade não está mais ativa.');
    if p_persist then
      insert into public.career_matches(user_id,opportunity_id,engine_version,score,classification,privacy_decision,salary_state,breakdown,explanation_safe)
      values(p_user_id,p_opportunity_id,'v1.0',null,v_classification,null,'UNKNOWN',v_breakdown,v_explanation)
      on conflict(user_id,opportunity_id,engine_version) do update
      set score=excluded.score,classification=excluded.classification,privacy_decision=excluded.privacy_decision,
          salary_state=excluded.salary_state,breakdown=excluded.breakdown,explanation_safe=excluded.explanation_safe,updated_at=now();
    end if;
    return query select null::numeric,v_classification,null::text,'UNKNOWN',v_breakdown,v_explanation;
    return;
  end if;

  select * into v_priv from public.career_privacy_gate(p_user_id, v_o.employer_name) limit 1;
  if v_priv.decision = 'SILENT_BLOCK' then
    v_classification := 'BLOCKED_PRIVACY';
    v_breakdown := jsonb_build_object('gate','PRIVACY','reason_code',v_priv.reason_code);
    v_explanation := jsonb_build_object('message','Oportunidade protegida pelas suas regras de privacidade.');
    if p_persist then
      insert into public.career_matches(user_id,opportunity_id,engine_version,score,classification,privacy_decision,salary_state,breakdown,explanation_safe)
      values(p_user_id,p_opportunity_id,'v1.0',null,v_classification,v_priv.decision,'UNKNOWN',v_breakdown,v_explanation)
      on conflict(user_id,opportunity_id,engine_version) do update
      set score=excluded.score,classification=excluded.classification,privacy_decision=excluded.privacy_decision,
          salary_state=excluded.salary_state,breakdown=excluded.breakdown,explanation_safe=excluded.explanation_safe,updated_at=now();
    end if;
    return query select null::numeric,v_classification,v_priv.decision,'UNKNOWN',v_breakdown,v_explanation;
    return;
  end if;

  -- Gate salarial: somente evidência EXPLÍCITA pode bloquear.
  if v_p.salary_floor_brl is not null then
    if v_o.salary_evidence_class = 'explicit' and v_o.salary_max is not null then
      if v_o.salary_max < v_p.salary_floor_brl then
        v_hard_block_reason := 'EXPLICIT_SALARY_BELOW_FLOOR';
      else
        v_salary_state := 'EXPLICIT_COMPATIBLE';
      end if;
    elsif v_o.salary_evidence_class = 'explicit' then
      v_salary_state := 'EXPLICIT_INCOMPLETE_CONFIRM';
    elsif v_o.salary_evidence_class = 'estimated' then
      v_salary_state := 'ESTIMATED_NOT_FACT';
    else
      v_salary_state := 'SALARY_TO_CONFIRM';
    end if;
  end if;

  -- Work model: lista não vazia é tratada como conjunto permitido no V1.
  select count(*) into v_work_models_count from jsonb_array_elements_text(v_p.work_models);
  if v_work_models_count > 0 and v_o.work_model <> 'unknown' then
    select exists(
      select 1 from jsonb_array_elements_text(v_p.work_models) x
      where public.career_normalize_text(x) = public.career_normalize_text(v_o.work_model)
    ) into v_work_match;
    if not v_work_match then
      v_hard_block_reason := coalesce(v_hard_block_reason,'WORK_MODEL_NOT_ALLOWED');
    else
      v_work_points := 10;
      v_total_weight := v_total_weight + 10;
      v_total_points := v_total_points + v_work_points;
    end if;
  elsif v_work_models_count > 0 then
    -- Modelo da vaga desconhecido: não inventar; componente não entra no denominador.
    null;
  end if;

  if v_hard_block_reason is not null then
    v_classification := 'BLOCKED_REQUIREMENT';
    v_breakdown := jsonb_build_object('gate','HARD_REQUIREMENT','reason_code',v_hard_block_reason,'salary_state',v_salary_state);
    v_explanation := jsonb_build_object('message','A oportunidade conflita com uma preferência ou requisito explícito seu.');
    if p_persist then
      insert into public.career_matches(user_id,opportunity_id,engine_version,score,classification,privacy_decision,salary_state,breakdown,explanation_safe)
      values(p_user_id,p_opportunity_id,'v1.0',null,v_classification,v_priv.decision,v_salary_state,v_breakdown,v_explanation)
      on conflict(user_id,opportunity_id,engine_version) do update
      set score=excluded.score,classification=excluded.classification,privacy_decision=excluded.privacy_decision,
          salary_state=excluded.salary_state,breakdown=excluded.breakdown,explanation_safe=excluded.explanation_safe,updated_at=now();
    end if;
    return query select null::numeric,v_classification,v_priv.decision,v_salary_state,v_breakdown,v_explanation;
    return;
  end if;

  -- Cargo-alvo: peso 40.
  select count(*) into v_role_count from jsonb_array_elements_text(v_p.target_roles);
  if v_role_count > 0 then
    select max(similarity(public.career_normalize_text(v_o.title), public.career_normalize_text(x)))
      into v_role_similarity
    from jsonb_array_elements_text(v_p.target_roles) x;
    v_role_similarity := greatest(0, least(1, coalesce(v_role_similarity,0)));
    v_role_points := 40 * v_role_similarity;
    v_total_weight := v_total_weight + 40;
    v_total_points := v_total_points + v_role_points;
  end if;

  -- Competências confirmadas: peso 30, apenas quando ambos os lados possuem dados.
  select count(*) into v_candidate_skills_count
  from public.career_confirmed_facts f
  where f.user_id=p_user_id and f.fact_type='skill' and f.superseded_at is null
    and nullif(public.career_normalize_text(f.fact_value->>'name'),'') is not null;

  select count(*) into v_required_skills_count from jsonb_array_elements_text(v_o.required_skills);

  if v_candidate_skills_count > 0 and v_required_skills_count > 0 then
    select count(*) into v_skill_matches
    from jsonb_array_elements_text(v_o.required_skills) req
    where exists (
      select 1 from public.career_confirmed_facts f
      where f.user_id=p_user_id and f.fact_type='skill' and f.superseded_at is null
        and public.career_normalize_text(f.fact_value->>'name') = public.career_normalize_text(req)
    );
    v_skill_ratio := least(1, v_skill_matches::numeric / v_required_skills_count::numeric);
    v_skill_points := 30 * v_skill_ratio;
    v_total_weight := v_total_weight + 30;
    v_total_points := v_total_points + v_skill_points;
  end if;

  -- Localização: peso 10; remoto não recebe peso artificial.
  select count(*) into v_locations_count from jsonb_array_elements_text(v_p.preferred_locations);
  v_location_known := nullif(trim(coalesce(v_o.city,'') || ' ' || coalesce(v_o.state_code,'')), '') is not null;
  if v_locations_count > 0 and v_o.work_model <> 'remote' and v_location_known then
    select exists(
      select 1 from jsonb_array_elements_text(v_p.preferred_locations) loc
      where public.career_normalize_text(loc) = public.career_normalize_text(trim(coalesce(v_o.city,'') || ' ' || coalesce(v_o.state_code,'')))
         or public.career_normalize_text(loc) = public.career_normalize_text(coalesce(v_o.city,''))
         or public.career_normalize_text(loc) = public.career_normalize_text(coalesce(v_o.state_code,''))
    ) into v_location_match;
    v_location_points := case when v_location_match then 10 else 0 end;
    v_total_weight := v_total_weight + 10;
    v_total_points := v_total_points + v_location_points;
  end if;

  -- Setor: peso 10 quando explicitamente configurado e informado pela vaga.
  select count(*) into v_sectors_count from jsonb_array_elements_text(v_p.preferred_sectors);
  if v_sectors_count > 0 and nullif(public.career_normalize_text(v_o.sector),'') is not null then
    select exists(
      select 1 from jsonb_array_elements_text(v_p.preferred_sectors) s
      where public.career_normalize_text(s) = public.career_normalize_text(v_o.sector)
    ) into v_sector_match;
    v_sector_points := case when v_sector_match then 10 else 0 end;
    v_total_weight := v_total_weight + 10;
    v_total_points := v_total_points + v_sector_points;
  end if;

  if v_total_weight <= 0 then
    v_score := null;
    v_classification := 'PENDING_DATA';
  else
    v_score := round((v_total_points / v_total_weight) * 100, 2);
    if v_score >= v_threshold then
      if v_salary_state in ('SALARY_TO_CONFIRM','ESTIMATED_NOT_FACT','EXPLICIT_INCOMPLETE_CONFIRM') then
        v_classification := 'QUALIFIED_SALARY_CONFIRM';
      else
        v_classification := 'QUALIFIED';
      end if;
    else
      v_classification := 'BELOW_FIT';
    end if;
  end if;

  v_breakdown := jsonb_build_object(
    'threshold',v_threshold,
    'applicable_weight',v_total_weight,
    'role',jsonb_build_object('weight',case when v_role_count>0 then 40 else 0 end,'similarity',v_role_similarity,'points',v_role_points),
    'skills',jsonb_build_object('weight',case when v_candidate_skills_count>0 and v_required_skills_count>0 then 30 else 0 end,'required',v_required_skills_count,'confirmed_candidate_skills',v_candidate_skills_count,'matches',v_skill_matches,'ratio',v_skill_ratio,'points',v_skill_points),
    'work_model',jsonb_build_object('weight',case when v_work_models_count>0 and v_o.work_model<>'unknown' then 10 else 0 end,'matched',v_work_match,'points',v_work_points),
    'location',jsonb_build_object('weight',case when v_locations_count>0 and v_o.work_model<>'remote' and v_location_known then 10 else 0 end,'matched',v_location_match,'points',v_location_points),
    'sector',jsonb_build_object('weight',case when v_sectors_count>0 and nullif(public.career_normalize_text(v_o.sector),'') is not null then 10 else 0 end,'matched',v_sector_match,'points',v_sector_points),
    'salary',jsonb_build_object('evidence_class',v_o.salary_evidence_class,'state',v_salary_state),
    'privacy',jsonb_build_object('decision',v_priv.decision,'reason_code',v_priv.reason_code,'identity_disclosure_required',v_priv.identity_disclosure_required)
  );

  v_explanation := jsonb_build_object(
    'message',case
      when v_classification='QUALIFIED' then 'A oportunidade está aderente às preferências e fatos confirmados do seu perfil.'
      when v_classification='QUALIFIED_SALARY_CONFIRM' then 'A oportunidade parece aderente, mas o salário ainda precisa ser confirmado.'
      when v_classification='BELOW_FIT' then 'A aderência ficou abaixo do limite inicial do Career 360.'
      else 'Ainda faltam dados suficientes para uma recomendação segura.'
    end,
    'identity_disclosure_required',v_priv.identity_disclosure_required
  );

  if p_persist then
    insert into public.career_matches(user_id,opportunity_id,engine_version,score,classification,privacy_decision,salary_state,breakdown,explanation_safe)
    values(p_user_id,p_opportunity_id,'v1.0',v_score,v_classification,v_priv.decision,v_salary_state,v_breakdown,v_explanation)
    on conflict(user_id,opportunity_id,engine_version) do update
    set score=excluded.score,classification=excluded.classification,privacy_decision=excluded.privacy_decision,
        salary_state=excluded.salary_state,breakdown=excluded.breakdown,explanation_safe=excluded.explanation_safe,updated_at=now();
  end if;

  return query select v_score,v_classification,v_priv.decision,v_salary_state,v_breakdown,v_explanation;
end;
$$;

revoke all on function public.career_score_opportunity(uuid,uuid,boolean) from public,anon,authenticated;
grant execute on function public.career_score_opportunity(uuid,uuid,boolean) to service_role;

commit;
