-- Career 360 — O*NET explicit client deny policies
-- The lookup layer is server-side evidence only. Client roles have grants revoked and RLS rejection policies.

drop policy if exists career_onet_occupations_no_client_access on public.career_onet_occupations;
create policy career_onet_occupations_no_client_access
  on public.career_onet_occupations
  for all
  to anon, authenticated
  using (false)
  with check (false);

drop policy if exists career_onet_job_titles_no_client_access on public.career_onet_job_titles;
create policy career_onet_job_titles_no_client_access
  on public.career_onet_job_titles
  for all
  to anon, authenticated
  using (false)
  with check (false);
