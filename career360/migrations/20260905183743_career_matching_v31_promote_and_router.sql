-- Mirror of the live Supabase migration applied at 2026-09-05 18:37:43 UTC.
-- Source of truth recovered from supabase_migrations.schema_migrations.
-- V3.1 becomes matching champion; V2.0 remains rollback.

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
security definer
set search_path to 'public','extensions'
as $$
declare v_engine text;
begin
  select champion_version into v_engine
  from public.career_engine_control
  where component='matching' and status='active';

  v_engine:=coalesce(v_engine,'v2.0');

  if v_engine='v3.1-rolegraph' then
    return query select * from public.career_score_opportunity_v3(p_user_id,p_opportunity_id,p_persist);
  elsif v_engine='v2.0' then
    return query select * from public.career_score_opportunity_v2(p_user_id,p_opportunity_id,p_persist);
  else
    return query select * from public.career_score_opportunity_v2(p_user_id,p_opportunity_id,p_persist);
  end if;
end;
$$;

revoke all on function public.career_score_opportunity(uuid,uuid,boolean) from public,anon,authenticated;
grant execute on function public.career_score_opportunity(uuid,uuid,boolean) to service_role;

update public.career_engine_control
set champion_version='v3.1-rolegraph',
    rollback_version='v2.0',
    status='active',
    notes_safe=jsonb_build_object(
      'promotion_reason','role graph + scope + seniority synthetic QA passed; live corpus no regression',
      'synthetic_positive_cases',7,
      'synthetic_negative_hard_gate_cases',4,
      'live_corpus_size',57,
      'live_class_changes_pre_promotion',0,
      'qualification_threshold',72,
      'role_fit_floor',0.55,
      'rollback','v2.0'
    ),
    updated_at=now()
where component='matching';

update public.career_engine_control
set champion_version='v1.1',
    status='active',
    notes_safe=coalesce(notes_safe,'{}'::jsonb)||'{"promotion":"role graph now feeds matching v3.1","rollback_matching":"v2.0"}'::jsonb,
    updated_at=now()
where component='role_graph';

update public.career_engine_control
set champion_version='v3.1-rolegraph',
    rollback_version='v2.0',
    status='active',
    notes_safe=coalesce(notes_safe,'{}'::jsonb)||'{"promoted":true,"production_engine":"v3.1-rolegraph"}'::jsonb,
    updated_at=now()
where component='matching_role_graph';
