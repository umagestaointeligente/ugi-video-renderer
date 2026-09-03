# LSI Career 360 — Master Pilot 1.0 FINAL

Data: 2026-09-03 BRT
Status: `READY_FOR_MASTER_USE`

## Hosted app

`https://nxjdnzdxclszqyqrkwdk.supabase.co/functions/v1/career-app`

HTTP 200 verificado internamente após deploy.

## E2E final

Teste executado com usuário QA criado pelo Supabase Auth real e dados 100% sintéticos.

Resultado:
- auth user created = PASS;
- bootstrap role = master;
- real auth session = PASS;
- document ingest = QUARANTINED;
- deep process = DRAFT_REQUIRES_CONFIRMATION;
- profile confirm = AGENT_READY;
- raw file deleted after confirmation = PASS;
- matching = QUALIFIED_SALARY_CONFIRM;
- score = 100;
- visible opportunities = 1;
- agent intent = opportunities;
- support = resolved;
- master panel = master;
- overall = PASS.

## Cleanup E2E

Após o teste:
- QA users = 0;
- QA opportunities = 0;
- QA master hashes = 0;
- one-time gate removido;
- E2E runner redeployado em modo desativado.

Nenhum dado real de cliente foi usado no E2E.

## Hardening pós-E2E — FINAL

A auditoria executada depois das últimas migrations encontrou dois WARN de funções `SECURITY DEFINER` diretamente executáveis pelo papel `authenticated`.

Eles foram tratados antes da promoção:
- `public.career_master_status_v1()` removida;
- `public.career_score_opportunity_self(uuid, boolean)` removida;
- motor base `career_score_opportunity` permanece sem EXECUTE para authenticated;
- criado `public.career_master_metrics` somente com dados agregados;
- RLS permite leitura desse snapshot apenas quando a role do próprio `auth.uid()` é `master`;
- authenticated não pode escrever no snapshot;
- refresh privilegiado foi movido para `career_private.refresh_master_metrics()` sem EXECUTE para authenticated;
- cron atualiza métricas mestre a cada 5 minutos;
- Edge `career-master-status` usa somente o JWT do usuário + cliente público e não contém service role.

Security Advisor executado novamente após essa alteração: `lints=[]`.

Performance Advisor final contém apenas avisos `INFO` de índices ainda não utilizados em uma base sem carga real; não são findings de segurança nem blockers do piloto.

## CI

Referência final:
- Career 360 Parser Tests = SUCCESS;
- Career 360 Prototype Smoke = SUCCESS;
- Career 360 Edge Typecheck = SUCCESS.

## Segurança

Estado final do Master Pilot:
- Security Advisor = ZERO LINTS;
- Auth real E2E = PASS;
- RLS A/B = PASS;
- bucket privado = PASS;
- raw delete após confirmação = PASS E2E;
- Proteção de Carreira = PASS no escopo do piloto;
- Matching V1 = PASS no escopo do piloto;
- painel mestre = agregados sem PII e protegido por RLS.

## Limites de escopo

Master Pilot 1.0 pronto não significa:
- browser pago já contratado;
- automação irrestrita de ATS;
- bypass de CAPTCHA/MFA;
- Founding Beta 20 automaticamente aberta;
- candidatura automática liberada.

Esses itens são Próximos Degraus e exigem gates próprios.

## Recovery

Em qualquer novo chat:
`Recovery LSI`
