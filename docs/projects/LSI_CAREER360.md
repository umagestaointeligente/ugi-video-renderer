# LSI CAREER 360 — MANIFESTO CURRENT

Status: MASTER_PILOT_1_0_READY_FOR_MASTER_USE
Versão do manifesto: 2.3
Data-base: 2026-09-04 BRT
Owner/CEO: Paulo
Orquestração: Lola / LSI

## 1. Missão

Entregar um agente de carreira que reduza esforço, proteja a busca e opere somente com fatos confirmados.

Posicionamento:
- IA para quem não quer aprender IA.
- Enquanto você trabalha na sua carreira, nós trabalhamos na sua próxima oportunidade.
- Evidência antes de promessa.

Princípios de experiência:
`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`
`O CLIENTE NÃO OPERA A BUSCA. O AGENTE OPERA; O CLIENTE CONFIRMA O QUE IMPORTA.`

## 2. Estado atual

Repository: `umagestaointeligente/ugi-video-renderer`
Fonte canônica: `main`
Backend: Supabase `nxjdnzdxclszqyqrkwdk`
Frontend: `https://lsi-career-360.vercel.app/`

`MASTER_PILOT_1_0=READY_FOR_MASTER_USE`
`GUIDED_ONBOARDING_V6=LIVE`
`CANDIDATE_MANUAL_JOB_ENTRY=REMOVED`
`EMPLOYER_AUTOCOMPLETE_API=LIVE_CATALOG_HYDRATION_PENDING`
`REAL_AUTH_E2E=PASS`
`SECURITY_ADVISOR=PASS_ZERO_LINTS` no último hardening verificado.
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

## 3. Superfície do cliente

Mobile-first, com uma área por vez:
1. Início
2. Minha Carreira
3. Oportunidades
4. Meu Agente
5. Resolver agora
6. Painel Mestre somente para role master

Arquitetura:
`VERCEL FRONTEND -> SUPABASE AUTH/DATA/EDGE BACKEND`

Correção V6 de navegação:
`.v { display:none!important }`
`.v.on { display:block!important }`

Isso impede Home/Carreira/Oportunidades de aparecerem empilhadas no mesmo scroll.

## 4. Onboarding V6

Fluxo:
`AUTH -> NOME COMPLETO/DADOS BÁSICOS -> OBJETIVO -> PROTEÇÃO -> ATRIBUIÇÕES -> CURRÍCULO OPCIONAL -> CONFIRMAÇÃO -> AGENT_READY`

### Nome
- solicitar **Nome completo**;
- primeiro nome usado somente na saudação;
- perfil mantém nome completo.

### Objetivo
- cargos-alvo;
- locais aceitos;
- salário mínimo opcional;
- salário alvo opcional.

### Proteção de Carreira
- situação de emprego;
- empresa atual;
- proteção da empresa atual;
- empresas adicionais bloqueadas.

Campo de empresa:
- autocomplete após 2 caracteres;
- Edge autenticada `career-employer-suggest`;
- fallback de digitação livre;
- catálogo dedicado ainda precisa de hidratação pública/curada antes de ter cobertura ampla.

Não usar dados privados de candidatos ou de recrutamento como catálogo global sem governança específica.

### Atribuições
- não usar campo livre como entrada principal;
- sugerir até 10 atividades/competências conforme o cargo informado;
- `Marcar todas` / `Limpar`;
- `Outras competências ou atribuições` como complemento;
- sugestão nunca vira fato sem confirmação.

### Currículo
- PDF textual ou DOCX, até 10 MB;
- pode ser enviado agora ou depois;
- não bloqueia ativação do perfil básico;
- sucesso só aparece depois de ingest + processamento reais;
- usuário revisa antes de confirmar.

## 5. Home V6

A Home prioriza **Seu perfil**, não apenas contadores de radar.

Resumo:
- nome completo;
- cargo atual;
- objetivos;
- local;
- competências confirmadas;
- proteções ativas;
- estado do currículo;
- percentual de completude dos dados essenciais.

Radar continua presente, porém secundário quando ainda não há pesquisa externa automática conectada.

## 6. Oportunidades

A experiência normal do candidato NÃO contém formulário manual de vaga.

Aba Oportunidades:
- read-only para o candidato;
- recebe resultados que o agente encontrou/avaliou;
- deve mostrar aderência, explicação e evidência quando existirem.

O antigo formulário `Empresa/Cargo/Modelo/Salário/Competências` existe somente em:
`Painel Mestre -> Laboratório técnico de matching`.

Estado real:
`AUTOMATED_OPPORTUNITY_RESEARCH=NOT_YET_LIVE`

Não fingir radar autônomo externo enquanto a rota não estiver conectada. Também não transferir cadastro manual de vagas para o cliente.

## 7. Currículo / segurança

Pipeline:
`FILE -> QUARANTINED -> DEEP VALIDATION -> DRAFT_REQUIRES_CONFIRMATION -> CONFIRMED -> RAW DELETE`

Controles:
- bucket privado;
- tipo real + SHA-256;
- path aleatório;
- validações fail-closed de PDF/DOCX;
- RLS/ownership;
- nenhuma inferência vira fato sem confirmação.

Feedback real V6 revelou que a tentativa de upload anterior não gerou registro em `career_documents`. O sistema agora deixa sucesso/falha explícitos.

Após processamento:
- `Minha Carreira` mostra metadata/status;
- usuário pode substituir currículo;
- draft estruturado permite `Ver dados extraídos do currículo` sem conservar o raw indefinidamente;
- quando raw delete imediato passa, `career-profile-confirm` V3 grava `file_status=deleted`, `deleted_at`, storage path nulo.

## 8. Proteção de Carreira / Matching

`OPORTUNIDADE -> IDENTIFICAR EMPREGADOR -> RESOLVER GRUPO -> PORTA DE PRIVACIDADE -> MATCHING`

- bloqueado = `SILENT_BLOCK`;
- empregador não resolvido = `NO_DISCLOSURE`;
- idade nunca entra;
- plano pago nunca altera FIT;
- salário oculto/estimado não vira fato;
- salário explícito abaixo do piso pode bloquear;
- score mínimo de referência = 72;
- explicação acompanha classificação.

## 9. Auth / dados

- Supabase Auth;
- Postgres RLS;
- role master por hash de e-mail autorizado;
- service role nunca no frontend;
- Painel Mestre somente com agregados;
- candidato comum não acessa painel mestre.

Pendência pré-Beta:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`

Frontend já envia `emailRedirectTo` ao domínio oficial, mas a configuração global do provider não pode ser declarada pronta sem evidência.

## 10. Meu Agente / Resolver agora

Meu Agente V1 zero-cash consulta estado real de:
- oportunidades;
- currículo;
- privacidade;
- configurações;
- pendências;
- suporte.

Não inventa vagas, respostas, entrevistas ou salários.

`Resolver agora`:
- Resolvido
- Preciso de Você
- Bloqueio Externo

## 11. Evidência da V6

Vercel production deployment:
`dpl_3CVnsu8JqoxwqL1fZ18rFg3Ztaty`

- deployment = READY;
- domínio oficial = HTTP 200;
- CSS = `text/css`;
- JS = `application/javascript`.

Release detalhada:
`career360/releases/MASTER_PILOT_1_0_UX_V6_2026-09-04.md`

## 12. Custo / incubação

`COST_MODE=ZERO_CASH`

Filosofia:
- Provar a Custo Zero
- Autonomia desde a Origem
- Estrutura Espelho
- Evidência antes de capital
- Próximo Degrau

## 13. Próximos Degraus

1. reteste real do currículo na V6;
2. hidratar catálogo público/curado de empregadores;
3. conectar pesquisa automática externa de oportunidades;
4. corrigir/provar Redirect allowlist global antes da Beta;
5. Career Learning Engine com outcomes reais;
6. Founding Beta 20 após decisão explícita;
7. Recruiter Agent B2B depois.

Pesquisa automática de oportunidades deve nascer com:
- evidência da fonte;
- deduplicação;
- expiração;
- privacidade antes do score;
- filtros de modelo/local/salário/FIT;
- checkpoints;
- nenhum bypass de CAPTCHA/MFA.

## 14. Recovery

Novo chat:
`Recovery LSI`

Ler:
- `docs/LSI_CANONICAL_INDEX.md`
- `docs/LSI_RECOVERY_CURRENT.md`
- este manifesto;
- release V6.

## 15. DO NOT REDO

- não reconstruir Career;
- não reintroduzir formulário manual de vaga ao candidato;
- não reintroduzir service role no frontend;
- não transformar inferência em fato;
- não manter raw de currículo indefinidamente apenas por conveniência;
- não fingir pesquisa automática externa como LIVE;
- não abrir Beta pública automaticamente;
- não deixar mudança material somente no chat.
