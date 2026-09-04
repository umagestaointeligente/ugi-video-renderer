do $$
begin
  if not exists (select 1 from vault.decrypted_secrets where name='career_proactive_digest_cron') then
    perform vault.create_secret(encode(extensions.gen_random_bytes(32),'hex'),'career_proactive_digest_cron','Career 360 proactive digest cron secret');
  end if;
end $$;

create or replace function public.career_validate_proactive_cron_secret(p_secret text)
returns boolean language sql security definer
set search_path to 'pg_catalog','public','extensions','vault'
as $$
  select p_secret is not null and exists (
    select 1 from vault.decrypted_secrets s
    where s.name='career_proactive_digest_cron'
      and encode(extensions.digest(p_secret,'sha256'),'hex') = encode(extensions.digest(s.decrypted_secret,'sha256'),'hex')
  );
$$;
revoke all on function public.career_validate_proactive_cron_secret(text) from public,anon,authenticated;
grant execute on function public.career_validate_proactive_cron_secret(text) to service_role;

do $$
declare v_jobid bigint;
begin
  select jobid into v_jobid from cron.job where jobname='career-proactive-digest' limit 1;
  if v_jobid is not null then perform cron.unschedule(v_jobid); end if;
  perform cron.schedule('career-proactive-digest','7 * * * *',$cmd$
    select net.http_post(
      url := 'https://nxjdnzdxclszqyqrkwdk.supabase.co/functions/v1/career-proactive-digest',
      body := '{}'::jsonb,
      params := '{}'::jsonb,
      headers := jsonb_build_object('Content-Type','application/json','x-lsi-proactive-secret',(select decrypted_secret from vault.decrypted_secrets where name='career_proactive_digest_cron' limit 1)),
      timeout_milliseconds := 30000
    );
  $cmd$);
end $$;