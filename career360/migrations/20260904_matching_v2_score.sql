-- LSI Career 360 — Matching V2 scorer
-- Reconciled from the promoted Supabase runtime on 2026-09-04.

create or replace function public.career_score_opportunity_v2(
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
security definer
set search_path to 'public', 'extensions'
as $$
declare
  v_o public.career_opportunities%rowtype;
  v_p public.career_preferences%rowtype;
  v_priv record;
  v_target text;
  v_opp_family text;
  v_target_family text;
  v_opp_rank int;
  v_target_rank int;
  v_family_fit numeric;
  v_seniority_fit numeric;
  v_lex numeric;
  v_candidate_role_fit numeric;
  v_best_role_fit numeric := 0;
  v_best_family_fit numeric := 0;
  v_best_seniority_fit numeric := 0;
  v_best_lex numeric := 0;
  v_best_target text := null;
  v_role_points numeric := 0;
  v_skill_points numeric := 0;
  v_sector_points numeric := 0;
  v_location_points numeric := 0;
  v_work_points numeric := 0;
  v_total_points numeric := 0;
  v_applicable_weight numeric := 0;
  v_evidence_weight numeric := 0;
  v_score numeric := null;
  v_confidence numeric := 0;
  v_classification text;
  v_salary_state text := 'NOT_APPLICABLE';
  v_hard_block_reason text := null;
  v_location_known boolean := false;
  v_location_match boolean := false;
  v_work_match boolean := false;
  v_sector_match boolean := false;
  v_candidate_skills_count int := 0;
  v_required_skills_count int := 0;
  v_skill_matches int := 0;
  v_skill_ratio numeric := null;
  v_threshold numeric := 72;
  v_breakdown jsonb;
  v_explanation jsonb;
  v_min_target_rank int := 0;
begin
  if p_user_id is null or p_opportunity_id is null then
    raise exception 'USER_AND_OPPORTUNITY_REQUIRED';
  end if;

  select * into v_o from public.career_opportunities where id=p_opportunity_id;
  if not found then raise exception 'OPPORTUNITY_NOT_FOUND'; end if;

  select * into v_p from public.career_preferences where user_id=p_user_id;
  if not found then
    return query select null::numeric,'PENDING_DATA',null::text,'UNKNOWN',
      jsonb_build_object('reason','PREFERENCES_NOT_FOUND'),
      jsonb_build_object('message','Preferências de carreira ainda não configuradas.');
    return;
  end if;

  if v_o.status <> 'active' or (v_o.expires_at is not null and v_o.expires_at <= now()) then
    v_classification:='EXPIRED';
    v_breakdown:=jsonb_build_object('gate','OPPORTUNITY_EXPIRED','engine','v2.0');
    v_explanation:=jsonb_build_object('message','A oportunidade não está mais ativa.');
    if p_persist then
      insert into public.career_matches(user_id,opportunity_id,engine_version,score,classification,privacy_decision,salary_state,breakdown,explanation_safe)
      values(p_user_id,p_opportunity_id,'v2.0',null,v_classification,null,'UNKNOWN',v_breakdown,v_explanation)
      on conflict(user_id,opportunity_id,engine_version) do update
      set score=excluded.score,classification=excluded.classification,privacy_decision=excluded.privacy_decision,
          salary_state=excluded.salary_state,breakdown=excluded.breakdown,explanation_safe=excluded.explanation_safe,updated_at=now();
    end if;
    return query select null::numeric,v_classification,null::text,'UNKNOWN',v_breakdown,v_explanation;
    return;
  end if;

  select * into v_priv from public.career_privacy_gate(p_user_id,v_o.employer_name) limit 1;
  if v_priv.decision='SILENT_BLOCK' then
    v_classification:='BLOCKED_PRIVACY';
    v_breakdown:=jsonb_build_object('gate','PRIVACY','reason_code',v_priv.reason_code,'engine','v2.0');
    v_explanation:=jsonb_build_object('message','Oportunidade protegida pelas suas regras de privacidade.');
    if p_persist then
      insert into public.career_matches(user_id,opportunity_id,engine_version,score,classification,privacy_decision,salary_state,breakdown,explanation_safe)
      values(p_user_id,p_opportunity_id,'v2.0',null,v_classification,v_priv.decision,'UNKNOWN',v_breakdown,v_explanation)
      on conflict(user_id,opportunity_id,engine_version) do update
      set score=excluded.score,classification=excluded.classification,privacy_decision=excluded.privacy_decision,
          salary_state=excluded.salary_state,breakdown=excluded.breakdown,explanation_safe=excluded.explanation_safe,updated_at=now();
    end if;
    return query select null::numeric,v_classification,v_priv.decision,'UNKNOWN',v_breakdown,v_explanation;
    return;
  end if;

  if v_p.salary_floor_brl is not null then
    if v_o.salary_evidence_class='explicit' and v_o.salary_max is not null then
      if v_o.salary_max < v_p.salary_floor_brl then
        v_hard_block_reason:='EXPLICIT_SALARY_BELOW_FLOOR';
      else
        v_salary_state:='EXPLICIT_COMPATIBLE';
      end if;
    elsif v_o.salary_evidence_class='explicit' then
      v_salary_state:='EXPLICIT_INCOMPLETE_CONFIRM';
    elsif v_o.salary_evidence_class='estimated' then
      v_salary_state:='ESTIMATED_NOT_FACT';
    else
      v_salary_state:='SALARY_TO_CONFIRM';
    end if;
  end if;

  if jsonb_array_length(coalesce(v_p.work_models,'[]'::jsonb))>0 and v_o.work_model<>'unknown' then
    select exists(
      select 1 from jsonb_array_elements_text(v_p.work_models) x
      where public.career_normalize_text(x)=public.career_normalize_text(v_o.work_model)
    ) into v_work_match;
    if not v_work_match then
      v_hard_block_reason:=coalesce(v_hard_block_reason,'WORK_MODEL_NOT_ALLOWED');
    else
      v_work_points:=10; v_total_points:=v_total_points+10; v_applicable_weight:=v_applicable_weight+10; v_evidence_weight:=v_evidence_weight+10;
    end if;
  end if;

  v_location_known := nullif(trim(coalesce(v_o.city,'')||' '||coalesce(v_o.state_code,'')),'') is not null;
  if jsonb_array_length(coalesce(v_p.preferred_locations,'[]'::jsonb))>0 then
    if v_o.work_model='remote' then
      v_location_match:=true; v_location_points:=10; v_total_points:=v_total_points+10; v_applicable_weight:=v_applicable_weight+10; v_evidence_weight:=v_evidence_weight+10;
    elsif v_location_known then
      select exists(
        select 1 from jsonb_array_elements_text(v_p.preferred_locations) loc
        where public.career_normalize_text(trim(coalesce(v_o.city,'')||' '||coalesce(v_o.state_code,''))) like '%'||public.career_normalize_text(loc)||'%'
           or public.career_normalize_text(loc) like '%'||public.career_normalize_text(coalesce(v_o.city,''))||'%'
           or public.career_normalize_text(loc)=public.career_normalize_text(coalesce(v_o.state_code,''))
      ) into v_location_match;
      if not v_location_match then
        v_hard_block_reason:=coalesce(v_hard_block_reason,'LOCATION_NOT_ALLOWED');
      else
        v_location_points:=10; v_total_points:=v_total_points+10; v_applicable_weight:=v_applicable_weight+10; v_evidence_weight:=v_evidence_weight+10;
      end if;
    end if;
  end if;

  if v_hard_block_reason is not null then
    v_classification:='BLOCKED_REQUIREMENT';
    v_breakdown:=jsonb_build_object('gate','HARD_REQUIREMENT','reason_code',v_hard_block_reason,'salary_state',v_salary_state,'engine','v2.0');
    v_explanation:=jsonb_build_object('message','A oportunidade conflita com uma preferência ou requisito explícito seu.');
    if p_persist then
      insert into public.career_matches(user_id,opportunity_id,engine_version,score,classification,privacy_decision,salary_state,breakdown,explanation_safe)
      values(p_user_id,p_opportunity_id,'v2.0',null,v_classification,v_priv.decision,v_salary_state,v_breakdown,v_explanation)
      on conflict(user_id,opportunity_id,engine_version) do update
      set score=excluded.score,classification=excluded.classification,privacy_decision=excluded.privacy_decision,
          salary_state=excluded.salary_state,breakdown=excluded.breakdown,explanation_safe=excluded.explanation_safe,updated_at=now();
    end if;
    return query select null::numeric,v_classification,v_priv.decision,v_salary_state,v_breakdown,v_explanation;
    return;
  end if;

  v_opp_family:=public.career_role_family(coalesce(v_o.title,'')||' '||coalesce(v_o.sector,''));
  v_opp_rank:=public.career_seniority_rank(coalesce(v_o.seniority,'')||' '||coalesce(v_o.title,''));
  select coalesce(min(public.career_seniority_rank(x)),0)
    into v_min_target_rank
  from jsonb_array_elements_text(coalesce(v_p.target_roles,'[]'::jsonb)) x
  where public.career_seniority_rank(x)>0;

  for v_target in select value from jsonb_array_elements_text(coalesce(v_p.target_roles,'[]'::jsonb)) loop
    v_target_family:=public.career_role_family(v_target);
    v_target_rank:=public.career_seniority_rank(v_target);
    v_family_fit:=case
      when v_opp_family<>'unknown' and v_target_family<>'unknown' and v_opp_family=v_target_family then 1
      when v_opp_family='unknown' or v_target_family='unknown' then 0.35
      else 0 end;
    if v_opp_rank>0 and v_target_rank>0 then
      v_seniority_fit:=case abs(v_opp_rank-v_target_rank)
        when 0 then 1 when 1 then 0.65 when 2 then 0.30 when 3 then 0.10 else 0 end;
    else
      v_seniority_fit:=0.35;
    end if;
    v_lex:=greatest(0,least(1,coalesce(similarity(public.career_normalize_text(v_o.title),public.career_normalize_text(v_target)),0)));
    v_candidate_role_fit:=0.5833333333*v_family_fit+0.25*v_seniority_fit+0.1666666667*v_lex;
    if v_candidate_role_fit>v_best_role_fit then
      v_best_role_fit:=v_candidate_role_fit;
      v_best_family_fit:=v_family_fit;
      v_best_seniority_fit:=v_seniority_fit;
      v_best_lex:=v_lex;
      v_best_target:=v_target;
    end if;
  end loop;

  if jsonb_array_length(coalesce(v_p.target_roles,'[]'::jsonb))>0 then
    v_role_points:=60*v_best_role_fit;
    v_total_points:=v_total_points+v_role_points;
    v_applicable_weight:=v_applicable_weight+60;
    v_evidence_weight:=v_evidence_weight+60;
  end if;

  select count(*) into v_candidate_skills_count
  from public.career_confirmed_facts f
  where f.user_id=p_user_id and f.fact_type='skill' and f.superseded_at is null
    and nullif(public.career_normalize_text(f.fact_value->>'name'),'') is not null;

  select count(*) into v_required_skills_count
  from jsonb_array_elements_text(coalesce(v_o.required_skills,'[]'::jsonb));

  if v_candidate_skills_count>0 and v_required_skills_count>0 then
    select count(*) into v_skill_matches
    from jsonb_array_elements_text(v_o.required_skills) req
    where exists(
      select 1 from public.career_confirmed_facts f
      where f.user_id=p_user_id and f.fact_type='skill' and f.superseded_at is null
        and (
          public.career_normalize_text(f.fact_value->>'name')=public.career_normalize_text(req)
          or similarity(public.career_normalize_text(f.fact_value->>'name'),public.career_normalize_text(req))>=0.55
        )
    );
    v_skill_ratio:=least(1,v_skill_matches::numeric/v_required_skills_count::numeric);
    v_skill_points:=20*v_skill_ratio;
    v_total_points:=v_total_points+v_skill_points;
    v_applicable_weight:=v_applicable_weight+20;
    v_evidence_weight:=v_evidence_weight+20;
  end if;

  if jsonb_array_length(coalesce(v_p.preferred_sectors,'[]'::jsonb))>0
     and nullif(public.career_normalize_text(v_o.sector),'') is not null then
    select exists(
      select 1 from jsonb_array_elements_text(v_p.preferred_sectors) s
      where public.career_normalize_text(v_o.sector) like '%'||public.career_normalize_text(s)||'%'
         or public.career_normalize_text(s) like '%'||public.career_normalize_text(v_o.sector)||'%'
    ) into v_sector_match;
    v_sector_points:=case when v_sector_match then 10 else 0 end;
    v_total_points:=v_total_points+v_sector_points;
    v_applicable_weight:=v_applicable_weight+10;
    v_evidence_weight:=v_evidence_weight+10;
  end if;

  if v_applicable_weight<=0 then
    v_score:=null;
    v_classification:='PENDING_DATA';
  else
    v_score:=round((v_total_points/v_applicable_weight)*100,2);
    v_confidence:=least(100,v_evidence_weight);
    if v_best_family_fit<1 and v_best_role_fit<0.65 then
      v_classification:='BELOW_FIT';
    elsif v_opp_rank>0 and v_min_target_rank>0 and v_opp_rank<v_min_target_rank then
      v_classification:='BELOW_FIT';
    elsif v_score>=v_threshold and v_confidence>=60 then
      if v_salary_state in ('SALARY_TO_CONFIRM','ESTIMATED_NOT_FACT','EXPLICIT_INCOMPLETE_CONFIRM') then
        v_classification:='QUALIFIED_SALARY_CONFIRM';
      else
        v_classification:='QUALIFIED';
      end if;
    elsif v_score>=v_threshold and v_confidence<60 then
      v_classification:='PENDING_EVIDENCE';
    else
      v_classification:='BELOW_FIT';
    end if;
  end if;

  v_breakdown:=jsonb_build_object(
    'engine','v2.0','threshold',v_threshold,'confidence',v_confidence,'applicable_weight',v_applicable_weight,
    'role',jsonb_build_object('weight',60,'best_target',v_best_target,'opportunity_family',v_opp_family,'family_fit',round(v_best_family_fit*100,1),'opportunity_seniority_rank',v_opp_rank,'seniority_fit',round(v_best_seniority_fit*100,1),'lexical_fit',round(v_best_lex*100,1),'combined_fit',round(v_best_role_fit*100,1),'points',round(v_role_points,2)),
    'skills',jsonb_build_object('weight',case when v_required_skills_count>0 and v_candidate_skills_count>0 then 20 else 0 end,'required',v_required_skills_count,'candidate_confirmed',v_candidate_skills_count,'matches',v_skill_matches,'ratio',v_skill_ratio,'points',v_skill_points),
    'location',jsonb_build_object('weight',case when jsonb_array_length(coalesce(v_p.preferred_locations,'[]'::jsonb))>0 and (v_o.work_model='remote' or v_location_known) then 10 else 0 end,'matched',v_location_match,'points',v_location_points),
    'work_model',jsonb_build_object('weight',case when jsonb_array_length(coalesce(v_p.work_models,'[]'::jsonb))>0 and v_o.work_model<>'unknown' then 10 else 0 end,'matched',v_work_match,'points',v_work_points),
    'sector',jsonb_build_object('weight',case when jsonb_array_length(coalesce(v_p.preferred_sectors,'[]'::jsonb))>0 and nullif(public.career_normalize_text(v_o.sector),'') is not null then 10 else 0 end,'matched',v_sector_match,'points',v_sector_points),
    'salary',jsonb_build_object('evidence_class',v_o.salary_evidence_class,'state',v_salary_state),
    'privacy',jsonb_build_object('decision',v_priv.decision,'reason_code',v_priv.reason_code,'identity_disclosure_required',v_priv.identity_disclosure_required)
  );

  v_explanation:=jsonb_build_object(
    'message',case
      when v_classification='QUALIFIED' then 'A oportunidade está aderente ao cargo-alvo, senioridade e requisitos confirmados.'
      when v_classification='QUALIFIED_SALARY_CONFIRM' then 'A oportunidade está aderente, mas o salário ainda precisa ser confirmado.'
      when v_classification='PENDING_EVIDENCE' then 'O cargo parece aderente, mas ainda faltam evidências suficientes para recomendar com segurança.'
      when v_classification='BELOW_FIT' then 'A oportunidade ficou abaixo do nível de aderência definido para seu perfil.'
      else 'Ainda faltam dados suficientes para uma recomendação segura.' end,
    'best_target_role',v_best_target,
    'role_family',v_opp_family,
    'identity_disclosure_required',v_priv.identity_disclosure_required
  );

  if p_persist then
    insert into public.career_matches(user_id,opportunity_id,engine_version,score,classification,privacy_decision,salary_state,breakdown,explanation_safe)
    values(p_user_id,p_opportunity_id,'v2.0',v_score,v_classification,v_priv.decision,v_salary_state,v_breakdown,v_explanation)
    on conflict(user_id,opportunity_id,engine_version) do update
    set score=excluded.score,classification=excluded.classification,privacy_decision=excluded.privacy_decision,
        salary_state=excluded.salary_state,breakdown=excluded.breakdown,explanation_safe=excluded.explanation_safe,updated_at=now();
  end if;

  return query select v_score,v_classification,v_priv.decision,v_salary_state,v_breakdown,v_explanation;
end;
$$;

revoke all on function public.career_score_opportunity_v2(uuid,uuid,boolean) from public, anon, authenticated;
grant execute on function public.career_score_opportunity_v2(uuid,uuid,boolean) to service_role;
