-- Career 360 — external user dependency policy V1
-- User constraint: Make and Vercel are valid only when fully operable from inside ChatGPT/app.
-- Any route requiring the user to open/authorize/configure those providers externally is not an admissible production route.

update public.career_engine_control
set notes_safe = coalesce(notes_safe,'{}'::jsonb) || jsonb_build_object(
      'external_user_intervention_allowed', false,
      'route_admissibility_rule', 'IN_APP_AUTONOMOUS_ONLY',
      'prohibited_dependency', 'Any Make/Vercel route requiring user OAuth, login, dashboard configuration, token provisioning, Git-link setup, or provider-side action outside ChatGPT/app',
      'primary_route', 'IN_APP_VERCEL_CONNECTOR_PROJECT_SCOPED_MUTATION_ONLY',
      'fallback_route', null,
      'primary_route_state', 'PAUSED_UNTIL_IN_APP_PROJECT_SCOPED_MUTATION_IS_AVAILABLE_AND_PROVEN',
      'blocker_code', 'EXTERNAL_USER_SETUP_PROHIBITED_AND_CURRENT_IN_APP_MUTATION_NOT_PROVEN',
      'one_time_provider_setup', '[]'::jsonb,
      'fallback_gate', null,
      'vercel_token_provisioning_allowed', false,
      'external_git_link_setup_allowed', false
    ),
    updated_at = now()
where component = 'frontend_delivery';

update public.career_engine_control
set notes_safe = coalesce(notes_safe,'{}'::jsonb) || jsonb_build_object(
      'external_user_intervention_allowed', false,
      'route_admissibility_rule', 'IN_APP_AUTONOMOUS_ONLY',
      'prohibited_dependency', 'Any Make route requiring the user to open an external authorization page or manage Make outside ChatGPT/app',
      'primary_route', 'IN_APP_AUTONOMOUS_MAIL_TRANSPORT_ONLY',
      'manual_fallback', 'CHATGPT_GMAIL_CONNECTOR_EXPLICIT_USER_ACTION_ONLY_NON_BACKGROUND',
      'make_connection_state', 'INVALID_AS_PRODUCTION_ROUTE_REQUIRES_EXTERNAL_USER_OAUTH',
      'gmail_connection_state', 'CHATGPT_GMAIL_CONNECTED_READ_WRITE_FOR_IN_CHAT_ACTIONS',
      'supabase_connection_state', 'CHATGPT_SUPABASE_CONNECTED_FOR_IN_APP_OPERATIONS',
      'make_connection_request_id', null,
      'make_external_oauth_allowed', false,
      'blocker_code', 'BACKGROUND_TRANSPORT_NOT_YET_AVAILABLE_WITHOUT_EXTERNAL_USER_SETUP'
    ),
    updated_at = now()
where component = 'mail_background_bridge';

update public.career_engine_control
set notes_safe = coalesce(notes_safe,'{}'::jsonb) || jsonb_build_object(
      'external_user_intervention_allowed', false,
      'route_admissibility_rule', 'IN_APP_AUTONOMOUS_ONLY',
      'fallback_route', null,
      'repair_preference', 'IN_APP_SUPABASE_CONNECTOR_OR_INTERNAL_AUTH_ADMIN_ROUTE_ONLY',
      'dashboard_manual_change_allowed', false,
      'blocker_code', 'AUTH_REDIRECT_BUG_PROVEN_IN_APP_ADMIN_CONFIG_WRITE_NOT_YET_AVAILABLE'
    ),
    updated_at = now()
where component = 'auth_redirect';

update public.career_engine_control
set notes_safe = coalesce(notes_safe,'{}'::jsonb) || jsonb_build_object(
      'external_user_intervention_allowed', false,
      'route_admissibility_rule', 'IN_APP_AUTONOMOUS_ONLY'
    ),
    updated_at = now()
where component = 'mail_delivery';
