# LSI CAREER 360 — MANIFESTO CURRENT

Status: MASTER_PILOT_1_0_READY_FOR_MASTER_USE
Versão do manifesto: 2.0
Data-base: 2026-09-03 BRT
Owner/CEO: Paulo
Orquestração: Lola / LSI

## 1. Missão

Entregar um agente de carreira que reduza esforço do usuário, proteja sua busca e trabalhe com fatos confirmados.

Posicionamento:
- IA para quem não quer aprender IA.
- Enquanto você trabalha na sua carreira, nós trabalhamos na sua próxima oportunidade.
- Evidência antes de promessa.

## 2. Estado atual

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `lsi-career360-beta1-foundation-20260902`
PR: Draft #25
Supabase dedicado: `nxjdnzdxclszqyqrkwdk`
Hosted app: `https://nxjdnzdxclszqyqrkwdk.supabase.co/functions/v1/career-app`

`MASTER_PILOT_1_0=READY_FOR_MASTER_USE`
`REAL_AUTH_E2E=PASS`
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

## 3. Superfície do cliente

App web responsivo + pacote PWA local.
Áreas:
1. Início
2. Minha Carreira
3. Oportunidades
4. Jornada
5. Meu Agente
6. Resolver agora
7. Painel Mestre para role master

Princípio:
`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`

## 4. Onboarding

Fluxo:
`AUTH -> CURRÍCULO OU MANUAL -> QUARANTENA -> VALIDAÇÃO -> RASCUNHO -> CONFIRMAÇÃO -> PRIVACIDADE -> OBJETIVOS -> AGENT_READY`

Entrada:
- PDF textual;
- DOCX;
- manual/texto;
- voz quando disponível na interface compatível.

Nenhuma inferência vira fato sem confirmação.

## 5. Proteção de Carreira

`OPORTUNIDADE -> IDENTIFICAR EMPREGADOR -> RESOLVER GRUPO -> PORTA DE PRIVACIDADE -> MATCHING`

- atual/grupo podem ser bloqueados;
- bloqueado = `SILENT_BLOCK`;
- desconhecido = `NO_DISCLOSURE`;
- identidade não sai quando gate não permite;
- B2B futuro não recebe busca nominal para descobrir se empregado usa Career;
- idade nunca entra no matching;
- plano pago nunca altera FIT.

## 6. Segurança / dados

- Supabase Auth;
- Postgres RLS;
- anon sem acesso aos dados pessoais;
- ownership por `auth.uid()`;
- bucket privado para currículo;
- upload direto do cliente ao storage bloqueado;
- service role nunca no frontend;
- painel mestre usa RPC autenticada `career_master_status_v1()` e não service role na Edge;
- logs gerais sem currículo, senha, token ou PII desnecessária.

Security Advisor: zero lints no último hardening verificado.

## 7. Currículo

Pipeline:
`FILE -> QUARANTINED -> DEEP VALIDATION -> DRAFT_REQUIRES_CONFIRMATION -> CONFIRMED -> RAW DELETE`

Controles:
- 10 MB;
- tipo real;
- SHA-256;
- path interno aleatório;
- PDF textual;
- DOCX ZIP/XML fail-closed;
- path traversal bloqueado;
- XML inseguro bloqueado;
- compressão suspeita bloqueada;
- PDF protegido/sem texto rejeitado;
- retry idempotente;
- retenção máxima inicial;
- cleanup automático de hora em hora.

## 8. Matching V1

Privacidade é gate anterior ao score.

Sinais permitidos:
- cargos-alvo;
- competências confirmadas;
- modelo de trabalho;
- localização quando aplicável;
- setor;
- salário explícito quando suportado.

Regras:
- salário oculto = a confirmar;
- estimativa não vira fato;
- salário explicitamente abaixo do piso pode bloquear;
- score mínimo de referência = 72;
- explicação acompanha classificação.

E2E final: `100 / QUALIFIED_SALARY_CONFIRM` no cenário sintético aderente.

## 9. Meu Agente

Modo V1 zero-cash e determinístico.
Consulta estado real de:
- oportunidades;
- currículo;
- privacidade;
- configurações;
- pendências;
- suporte;
- acesso mestre.

Não inventa vagas, respostas, entrevistas ou salários.

## 10. SAC / recuperação

`Resolver agora` classifica e tenta resolver:
- documento;
- matching;
- privacidade;
- auth;
- dependência externa;
- outros.

Estados externos:
- Resolvido
- Preciso de Você
- Bloqueio Externo

Falha externa preserva estado; não justifica chamadas caras repetidas.

## 11. Papel mestre

E-mail autorizado fica armazenado como SHA-256 no backend, não em texto aberto no app.
Trigger em `auth.users` cria:
- `career_user_roles`;
- `career_profiles`;
- `career_preferences`;
- `career_action_permissions`.

Se hash do e-mail bater com lista mestre, role = `master`.

Ações irreversíveis continuam fechadas por padrão, inclusive candidatura automática.

## 12. E2E final

PASS com Auth real e dados sintéticos descartáveis:
- create user;
- bootstrap master;
- sign-in JWT;
- DOCX ingest;
- quarantine;
- deep parser;
- draft;
- confirm;
- `AGENT_READY`;
- raw deleted;
- match qualificado;
- feed;
- agent;
- support;
- master panel.

Cleanup verificado depois:
- 0 QA users;
- 0 QA opportunities;
- 0 QA master hashes.

Runner temporário foi desativado depois do teste.

## 13. CI / QA

- Parser Tests = SUCCESS
- Prototype Smoke = SUCCESS
- Edge Typecheck = SUCCESS
- Master app static test = PASS
- JavaScript syntax = PASS
- Hosted app HTTP = 200

## 14. Custo / incubação

`COST_MODE=ZERO_CASH`
Projeto Supabase dedicado confirmado em R$0/mês no momento da criação.

Filosofia:
- Provar a Custo Zero
- Autonomia desde a Origem
- Estrutura Espelho
- Evidência antes de capital
- Próximo Degrau

## 15. Gates finais do Master Pilot

`SECURITY_P0=PASS_MASTER_PILOT_SCOPE`
`CAREER_PRIVACY_P0=PASS_MASTER_PILOT_SCOPE`
`MULTIUSER_ISOLATION=PASS`
`SAFE_FILE_PIPELINE=PASS_MASTER_PILOT_SCOPE`
`RAW_FILE_RETENTION=PASS`
`CV_CONFIRMATION_UI=PASS`
`MATCH_ENGINE_V1=PASS`
`NO_FABRICATION_GUARD=PASS_MASTER_PILOT_SCOPE`
`AUDIT_RECOVERY=PASS_MASTER_PILOT_SCOPE`
`CORE_RELIABILITY=PASS_MASTER_PILOT_SCOPE`
`MASTER_PILOT=READY_FOR_MASTER_USE`

## 16. Próximos Degraus — não blockers

1. uso mestre real;
2. feedback e UX tuning;
3. browser/research automation quando houver rota/capacidade adequada;
4. Career Learning Engine com outcomes reais;
5. Founding Beta 20 após decisão explícita;
6. Recruiter Agent B2B depois.

## 17. Recovery

Novo chat:
`Recovery LSI`

Ler:
- `docs/LSI_CANONICAL_INDEX.md`
- `docs/LSI_RECOVERY_CURRENT.md`
- este manifesto.

## 18. DO NOT REDO

- não reconstruir Career;
- não usar banco de outro produto;
- não reintroduzir service role no frontend;
- não fabricar dados;
- não bypassar MFA/CAPTCHA;
- não abrir Beta pública automaticamente;
- não confundir master pilot pronto com automação total de ATS/browser;
- não deixar mudança material somente no chat.
