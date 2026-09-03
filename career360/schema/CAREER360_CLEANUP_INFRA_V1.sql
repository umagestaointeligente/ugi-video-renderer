-- LSI Career 360 — Infra de cleanup automático V1
-- O segredo do cron é gerado no banco/Vault; nenhum valor secreto entra no Git.

begin;

create extension if not exists pg_cron;
create extension if not exists pg_net;

-- Gera uma credencial interna apenas se ainda não existir.
do $$
begin
  if not exists (select 1 from vault.secrets where name = 'career_raw_cleanup_cron') then
    perform vault.create_secret(
      encode(gen_random_bytes(32), 'hex'),
      'career_raw_cleanup_cron',
      'Credencial interna do cron para limpeza de currículos brutos do Career 360',
      null
    );
  end if;
end
$$;

create or replace function public.career_validate_internal_secret(
  p_name text,
  p_candidate text
)
returns boolean
language sql
stable
security definer
set search_path = public, vault
as $$
  select exists (
    select 1
    from vault.decrypted_secrets s
    where s.name = p_name
      and s.decrypted_secret = p_candidate
  );
$$;

revoke all on function public.career_validate_internal_secret(text, text) from public, anon, authenticated;
grant execute on function public.career_validate_internal_secret(text, text) to service_role;

commit;
