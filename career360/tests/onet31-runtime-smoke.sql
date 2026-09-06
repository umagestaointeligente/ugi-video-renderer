-- Career 360 — O*NET 31.0 runtime smoke
-- Read-only assertions against live runtime state.

DO $$
DECLARE
  v_occ integer;
  v_titles integer;
  v_source_status text;
  v_source_version text;
  v_auto_promote boolean;
  v_match_type text;
  v_match_score numeric;
  v_rls_enabled integer;
  v_public_tables integer;
  v_anon_exec boolean;
  v_auth_exec boolean;
  v_service_exec boolean;
BEGIN
  SELECT count(*) INTO v_occ FROM public.career_onet_occupations;
  SELECT count(*) INTO v_titles FROM public.career_onet_job_titles;
  IF v_occ <> 1016 THEN RAISE EXCEPTION 'ONET_OCCUPATIONS_EXPECTED_1016_GOT_%', v_occ; END IF;
  IF v_titles <> 54229 THEN RAISE EXCEPTION 'ONET_JOB_TITLES_EXPECTED_54229_GOT_%', v_titles; END IF;

  SELECT integration_status,source_version,coalesce((notes_safe->>'auto_promote_to_role_graph')::boolean,true)
    INTO v_source_status,v_source_version,v_auto_promote
  FROM public.career_role_taxonomy_sources WHERE source_key='onet';
  IF v_source_status <> 'live_bulk' THEN RAISE EXCEPTION 'ONET_SOURCE_NOT_LIVE_BULK_%',v_source_status; END IF;
  IF v_source_version <> '31.0' THEN RAISE EXCEPTION 'ONET_SOURCE_VERSION_UNEXPECTED_%',v_source_version; END IF;
  IF v_auto_promote THEN RAISE EXCEPTION 'ONET_AUTO_PROMOTION_MUST_BE_FALSE'; END IF;

  SELECT match_type,match_score INTO v_match_type,v_match_score
  FROM public.career_onet_search('category manager',5)
  ORDER BY match_score DESC,match_type
  LIMIT 1;
  IF v_match_type <> 'exact_job_title' OR v_match_score <> 1.000 THEN
    RAISE EXCEPTION 'ONET_LOOKUP_EXACT_GATE_FAILED type=% score=%',v_match_type,v_match_score;
  END IF;

  SELECT count(*) filter(where c.relrowsecurity),count(*)
    INTO v_rls_enabled,v_public_tables
  FROM pg_class c join pg_namespace n on n.oid=c.relnamespace
  WHERE n.nspname='public' and c.relkind='r';
  IF v_rls_enabled <> v_public_tables THEN
    RAISE EXCEPTION 'PUBLIC_RLS_GAP enabled=% total=%',v_rls_enabled,v_public_tables;
  END IF;

  SELECT
    has_function_privilege('anon','public.career_onet_search(text,integer)','EXECUTE'),
    has_function_privilege('authenticated','public.career_onet_search(text,integer)','EXECUTE'),
    has_function_privilege('service_role','public.career_onet_search(text,integer)','EXECUTE')
  INTO v_anon_exec,v_auth_exec,v_service_exec;
  IF v_anon_exec OR v_auth_exec OR NOT v_service_exec THEN
    RAISE EXCEPTION 'ONET_LOOKUP_ACL_FAILED anon=% auth=% service=%',v_anon_exec,v_auth_exec,v_service_exec;
  END IF;

  RAISE NOTICE 'ONET31_RUNTIME_SMOKE=PASS occupations=% titles=% rls=%/%',v_occ,v_titles,v_rls_enabled,v_public_tables;
END $$;
