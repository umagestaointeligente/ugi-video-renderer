# LSI CAREER 360 — MANIFESTO CURRENT

Status: MASTER_PILOT_1_0_READY_FOR_MASTER_USE
Versão do manifesto: 2.2
Data-base: 2026-09-03 BRT
Owner/CEO: Paulo
Orquestração: Lola / LSI

## 1. Missão

Entregar um agente de carreira que reduza esforço, proteja a busca e trabalhe somente com fatos confirmados.

Posicionamento:
- IA para quem não quer aprender IA.
- Enquanto você trabalha na sua carreira, nós trabalhamos na sua próxima oportunidade.
- Evidência antes de promessa.

Princípio de experiência:
`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`

## 2. Estado atual

Repository: `umagestaointeligente/ugi-video-renderer`
Fonte canônica: `main`
PR #25: MERGED
Backend dedicado: Supabase `nxjdnzdxclszqyqrkwdk`
Frontend oficial: `https://lsi-career-360.vercel.app/`

`MASTER_PILOT_1_0=READY_FOR_MASTER_USE`
`GUIDED_ONBOARDING_V5=LIVE`
`REAL_AUTH_E2E=PASS`
`SECURITY_ADVISOR=PASS_ZERO_LINTS` no último hardening verificado.
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

## 3. Superfície do cliente

App web responsivo, mobile-first.

Depois de ativado, áreas principais:
1. Início
2. Minha Carreira
3. Oportunidades
4. Meu Agente
5. Resolver agora
6. Painel Mestre para role master

Frontend e backend separados:
`VERCEL FRONTEND -> SUPABASE AUTH/DATA/EDGE BACKEND`

Não usar Supabase Edge Function como hospedagem da interface.

## 4. Onboarding Guiado V5

Fluxo atual:
`AUTH -> DADOS BÁSICOS -> OBJETIVO -> PROTEÇÃO -> COMPETÊNCIAS -> CURRÍCULO OPCIONAL -> CONFIRMAÇÃO -> AGENT_READY`

Etapa 1 — Sobre você:
- nome;
- cargo atual;
- cidade;
- UF.

Etapa 2 — Seu objetivo:
- cargos-alvo;
- locais aceitos;
- salário mínimo opcional;
- salário alvo opcional.

Etapa 3 — Proteção de Carreira:
- situação de emprego;
- empregador atual;
- proteção do empregador atual;
- empresas adicionais bloqueadas.

Etapa 4 — Competências:
- competências principais confirmadas.

Etapa 5 — Currículo:
- PDF textual ou DOCX;
- até 10 MB;
- pode ser adicionado agora ou depois;
- não bloqueia ativação do agente;
- currículo serve para automatizar organização/preenchimento que o usuário ainda confirma.

UX:
- barra de progresso 1/5;
- Próximo / Voltar;
- Continuar depois / Fazer depois;
- progresso temporário preservado em `sessionStorage`;
- Home oferece retomada do onboarding;
- Minha Carreira permite revisão e currículo posterior;
- senha possui mostrar/ocultar (olho).

Release:
`career360/releases/MASTER_PILOT_1_0_ONBOARDING_GUIADO_2026-09-03.md`

## 5. Auth / usuário mestre

E-mail mestre autorizado fica como SHA-256 no backend, não em texto aberto no app.

Conta mestre real atual:
- e-mail confirmado;
- role = `master`;
- onboarding = `started` no último readback antes de concluir o novo passo a passo.

Incidente conhecido e tratado no frontend:
- confirmação inicial redirecionou para `localhost:3000`;
- confirmação da conta ocorreu corretamente;
- signup agora envia `emailRedirectTo` para o frontend oficial.

Pendência antes da Beta pública:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`
Não declarar resolvido sem evidência do provider.

## 6. Proteção de Carreira

`OPORTUNIDADE -> IDENTIFICAR EMPREGADOR -> RESOLVER GRUPO -> PORTA DE PRIVACIDADE -> MATCHING`

- atual/grupo podem ser bloqueados;
- bloqueado = `SILENT_BLOCK`;
- desconhecido = `NO_DISCLOSURE`;
- identidade não sai quando gate não permite;
- idade nunca entra no matching;
- pagamento nunca altera FIT;
- B2B futuro não recebe busca nominal de usuários Career.

## 7. Segurança / dados

- Supabase Auth;
- Postgres RLS;
- anon sem acesso a dados pessoais;
- ownership por `auth.uid()`;
- bucket privado de currículo;
- upload direto do cliente ao storage bloqueado;
- service role nunca no frontend;
- logs sem currículo/senha/token/PII desnecessária.

Painel Mestre:
- `career_master_metrics` contém somente agregados;
- leitura RLS para role master;
- authenticated não escreve;
- refresh interno não executável por authenticated;
- candidato = HTTP 403;
- mestre = HTTP 200.

## 8. Currículo

Pipeline:
`FILE -> QUARANTINED -> DEEP VALIDATION -> DRAFT_REQUIRES_CONFIRMATION -> CONFIRMED -> RAW DELETE`

Controles:
- 10 MB;
- tipo real;
- SHA-256;
- caminho interno aleatório;
- PDF textual;
- DOCX ZIP/XML fail-closed;
- path traversal/XML inseguro/compressão suspeita bloqueados;
- PDF protegido/sem texto rejeitado;
- retry idempotente;
- cleanup automático;
- inferência nunca vira fato sem confirmação.

## 9. Matching V1

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

E2E sintético aderente: `100 / QUALIFIED_SALARY_CONFIRM`.

## 10. Meu Agente e SAC

Meu Agente V1 zero-cash consulta estado real de:
- oportunidades;
- currículo;
- privacidade;
- configurações;
- pendências;
- suporte;
- acesso mestre.

Não inventa vagas, respostas, entrevistas ou salários.

`Resolver agora` usa estados externos simples:
- Resolvido
- Preciso de Você
- Bloqueio Externo

## 11. E2E / QA

PASS com Auth real e dados sintéticos descartáveis:
- create user;
- bootstrap master;
- JWT real;
- DOCX ingest/quarantine/parser/draft/confirm;
- `AGENT_READY`;
- raw deleted;
- match qualificado;
- feed;
- agent;
- support;
- master panel.

Cleanup pós-E2E = 0 QA users / opportunities / master hashes.

CI da fundação:
- Parser Tests = SUCCESS
- Prototype Smoke = SUCCESS
- Edge Typecheck = SUCCESS
- JavaScript syntax = PASS
- frontend oficial = HTTP 200 / HTML correto

## 12. Custo / incubação

`COST_MODE=ZERO_CASH`
Projeto Supabase dedicado foi confirmado em R$0/mês no momento da criação.

Filosofia:
- Provar a Custo Zero
- Autonomia desde a Origem
- Estrutura Espelho
- Evidência antes de capital
- Próximo Degrau

## 13. Gates

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
`GUIDED_ONBOARDING_V5=LIVE`
`MASTER_PILOT=READY_FOR_MASTER_USE`

## 14. Próximos Degraus

1. continuar uso mestre real;
2. UX tuning baseado em comportamento real;
3. corrigir e provar configuração global de Auth redirects antes da Beta;
4. Career Learning Engine com outcomes reais;
5. browser/research automation quando houver capacidade adequada;
6. Founding Beta 20 após decisão explícita;
7. Recruiter Agent B2B depois.

## 15. Recovery

Novo chat:
`Recovery LSI`

Ler:
- `docs/LSI_CANONICAL_INDEX.md`
- `docs/LSI_RECOVERY_CURRENT.md`
- este manifesto.

## 16. DO NOT REDO

- não reconstruir Career;
- não usar banco de outro produto;
- não reintroduzir service role no frontend;
- não expor `SECURITY DEFINER` diretamente ao authenticated;
- não transformar inferência em fato;
- não bypassar MFA/CAPTCHA;
- não abrir Beta pública automaticamente;
- não confundir Master Pilot pronto com automação total de ATS/browser;
- não deixar mudança material somente no chat.