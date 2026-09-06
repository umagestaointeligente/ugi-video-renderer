-- LSI Career 360 — Follow-up Scheduler V1 advisor hardening
-- Fixes the two structural findings introduced by the scheduler migration.

create index if not exists idx_career_followups_application_id
  on public.career_followups(application_id);

drop policy if exists career_followups_select_own on public.career_followups;
create policy career_followups_select_own
  on public.career_followups
  for select
  to authenticated
  using ((select auth.uid()) = user_id);
