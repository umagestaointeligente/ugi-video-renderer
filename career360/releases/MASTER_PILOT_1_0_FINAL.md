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

## Hardening pós-E2E

O painel mestre deixou de depender de service role dentro da Edge Function.

Arquitetura final:
`JWT DO USUÁRIO -> career-master-status -> career_master_status_v1() -> auth.uid() + role master -> agregados`

A RPC `career_master_status_v1()` é `SECURITY DEFINER`, tem `search_path` fixo, exige role master e não retorna currículo, nome, e-mail ou histórico de outro usuário.

## CI

Última referência antes da finalização:
- Career 360 Parser Tests = SUCCESS;
- Career 360 Prototype Smoke = SUCCESS;
- Career 360 Edge Typecheck = SUCCESS.

## Segurança

Último Security Advisor verificado: zero lints.

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
