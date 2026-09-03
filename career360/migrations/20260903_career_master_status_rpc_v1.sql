begin;
create or replace function public.career_master_status_v1()
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, public
as $$
declare
  v_uid uuid := auth.uid();
  v_role text;
  v_result jsonb;
begin
  if v_uid is null then raise exception 'AUTH_REQUIRED'; end if;
  select role into v_role from public.career_user_roles where user_id=v_uid;
  if v_role is distinct from 'master' then raise exception 'MASTER_REQUIRED'; end if;

  v_result := jsonb_build_object(
    'product','LSI Career 360',
    'release','Master Pilot 1.0',
    'role','master',
    'privacy_notice','Painel agregado: não retorna currículo, nome, e-mail ou histórico de outro usuário.',
    'aggregates',jsonb_build_object(
      'users',(select count(*) from public.career_user_roles),
      'masters',(select count(*) from public.career_user_roles where role='master'),
      'documents',(select count(*) from public.career_documents),
      'quarantined',(select count(*) from public.career_documents where file_status='quarantined'),
      'rejected',(select count(*) from public.career_documents where file_status='rejected'),
      'drafts',(select count(*) from public.career_profile_drafts),
      'matches',(select count(*) from public.career_matches),
      'qualified',(select count(*) from public.career_matches where classification in ('QUALIFIED','QUALIFIED_SALARY_CONFIRM')),
      'privacy_blocks',(select count(*) from public.career_matches where classification='BLOCKED_PRIVACY'),
      'incidents_open',(select count(*) from public.career_incidents where status in ('open','needs_user')),
      'incidents_external',(select count(*) from public.career_incidents where status='external_block')
    ),
    'gates',jsonb_build_object(
      'dedicated_project','PASS',
      'database_rls','PASS_CORE_AB_TEST',
      'security_advisor','PASS_ZERO_LINTS',
      'private_storage','PASS',
      'raw_retention','PASS_CRON_ACTIVE',
      'deep_parser','PASS_CI_AND_DEPLOYED',
      'privacy_gate','PASS_SYNTHETIC_SCENARIOS',
      'matching_v1','PASS_SYNTHETIC_SCENARIOS_AND_E2E',
      'auth_real_session','PASS_E2E',
      'master_role_bootstrap','PASS_E2E',
      'resume_full_flow','PASS_E2E',
      'raw_file_delete_after_confirmation','PASS_E2E',
      'agent','PASS_E2E',
      'support','PASS_E2E',
      'hosted_app','PASS_HTTP_200',
      'master_pilot','PASS_READY_FOR_MASTER_USE',
      'public_beta','NOT_OPENED_PRODUCT_DECISION'
    ),
    'operations',jsonb_build_object('cleanup_schedule','hourly minute 17','cost_mode','ZERO_CASH','customer_data_in_logs',false)
  );
  return v_result;
end;
$$;
revoke all on function public.career_master_status_v1() from public, anon;
grant execute on function public.career_master_status_v1() to authenticated;
commit;