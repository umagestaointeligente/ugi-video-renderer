create table if not exists public.career_professional_photo_jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  source_media_id uuid not null references public.career_profile_media(id) on delete cascade,
  status text not null default 'planned' check (status in ('planned','generating','preview_ready','accepted','rejected','failed')),
  style_key text not null,
  style_label text not null,
  context_json jsonb not null default '{}'::jsonb,
  prompt_text text not null,
  negative_prompt_text text,
  generated_storage_path text,
  generated_mime_type text,
  failure_code text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  decided_at timestamptz
);

alter table public.career_professional_photo_jobs enable row level security;
drop policy if exists career_professional_photo_jobs_select_own on public.career_professional_photo_jobs;
create policy career_professional_photo_jobs_select_own on public.career_professional_photo_jobs
for select to authenticated using ((select auth.uid()) is not null and (select auth.uid()) = user_id);
revoke insert, update, delete on public.career_professional_photo_jobs from authenticated;
grant select on public.career_professional_photo_jobs to authenticated;
create index if not exists idx_career_prof_photo_jobs_user_created on public.career_professional_photo_jobs(user_id, created_at desc);
create unique index if not exists uq_career_prof_photo_one_active_preview on public.career_professional_photo_jobs(user_id) where status in ('generating','preview_ready');

alter table public.career_profiles
add column if not exists active_professional_photo_job_id uuid references public.career_professional_photo_jobs(id) on delete set null;
create index if not exists idx_career_profiles_active_prof_photo on public.career_profiles(active_professional_photo_job_id) where active_professional_photo_job_id is not null;
