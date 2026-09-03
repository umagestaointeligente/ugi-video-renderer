-- LSI Career 360 — hardening de extensões V1
-- Segue recomendação Supabase: extensões relocáveis em schema extensions.

begin;

-- Não reinstalar pg_net se houver request ainda na fila.
do $$
begin
  if exists (select 1 from net.http_request_queue) then
    raise exception 'PG_NET_QUEUE_NOT_EMPTY';
  end if;
end
$$;

-- pg_trgm é relocável.
alter extension pg_trgm set schema extensions;

-- O matcher usa similarity() do pg_trgm em runtime.
alter function public.career_score_opportunity(uuid, uuid, boolean)
  set search_path = public, extensions;

-- pg_net não é relocável via ALTER; reinstalar no schema recomendado.
drop extension pg_net;
create extension pg_net with schema extensions;

commit;
