-- LSI Career 360 — agendamento de cleanup automático do arquivo bruto V1
-- O comando lê o segredo do Vault em runtime; nenhum segredo é versionado.

begin;

do $$
begin
  if exists (select 1 from cron.job where jobname = 'career_raw_file_cleanup') then
    perform cron.unschedule('career_raw_file_cleanup');
  end if;
end
$$;

select cron.schedule(
  'career_raw_file_cleanup',
  '17 * * * *',
  $cmd$
    select net.http_post(
      url := 'https://nxjdnzdxclszqyqrkwdk.supabase.co/functions/v1/career-document-cleanup',
      body := '{}'::jsonb,
      params := '{}'::jsonb,
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'x-lsi-cron-secret', (
          select decrypted_secret
          from vault.decrypted_secrets
          where name = 'career_raw_cleanup_cron'
          limit 1
        )
      ),
      timeout_milliseconds := 10000
    );
  $cmd$
);

commit;
