begin;

revoke all on function public.career_score_opportunity(uuid, uuid, boolean) from public, anon, authenticated;
grant execute on function public.career_score_opportunity(uuid, uuid, boolean) to service_role;

revoke all on function public.career_privacy_gate(uuid, text) from public, anon, authenticated;
grant execute on function public.career_privacy_gate(uuid, text) to service_role;

create or replace function public.career_score_opportunity_self(
  p_opportunity_id uuid,
  p_persist boolean default true
)
returns table(
  score numeric,
  classification text,
  privacy_decision text,
  salary_state text,
  breakdown jsonb,
  explanation_safe jsonb
)
language sql
volatile
security definer
set search_path = pg_catalog, public
as $$
  select *
  from public.career_score_opportunity((select auth.uid()), p_opportunity_id, p_persist)
  where (select auth.uid()) is not null;
$$;

revoke all on function public.career_score_opportunity_self(uuid, boolean) from public, anon;
grant execute on function public.career_score_opportunity_self(uuid, boolean) to authenticated;

commit;
