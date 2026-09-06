-- Career 360 — align Role Graph control-plane source truth after validated O*NET 31.0 bulk sync.
-- Metadata-only: no Role Graph concept/alias/relation or matching mutation.

update public.career_engine_control
set notes_safe = jsonb_set(
      coalesce(notes_safe,'{}'::jsonb),
      '{sources,onet}',
      '"live_bulk"'::jsonb,
      true
    ) || jsonb_build_object(
      'onet_version','31.0',
      'onet_mode','diagnostic_evidence_only',
      'onet_auto_promote_to_role_graph',false
    ),
    updated_at = now()
where component='role_graph';
