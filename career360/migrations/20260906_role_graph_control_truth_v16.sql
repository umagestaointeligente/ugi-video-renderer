-- LSI Career 360 — Role Graph control-plane truth V16
-- Reconcile stale challenger metadata after the already-proven V3.1 promotion.

update public.career_engine_control
set notes_safe=jsonb_build_object(
      'mode','production_component',
      'feeds_matching','v3.1-rolegraph',
      'normalization','canonical_career_normalize_text_applied',
      'seniority_guard','expanded roles below current rank suppressed unless allow_progression_down=true',
      'balanced_threshold',0.59,
      'user_match_formula','0.85 pair fit + 0.15 search prior',
      'sources',jsonb_build_object(
        'lsi_curated','live_bulk',
        'esco','live_api',
        'cbo','live_bulk',
        'onet','bulk_pending'
      ),
      'rollback_matching','v2.0'
    ),
    updated_at=now()
where component='role_graph'
  and champion_version='v1.1'
  and status='active';

update public.career_engine_control
set notes_safe=jsonb_build_object(
      'mode','production_component',
      'production_engine','v3.1-rolegraph',
      'role_fit_floor',0.55,
      'qualification_threshold',72,
      'promoted',true,
      'rollback','v2.0'
    ),
    updated_at=now()
where component='matching_role_graph'
  and champion_version='v3.1-rolegraph'
  and status='active';
