-- Career 360 — external provider route registry V1
-- Uses the existing career_engine_control plane. No parallel control table.
-- Runtime truth beats documentation; routes remain fail-closed until their live evidence gates pass.

insert into public.career_engine_control(component,champion_version,rollback_version,status,notes_safe,updated_at)
values
(
  'frontend_delivery',
  'v1-vercel-official-project',
  'v14-production',
  'paused',
  jsonb_build_object(
    'purpose','deterministic delivery of the Career 360 frontend to the existing official Vercel project',
    'official_team_id','team_ZJys00FTE2kK9yVtsqH5fHyF',
    'official_project_id','prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP',
    'official_url','https://lsi-career-360.vercel.app/',
    'current_production_deployment','dpl_98eN1wuVyk4wQmnYpG2jjsZ1ZazU',
    'current_live_frontend','v14',
    'candidate_frontend','v16',
    'primary_route','VERCEL_GITHUB_INTEGRATION_EXISTING_PROJECT_ROOT_CAREER360_FRONTEND',
    'primary_route_state','ONE_TIME_LINK_REQUIRED_NOT_ACTIVE',
    'fallback_route','GITHUB_PROJECT_SCOPED_PREVIEW_PROMOTE_WORKFLOW',
    'fallback_artifact','.github/workflows/career360-vercel-deploy.yml',
    'fallback_gate','VERCEL_TOKEN_INTENTIONALLY_PROVISIONED',
    'vercel_token_present',false,
    'github_vercel_integration_present',false,
    'unscoped_deploy_allowed',false,
    'blocker_code','NO_PROJECT_SCOPED_MUTATION_CREDENTIAL_OR_GIT_LINK',
    'success_evidence','official alias HTTP 200 + app-k/app-l/app-m immutable pins + truthful auth copy',
    'rollback','keep/promote last verified V14 production deployment; never mutate another Vercel project',
    'debug_order',jsonb_build_array('career_engine_control.frontend_delivery','.github/workflows/career360-vercel-deploy.yml','Vercel project prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP','official alias HTTP readback')
  ),
  now()
),
(
  'auth_redirect',
  'v1-production-email-confirmation',
  'localhost-default',
  'paused',
  jsonb_build_object(
    'purpose','email confirmation returns the user to the official Career 360 URL',
    'requested_redirect','https://lsi-career-360.vercel.app/?email-confirmado=1',
    'observed_redirect','http://localhost:3000',
    'primary_route','SUPABASE_MANAGEMENT_API_AUTH_CONFIG_PATCH',
    'primary_route_scope','PATCH_ONLY_SITE_URL_AND_URI_ALLOW_LIST_PRESERVE_OTHER_CONFIG',
    'fallback_route','ONE_TIME_SUPABASE_DASHBOARD_AUTH_URL_CONFIGURATION',
    'supabase_access_token_present',false,
    'connector_management_auth_config_write_available',false,
    'blocker_code','PRODUCTION_REDIRECT_REJECTED_AND_MANAGEMENT_AUTH_NOT_AUTHORIZED',
    'blackbox_probe_request_id',235,
    'blackbox_probe_result','SIGNUP_200_CONFIRMATION_EMAIL_REDIRECTED_TO_LOCALHOST',
    'success_evidence','fresh disposable signup confirmation link contains https://lsi-career-360.vercel.app/?email-confirmado=1 then test identity is deleted',
    'rollback','restore previous Site URL/allowlist snapshot only if production confirmation breaks',
    'debug_order',jsonb_build_array('career_engine_control.auth_redirect','frontend app-a.js APP constant','Supabase Auth Site URL + Redirect URLs','black-box signup confirmation email')
  ),
  now()
),
(
  'mail_background_bridge',
  'v1-make-gmail-supabase',
  null,
  'paused',
  jsonb_build_object(
    'purpose','background outbound/inbound Career 360 mail with provider receipts persisted in Supabase',
    'canonical_mailbox','umagestaointeligente@gmail.com',
    'mailbox_identity','Uma Gestao Inteligente',
    'mailbox_isolation',jsonb_build_array('Career 360','Career 360/Outbound','Career 360/Replies'),
    'primary_route','MAKE_PRIVATE_SPACE_GMAIL_TO_SUPABASE',
    'make_team_id',2782728,
    'make_connection_request_id','46eb6d7b-45bc-4901-9c24-8147c8ef4f13',
    'make_connection_state','PENDING_USER_OAUTH',
    'gmail_connection_state','pending',
    'supabase_connection_state','pending',
    'outbound_flow','permission gate -> Gmail send -> provider message/thread receipt -> career_record_mail_delivery_receipt -> only then SENT',
    'inbound_flow','Gmail watch -> known Career thread/recruiter filter -> career_record_inbound_mail_event -> milestone evaluation',
    'manual_fallback','CHATGPT_GMAIL_CONNECTOR_EXPLICIT_USER_ACTION_ONLY_NON_BACKGROUND',
    'manual_fallback_is_champion',false,
    'delivery_side_effects_live',false,
    'permission_source','career_action_permissions',
    'success_evidence','Make Gmail/Supabase connection ids + scenario active + real controlled delivery receipt + real controlled inbound receipt',
    'rollback','deactivate Make scenarios; keep receipt ledger; mail_delivery remains paused',
    'debug_order',jsonb_build_array('career_engine_control.mail_background_bridge','Make scenario execution','Gmail provider id/thread id','Supabase receipt RPC/result','career_mail_actions/application state')
  ),
  now()
)
on conflict(component) do update set
  champion_version=excluded.champion_version,
  rollback_version=excluded.rollback_version,
  status=excluded.status,
  notes_safe=excluded.notes_safe,
  updated_at=excluded.updated_at;
