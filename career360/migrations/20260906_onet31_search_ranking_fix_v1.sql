-- O*NET lookup ranking fix: deduplicate first, then rank globally by match quality.

create or replace function public.career_onet_search(
  p_query text,
  p_limit integer default 12
)
returns table(
  onetsoc_code text,
  occupation_title text,
  job_title text,
  short_title text,
  match_score numeric,
  match_type text,
  source_version text
)
language sql
stable
security definer
set search_path = public, extensions
as $$
  with q as (
    select public.career_normalize_text(coalesce(p_query,'')) n,
           greatest(1, least(coalesce(p_limit,12),50)) lim
  ), exacts as (
    select jt.onetsoc_code,
           jt.occupation_title,
           jt.job_title,
           jt.short_title,
           1.000::numeric match_score,
           'exact_job_title'::text match_type,
           jt.source_version,
           1 ord
    from public.career_onet_job_titles jt,q
    where q.n<>'' and jt.normalized_job_title=q.n
    union all
    select o.onetsoc_code,
           o.title,
           o.title,
           null::text,
           1.000::numeric,
           'exact_occupation_title'::text,
           o.source_version,
           1
    from public.career_onet_occupations o,q
    where q.n<>'' and o.normalized_title=q.n
  ), fuzzy as (
    select jt.onetsoc_code,
           jt.occupation_title,
           jt.job_title,
           jt.short_title,
           round(greatest(
             similarity(jt.normalized_job_title,q.n),
             similarity(public.career_normalize_text(jt.occupation_title),q.n)
           )::numeric,3) match_score,
           'fuzzy_title'::text match_type,
           jt.source_version,
           2 ord
    from public.career_onet_job_titles jt,q
    where q.n<>''
      and (jt.normalized_job_title % q.n or public.career_normalize_text(jt.occupation_title) % q.n)
      and greatest(
        similarity(jt.normalized_job_title,q.n),
        similarity(public.career_normalize_text(jt.occupation_title),q.n)
      ) >= 0.45
  ), combined as (
    select * from exacts
    union all
    select * from fuzzy
  ), dedup as (
    select distinct on(c.onetsoc_code, public.career_normalize_text(c.job_title))
           c.*
    from combined c
    order by c.onetsoc_code,
             public.career_normalize_text(c.job_title),
             c.ord,
             c.match_score desc
  )
  select d.onetsoc_code,d.occupation_title,d.job_title,d.short_title,d.match_score,d.match_type,d.source_version
  from dedup d,q
  order by d.ord,d.match_score desc,d.job_title,d.onetsoc_code
  limit (select lim from q);
$$;

revoke all on function public.career_onet_search(text,integer) from public, anon, authenticated;
grant execute on function public.career_onet_search(text,integer) to service_role;
