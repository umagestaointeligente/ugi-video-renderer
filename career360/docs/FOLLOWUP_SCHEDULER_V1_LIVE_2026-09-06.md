# LSI Career 360 — Follow-up Scheduler V1 LIVE

Data: 2026-09-06 BRT

## Estado

`FOLLOWUP_SCHEDULER_V1=LIVE`
`FOLLOWUP_DELIVERY_SIDE_EFFECTS=NONE`
`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`
`MAIL_DELIVERY_CONTROL=PAUSED`

## O que está LIVE

O scheduler registra e reavalia uma intenção de follow-up com `due_at` explícito. Ele não escolhe prazo por conta própria, não cria candidatura, não cria e-mail e não envia mensagem.

A função `career_schedule_followup` aceita apenas candidatura `status='applied'` com `applied_at` e `external_application_ref_hash` já presentes. A função é `SECURITY DEFINER`, possui `search_path=public` e `EXECUTE` somente para `service_role`.

A função `career_process_due_followups` avalia itens vencidos e aplica, em ordem:
1. candidatura ainda aguardando resposta;
2. `allow_followup_draft` do usuário;
3. capability `career_engine_control.mail_delivery`;
4. apenas se ambos passarem, estado `due_ready_for_orchestration`.

Mesmo no estado ready, V1 não cria `career_mail_actions` e não envia mensagem.

## Control plane

`followup_scheduler = v1.0 / active`

`mail_delivery = none / paused`

O segundo estado é deliberado enquanto `MAIL_DELIVERY_CONNECTOR=NOT_LIVE`.

## Cron

Job: `career-followup-evaluator`

Job ID observado: `5`

Schedule: `23,53 * * * *`

Executor: `postgres`

Command: `select public.career_process_due_followups(100);`

## Segurança e RLS

Tabela `career_followups`:
- RLS habilitado;
- usuário autenticado possui apenas SELECT da própria linha;
- policy usa `(select auth.uid()) = user_id`;
- writes permanecem service-only;
- FK `application_id` possui índice de cobertura.

RPCs:
- `career_schedule_followup`: service-role only;
- `career_process_due_followups`: service-role only;
- PUBLIC/anon/authenticated sem EXECUTE.

## QA transacional

Smoke funcional validado dentro de `BEGIN/ROLLBACK`:
- schedule inicial;
- replay idempotente;
- gate de permissão;
- gate de connector;
- ready gate;
- cancelamento após progresso externo da candidatura;
- rejeição de candidatura não `applied`;
- zero criação de `career_mail_actions`;
- estado final `cancelled / APPLICATION_NO_LONGER_WAITING_RESPONSE`.

Smoke permanente:
`career360/tests/followup-scheduler-v1-smoke.sql`

Commit do smoke:
`458191d7e36571f9a2f1eebb0506fea36bab1d72`

Após a execução do smoke permanente, readback confirmou:
- `career_applications=0`;
- `career_followups=0`;
- `career_mail_actions=0`.

Evaluator em banco vazio:
`(scanned=0, ready=0, waiting_permission=0, waiting_connector=0, cancelled=0)`.

## Advisor hardening

Migration inicial:
`career360/migrations/20260906_followup_scheduler_v1.sql`
commit `5c26f83527e372b21ce77950fbdb196ce90fa196`.

Hardening posterior:
`career360/migrations/20260906_followup_scheduler_v1_advisor_hardening.sql`
commit `295c21f86b7b89cfb2694465e848030c3634d5be`.

O hardening corrigiu:
- FK `career_followups.application_id` sem índice;
- policy RLS com `auth.uid()` sem initplan otimizado.

Advisor pós-hardening:
- Security: somente `auth_leaked_password_protection` WARN conhecido do plano atual;
- Performance: somente INFO `unused_index`; nenhum WARN estrutural novo.

## Regra de verdade

`DUE != DRAFTED`
`DRAFTED != APPROVED`
`APPROVED != SENT`
`SENT REQUIRES PROVIDER RECEIPT`

O scheduler V1 encerra sua responsabilidade em orquestração/pendência. Qualquer envio futuro depende do connector de delivery, das permissões do usuário e dos receipt guards já LIVE.
