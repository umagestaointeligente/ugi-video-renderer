# LSI Career 360 — Proactive Agent V12

Data: 2026-09-04 BRT
Status: BACKEND LIVE / CRON LIVE / IN-APP UI VERSIONED NOT YET PROMOTED / MAIL DELIVERY CONNECTOR NOT LIVE

## Objetivo

Transformar o Career 360 de agente reativo em agente contínuo:

`PESQUISAR -> ANALISAR -> AGIR -> REGISTRAR -> ACOMPANHAR -> DETECTAR MUDANÇA -> AVISAR -> CONTINUAR`

Princípio:
`O CAREER NÃO DEPENDE DO USUÁRIO ABRIR O CHAT PARA CONTINUAR TRABALHANDO.`

## Componentes V12

### Career Activity Ledger — LIVE
Tabela `career_activity_ledger`.
Registra eventos relevantes de:
- oportunidades qualificadas;
- candidatura preparada/aplicada/atualizada;
- resposta de recrutador/empresa;
- entrevista;
- oferta/contratação;
- decisões de e-mail;
- digest gerado.

### Digest Engine — LIVE
Edge `career-proactive-digest`.

Cadências suportadas:
- 4h;
- 6h;
- 8h;
- 12h.

O cron roda uma vez por hora e apenas processa usuários cujo `next_digest_at` venceu.

Job:
`career-proactive-digest`
Schedule:
`7 * * * *`

Conta piloto atual:
- `plan_key=pilot`;
- `cadence_hours=4`.

QA real:
- primeiro ciclo forçado retornou HTTP 200;
- processou 1 usuário;
- gerou 1 digest;
- resumo: 1 oportunidade analisada / 0 qualificada no período;
- segundo ciclo imediatamente em seguida processou 0 usuários, comprovando trava de cadência.

### Digest Preferences — LIVE
Tabela `career_digest_preferences`.

Campos principais:
- `plan_key`;
- `cadence_hours`;
- `timezone`;
- in-app on/off;
- email on/off;
- critical immediate;
- last/next digest.

A camada de planos pode definir a cadência sem alterar FIT ou qualidade do matching.

### Notifications — LIVE
Tabela `career_notifications`.
Tipos:
- digest;
- critical;
- action_required;
- info.

### Applications — LIVE FOUNDATION
Tabela `career_applications`.
Estados:
`considered -> draft_ready -> awaiting_user -> applied -> recruiter_reply -> interview_pending -> interview_confirmed -> finalist -> offer -> hired`

Também suporta rejected/withdrawn/closed.

Mudança de estágio gera evento no Ledger automaticamente.
`awaiting_user` gera notificação `action_required`.

QA transacional com rollback:
- 1 evento de Ledger;
- 1 notificação action_required;
- 0 dados QA persistidos.

### Mail Actions — LIVE FOUNDATION
Tabela `career_mail_actions`.

Armazena metadados minimizados e seguros:
- referência externa hash;
- remetente de exibição;
- assunto seguro;
- resumo;
- resposta sugerida;
- decisão/status;
- criticidade;
- categoria sensível.

Não é repositório de corpo bruto de e-mail.

Mensagem crítica gera notificação imediata via trigger.

QA transacional com rollback:
- 1 evento de Ledger;
- 1 alerta crítico;
- 0 dados QA persistidos.

### Proactive Status — LIVE
Edge `career-proactive-status`, JWT obrigatório.

Retorna em uma única leitura:
- preferência/cadência;
- último digest;
- notificações;
- unread count;
- application counts;
- ações de e-mail pendentes;
- critical/action-required count.

Suporta `mark_read` para notificações próprias.

### Mail Autonomy Policy — LIVE
Reutiliza `career_action_permissions`.

Modos:
- `suggestion`;
- `one_tap`;
- `controlled_autopilot`.

Permissões adicionais:
- inbox monitoring;
- draft de resposta;
- envio de resposta;
- draft de follow-up;
- envio de follow-up;
- auto-send de acknowledgement simples;
- auto-send de disponibilidade simples;
- auto-send de follow-up.

Hard rule:
`always_confirm_sensitive_email = true`.

Categorias sensíveis incluem no gate:
- salary;
- offer;
- documents;
- identity;
- interview_commitment;
- legal.

### Mail Decision — LIVE
Edge `career-mail-decision`, JWT obrigatório.

Ações:
- `get_policy`;
- `set_policy`;
- `decide` com approve/copy/dismiss.

`approve` registra autorização. NÃO significa envio.

Estado explícito:
`MAIL_DECISION=LIVE`
`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`

Nenhuma mensagem pode receber status `sent` apenas porque foi aprovada. Um conector autenticado de entrega precisa existir e produzir evidência real.

## UI V12

Arquivo versionado:
`career360/frontend/app-i.js`

Prevê na Minha Página:
- card `Atualizações do seu agente`;
- cadência;
- última/próxima atualização;
- analisadas/qualificadas/candidaturas/respostas;
- alertas críticos;
- action required;
- badge no Meu Agente;
- `Atualizar agora`.

Status:
`PROACTIVE_UI=VERSIONED_NOT_YET_PROMOTED`

Não declarar LIVE até novo bundle Vercel carregar `app-i.js` no domínio oficial e passar validação.

## Segurança

RLS ativo em todas as novas tabelas.
Cliente lê apenas dados próprios.
Tabelas de Ledger, Applications, Mail Actions e Digest Runs não aceitam escrita direta do cliente.
Notifications permitem somente update do próprio usuário para leitura/dispensa.

Security Advisor pós-DDL:
- nenhum novo lint estrutural de RLS;
- permanece apenas WARN conhecido `auth_leaked_password_protection` desativado.

## Regra comercial

Diferença entre planos pode alterar cadência do acompanhamento, nunca a qualidade do FIT.

Exemplo de entitlement:
- 12h;
- 8h;
- 6h;
- 4h.

Os nomes comerciais dos planos ainda não ficam fixados por esta release.

## Próximos passos

1. promover `app-i.js` no bundle Vercel oficial;
2. validar card proativo autenticado no Android;
3. conectar um provedor real de e-mail com OAuth do usuário;
4. ingestão de mensagens -> classificação -> resumo -> proposta de resposta;
5. entrega somente após gate de autonomia e evidência do conector;
6. ligar submissão real de candidatura ao `career_applications`;
7. criar follow-up scheduler por candidatura;
8. alertas críticos não aguardarem digest;
9. e-mail de digest somente quando canal de entrega estiver realmente conectado.

## Do not fake

- não declarar e-mail enviado sem receipt real;
- não declarar candidatura aplicada sem receipt/URL/status real;
- não marcar `sent` a partir de `approved`;
- não inferir entrevista confirmada a partir de convite;
- não guardar corpo bruto de e-mail por conveniência;
- não usar plano pago para elevar FIT;
- não declarar UI V12 LIVE antes de deployment validado.

`LAST_VERIFIED_CHANGE=PROACTIVE_AGENT_CORE_DIGEST_CRON_LEDGER_NOTIFICATIONS_APPLICATION_MAIL_FOUNDATION_LIVE_UI_V12_VERSIONED_NOT_PROMOTED_MAIL_DELIVERY_NOT_LIVE`
