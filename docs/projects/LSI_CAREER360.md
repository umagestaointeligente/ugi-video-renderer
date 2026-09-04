# LSI CAREER 360 — MANIFESTO CURRENT

Status: MASTER_PILOT_1_0_READY_FOR_MASTER_USE
Versão do manifesto: 2.4
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
`PROFILE_PHOTO_PRIVATE_BACKEND=LIVE`
`PROFESSIONAL_PROFILE_VERSIONING_BACKEND=LIVE`
`FRONTEND_V7=NOT_YET_PROVEN_LIVE`
`CANDIDATE_MANUAL_JOB_ENTRY=REMOVED`
`EMPLOYER_AUTOCOMPLETE_API=LIVE_CATALOG_HYDRATION_PENDING`
`REAL_AUTH_E2E=PASS`
`SECURITY_ADVISOR=PASS_ZERO_LINTS` no último hardening verificado antes da V7.
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

## 3. Superfície do cliente

Mobile-first, com uma área por vez:
1. Início
2. Meu Perfil / Minha Carreira
3. Oportunidades
4. Meu Agente
5. Resolver agora
6. Painel Mestre somente para role master

Arquitetura:
`VERCEL FRONTEND -> SUPABASE AUTH/DATA/EDGE BACKEND`

Correção V6:
`.v { display:none!important }`
`.v.on { display:block!important }`

## 4. Onboarding

Fluxo:
`AUTH -> NOME COMPLETO/DADOS BÁSICOS -> OBJETIVO -> PROTEÇÃO -> ATRIBUIÇÕES -> CURRÍCULO OPCIONAL -> CONFIRMAÇÃO -> AGENT_READY`

### Nome
- solicitar **Nome completo**;
- primeiro nome usado somente na saudação.

### Foto V7
- foto opcional no Perfil Profissional;
- JPG/PNG/WebP, máximo 5 MB;
- storage privado via backend;
- não participa do matching;
- não altera FIT;
- não é usada para inferir atributos sensíveis;
- não é exposta externamente por padrão.

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
- catálogo dedicado ainda precisa de hidratação pública/curada.

### Atribuições
- até 10 atividades/competências conforme cargo;
- `Marcar todas` / `Limpar`;
- `Outras competências ou atribuições` como complemento;
- sugestão nunca vira fato sem confirmação.

### Currículo de entrada
- PDF textual ou DOCX, até 10 MB;
- pode ser enviado agora ou depois;
- sucesso somente após ingest + processamento reais;
- usuário revisa antes de confirmar.

## 5. Perfil Profissional LSI — V7

Objetivo: entregar uma superfície visual própria da LSI, semelhante apenas na utilidade de um perfil profissional digital, sem copiar interface, métricas ou trade dress do LinkedIn.

Conteúdo:
- foto opcional;
- nome;
- headline profissional;
- cargo atual;
- localização;
- resumo profissional;
- competências confirmadas;
- objetivos;
- trajetória confirmada;
- formação;
- idiomas;
- cursos/certificações;
- estado de privacidade.

Edge:
`career-profile-photo = LIVE / JWT_REQUIRED`

Persistência:
`career_profile_media`

## 6. Currículo Inteligente — V7

Edge:
`career-professional-profile = LIVE / JWT_REQUIRED`

Persistência:
`career_professional_profile_versions`

Fluxo:
`DADOS CONFIRMADOS -> VERSÃO PROFISSIONAL -> PREVIEW -> DOWNLOAD/ACEITE`

A inteligência pode:
- organizar;
- reescrever com clareza;
- priorizar;
- criar headline a partir de cargo e competências confirmadas;
- estruturar resumo profissional;
- apontar lacunas.

Não pode fabricar:
- cargo;
- empresa;
- anos de experiência;
- resultado;
- competência;
- formação;
- certificação;
- salário.

Versionamento:
- `draft`;
- `accepted`;
- `superseded`;
- source hash evita duplicação quando a base confirmada não mudou.

Direção frontend V7 preparada:
- `Gerar meu novo currículo`;
- preview visual;
- `Baixar PDF` client-side;
- `Copiar resumo profissional`;
- `Usar esta versão como principal`;
- `Incluir minha foto neste PDF` desligado por padrão.

`FRONTEND_V7=NOT_YET_PROVEN_LIVE` até deployment + validação oficial.

Próximo nível futuro:
`CURRÍCULO GERAL -> VERSÃO PARA OPORTUNIDADE`, alterando apenas ênfase/ordem/redação dos mesmos fatos confirmados.

## 7. Home

Home prioriza **Seu perfil**, não apenas contadores.

Resumo:
- nome completo;
- cargo;
- objetivos;
- local;
- competências;
- proteções;
- currículo;
- completude.

## 8. Oportunidades

A experiência normal do candidato NÃO contém formulário manual de vaga.

Aba Oportunidades:
- read-only para o candidato;
- deve receber resultados do agente;
- deve mostrar aderência, explicação e evidência.

Formulário manual existe somente em:
`Painel Mestre -> Laboratório técnico de matching`.

Estado real:
`AUTOMATED_OPPORTUNITY_RESEARCH=NOT_YET_LIVE`

## 9. Currículo de entrada / segurança

Pipeline:
`FILE -> QUARANTINED -> DEEP VALIDATION -> DRAFT_REQUIRES_CONFIRMATION -> CONFIRMED -> RAW DELETE`

Controles:
- bucket privado;
- tipo real + SHA-256;
- path aleatório;
- validações fail-closed;
- RLS/ownership;
- nenhuma inferência vira fato sem confirmação.

Feedback real V6 mostrou que uma tentativa de upload anterior não gerou registro; o sistema agora exige sucesso explícito.

## 10. Proteção / Matching

`OPORTUNIDADE -> IDENTIFICAR EMPREGADOR -> RESOLVER GRUPO -> PORTA DE PRIVACIDADE -> MATCHING`

- bloqueado = `SILENT_BLOCK`;
- empregador não resolvido = `NO_DISCLOSURE`;
- idade nunca entra;
- foto nunca entra;
- plano pago nunca altera FIT;
- salário oculto/estimado não vira fato;
- salário explícito abaixo do piso pode bloquear;
- score mínimo de referência = 72;
- explicação acompanha classificação.

## 11. Auth / dados

- Supabase Auth;
- Postgres RLS;
- role master por hash de e-mail autorizado;
- service role nunca no frontend;
- Painel Mestre somente agregados;
- candidato comum não acessa painel mestre.

Pendência pré-Beta:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`

## 12. Meu Agente / Resolver agora

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

## 13. Evidências / releases

V6 produção:
`dpl_3CVnsu8JqoxwqL1fZ18rFg3Ztaty`

Release V6:
`career360/releases/MASTER_PILOT_1_0_UX_V6_2026-09-04.md`

Release V7:
`career360/releases/MASTER_PILOT_1_0_PROFILE_CV_V7_2026-09-04.md`

Migration V7 versionada:
`career360/migrations/20260904_professional_profile_and_photo_v1.sql`

## 14. Custo / incubação

`COST_MODE=ZERO_CASH`

Filosofia:
- Provar a Custo Zero
- Autonomia desde a Origem
- Estrutura Espelho
- Evidência antes de capital
- Próximo Degrau

## 15. Próximos Degraus

1. promover e validar frontend V7;
2. teste mestre de foto/perfil/Currículo Inteligente/PDF;
3. reteste real do currículo de entrada;
4. hidratar catálogo público/curado de empregadores;
5. conectar pesquisa automática externa de oportunidades;
6. currículo adaptado por oportunidade sem fabricação;
7. corrigir/provar Redirect allowlist global antes da Beta;
8. Career Learning Engine;
9. Founding Beta 20 após decisão explícita;
10. Recruiter Agent B2B depois.

## 16. Recovery

Novo chat:
`Recovery LSI`

Ler:
- `docs/LSI_CANONICAL_INDEX.md`
- `docs/LSI_RECOVERY_CURRENT.md`
- este manifesto;
- release V7 quando tarefa envolver Perfil/CV.

## 17. DO NOT REDO

- não reconstruir Career;
- não copiar LinkedIn;
- não tornar foto obrigatória;
- não usar foto no matching;
- não reintroduzir formulário manual de vaga ao candidato;
- não reintroduzir service role no frontend;
- não transformar inferência em fato;
- não manter raw de currículo indefinidamente;
- não fingir pesquisa automática externa como LIVE;
- não declarar frontend V7 LIVE sem validação;
- não abrir Beta pública automaticamente;
- não deixar mudança material somente no chat.
