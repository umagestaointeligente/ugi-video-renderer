-- Career 360 — external provider route registry hardening after live route construction.
-- DML-only control-plane truth update. Components stay paused until provider authorization gates pass.

update public.career_engine_control
set notes_safe = notes_safe || jsonb_build_object(
  'production_branch','career360-production',
  'root_directory','career360/frontend',
  'branch_guard','vercel.json: all branches false; career360-production true',
  'branch_guard_commit','9979cf82b7ec4cc13752ef432c4aeebf5b7ce505',
  'promotion_trigger','.github/career360-production-promote.trigger',
  'promotion_workflow','.github/workflows/career360-production-branch-promote.yml',
  'promotion_mode','GITHUB_FORCE_WITH_LEASE_THEN_OFFICIAL_ALIAS_PIN_GATE',
  'promotion_selftest_run_id',34054221632,
  'promotion_selftest_result','SUCCESS_NOOP_NO_PRODUCTION_MUTATION',
  'primary_route_state','REPO_SIDE_READY_WAITING_ONE_TIME_VERCEL_GIT_LINK',
  'one_time_provider_setup',jsonb_build_array(
    'Connect existing Vercel project prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP to GitHub repository umagestaointeligente/ugi-video-renderer',
    'Set Root Directory to career360/frontend',
    'Set Production Branch to career360-production'
  )
), updated_at=now()
where component='frontend_delivery';

update public.career_engine_control
set notes_safe = notes_safe || jsonb_build_object(
  'probe_user_cleaned',true,
  'probe_mail_cleaned',true,
  'configuration_bug_proven',true,
  'repair_preference','ONE_TIME_DASHBOARD_CHANGE_IF_NO_MANAGEMENT_API_AUTH; DO_NOT_STORE_NEW_PAT_ONLY_FOR_THIS_STATIC_SETTING',
  'required_site_url','https://lsi-career-360.vercel.app/',
  'required_redirect_pattern','https://lsi-career-360.vercel.app/**'
), updated_at=now()
where component='auth_redirect';

update public.career_engine_control
set notes_safe = notes_safe || jsonb_build_object(
  'backend_dispatch_contract','LIVE_VALIDATED',
  'recipient_storage','PGCRYPTO_AES256_VAULT_KEY_HASH_FOR_AUDIT',
  'dispatch_rpc','career_claim_mail_delivery',
  'receipt_rpc','career_record_mail_delivery_receipt_v2',
  'uncertain_rpc','career_mark_mail_delivery_uncertain',
  'legacy_unclaimed_receipt_v1','RETIRED_SERVICE_EXEC_REVOKED',
  'blind_retry_allowed',false,
  'expired_lease_behavior','PERSIST_DELIVERY_UNCERTAIN_RETURN_ZERO_CLAIMS',
  'dispatch_smoke','9_OF_9_PASS_NO_EXTERNAL_SEND',
  'dispatch_smoke_file','career360/tests/mail-delivery-dispatch-lease-v1-smoke.sql'
), updated_at=now()
where component='mail_background_bridge';

update public.career_engine_control
set notes_safe = coalesce(notes_safe,'{}'::jsonb) || jsonb_build_object(
  'required_receipt_route','career_claim_mail_delivery -> provider -> career_record_mail_delivery_receipt_v2',
  'legacy_receipt_v1','RETIRED',
  'blind_retry_allowed',false
), updated_at=now()
where component='mail_delivery';
