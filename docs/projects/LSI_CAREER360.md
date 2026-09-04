# LSI CAREER 360 — MANIFESTO CURRENT

Status: MASTER_PILOT_1_0_ACTIVE
Versão do manifesto: 2.5
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

`MASTER_PILOT_1_0=ACTIVE_MASTER_USE`
`GUIDED_ONBOARDING_V6=LIVE`
`PROFILE_PHOTO_PRIVATE_BACKEND=LIVE`
`PROFESSIONAL_PROFILE_V3=LIVE`
`CONTE_DO_SEU_JEITO_V8=LIVE`
`UX_V11_1=LIVE`
`MATCH_ENGINE_V2=CHAMPION`
`MATCH_ENGINE_V1=ROLLBACK`
`AUTOMATED_OPPORTUNITY_RESEARCH=LIVE_PILOT_SCOPE`
`REGION_FILTER_V2=LIVE`
`PARSER_1_0_3=LIVE`
`CANDIDATE_MANUAL_JOB_ENTRY=REMOVED`
`EMPLOYER_AUTOCOMPLETE_API=LIVE_CATALOG_HYDRATION_PENDING`
`REAL_AUTH_E2E=PASS`
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

Segurança atual:
- RLS e isolamento permanecem ativos;
- Security Advisor sem lint estrutural pendente de RLS no checkpoint atual;
- `auth_leaked_password_protection=DISABLED/WARN` permanece pendente pré-Beta.

## 3. Superfície do cliente

Mobile-first, com a complexidade fora do caminho principal:
1. Minha Página
2. Oportunidades / Radar
3. Meu Agente
4. Mais -> Editar meu perfil / Resolver agora
5. Painel Mestre somente para role master

A experiência diária não deve parecer formulário administrativo.

Arquitetura:
`VERCEL STATIC FRONTEND -> SUPABASE AUTH/DATA/EDGE BACKEND`

## 4. Onboarding

Fluxo:
`AUTH -> NOME COMPLETO/DADOS BÁSICOS -> OBJETIVO -> PROTEÇÃO -> ATRIBUIÇÕES -> CURRÍCULO OPCIONAL -> CONFIRMAÇÃO -> AGENT_READY`

### Nome
- solicitar **Nome completo**;
- primeiro nome usado somente na saudação.

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
- atividades/competências sugeridas conforme cargo;
- `Marcar todas` / `Limpar`;
- complemento livre opcional;
- sugestão nunca vira fato sem confirmação.

### Currículo de entrada
- PDF textual ou DOCX, até 10 MB;
- pode ser enviado agora ou depois;
- sucesso somente após ingest + processamento reais;
- usuário revisa antes de confirmar.

## 5. Minha Página — UX V11.1

Objetivo: entregar uma superfície profissional própria da LSI, semelhante apenas na utilidade de um perfil profissional digital, sem copiar interface, métricas ou trade dress do LinkedIn.

Estrutura:
- foto opcional;
- nome;
- headline;
- localização;
- resumo profissional compacto com `Ver mais` quando necessário;
- competências;
- Destaques profissionais;
- Liderança e escopo;
- Experiência;
- Formação.

No mobile:
- destaques aparecem de forma reduzida;
- informação secundária não domina a primeira dobra;
- editar perfil fica fora do fluxo principal.

Regra visual:
`LER PRIMEIRO -> EDITAR SOMENTE SE NECESSÁRIO`

## 6. Foto

Foto é opcional.

Backend:
`career-profile-photo = LIVE / JWT_REQUIRED`

Controles:
- JPG/PNG/WebP até 5 MB;
- storage privado;
- signed URL;
- não participa do matching;
- não altera FIT;
- não é usada para inferir atributos sensíveis;
- não é enviada a empregadores automaticamente.

Currículo Inteligente:
- foto no PDF desligada por padrão;
- quando o usuário ativa, V11.1 converte a imagem localmente para JPEG e tenta incluí-la no PDF.

`PROFESSIONAL_PHOTO_STUDIO=NOT_LIVE`

A futura transformação de foto profissional exige:
`ORIGINAL -> GERAR VARIAÇÃO -> PREVIEW -> USUÁRIO ESCOLHE ORIGINAL/NOVA -> ACEITE`

Não expor botão de transformação antes de existir endpoint real ponta a ponta.

## 7. Currículo — Parser 1.0.3

Pipeline:
`FILE -> QUARANTINED -> DEEP VALIDATION -> DRAFT_REQUIRES_CONFIRMATION -> CONFIRMED -> RAW DELETE`

`career-document-process = ACTIVE / JWT_REQUIRED`
`PARSER_VERSION = career360-edge-parser/1.0.3`

Seções reconhecidas:
- resumo;
- impactos/destaques;
- transformações de negócio;
- liderança/escopo;
- trajetória profissional;
- formação;
- competências;
- idiomas;
- certificações.

O parser não transforma extração em verdade automática.

Regra:
`EXTRAÇÃO = CANDIDATO A FATO`
`CONFIRMAÇÃO DO USUÁRIO = FATO UTILIZÁVEL`

QA com currículo real demonstrou correção do problema do parser 1.0.2, que podia engolir várias seções dentro do resumo e deixar experiência vazia.

## 8. Perfil Profissional + Currículo Inteligente — V3

Backend:
`career-professional-profile = ACTIVE / V3 / JWT_REQUIRED`

Persistência:
`career_professional_profile_versions`

Fluxo:
`DADOS CONFIRMADOS -> VERSÃO PROFISSIONAL -> PREVIEW -> DOWNLOAD/ACEITE`

A inteligência pode:
- organizar;
- reescrever com clareza;
- priorizar;
- criar headline a partir de fatos confirmados;
- estruturar resumo;
- separar Destaques/Liderança/Experiência;
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

PDF V11.1:
- resumo;
- destaques;
- liderança/escopo;
- competências;
- experiência;
- formação;
- idiomas;
- cursos/certificações;
- foto somente opt-in.

Próximo nível futuro:
`CURRÍCULO GERAL -> VERSÃO PARA OPORTUNIDADE`, alterando apenas ênfase/ordem/redação dos mesmos fatos confirmados.

## 9. Conte do Seu Jeito — V8

Fluxo:
`FALAR/ESCREVER -> ORGANIZAR -> MOSTRAR -> APROVAR/AJUSTAR/DESCARTAR -> PERFIL/CURRÍCULO`

Sugestões são contextuais ao cargo e carreira.
Texto bruto é minimizado após aceite/rejeição.
Somente narrativa `accepted` pode alimentar Perfil/CV.

## 10. Radar automático

A experiência normal do candidato NÃO contém formulário manual de vaga.

Formulário manual existe somente em:
`Painel Mestre -> Laboratório técnico de matching`.

Estado real:
`AUTOMATED_OPPORTUNITY_RESEARCH=LIVE_PILOT_SCOPE`

Características:
- 10 fontes públicas estruturadas no piloto atual;
- rotação automática aproximadamente horária;
- cobertura completa estimada em cerca de 4h no desenho atual;
- ação `Pesquisar agora` disponível;
- candidato recebe apenas o que passa por filtros.

Último saneamento integral documentado:
- 126 oportunidades antigas ativas;
- 70 expiradas como ruído regional;
- 56 permaneceram no recorte piloto;
- 0 qualificadas naquele checkpoint para o perfil mestre.

Zero qualificada não é falha de UX. É preferível a mostrar vaga errada.

## 11. Region Filter V2

Problema resolvido:
descrições institucionais mencionavam Brasil/LATAM e faziam uma vaga de outro país parecer brasileira.

Nova regra:
- título + localização = sinal principal;
- descrição só conta com formulação específica de elegibilidade/base Brasil/LATAM;
- país real é armazenado quando identificável;
- não gravar `BR` indiscriminadamente.

## 12. Matching V2

Governança:
`CHAMPION=v2.0`
`ROLLBACK=v1.0`

O V2 entende:
- famílias profissionais bilíngues/conceituais;
- senioridade;
- similaridade lexical;
- competências quando a fonte traz evidência;
- localização;
- modelo de trabalho;
- setor quando aplicável.

Gates de privacidade/requisito acontecem antes do score.

Score mínimo de referência:
`72`

Promoção ocorreu somente após bateria de seis casos:
- cargo equivalente bilíngue correto;
- área profissional errada;
- senioridade abaixo;
- localização proibida;
- salário explícito abaixo do piso;
- empresa bloqueada.

Migrations:
- `career360/migrations/20260904_matching_v2_control_and_helpers.sql`
- `career360/migrations/20260904_matching_v2_score.sql`

## 13. Proteção / Matching

`OPORTUNIDADE -> IDENTIFICAR EMPREGADOR -> RESOLVER GRUPO -> PORTA DE PRIVACIDADE -> MATCHING`

- bloqueado = `SILENT_BLOCK`;
- empregador não resolvido = `NO_DISCLOSURE`;
- idade nunca entra;
- foto nunca entra;
- plano pago nunca altera FIT;
- salário oculto/estimado não vira fato;
- salário explícito abaixo do piso pode bloquear;
- explicação acompanha classificação.

## 14. Auth / dados

- Supabase Auth;
- Postgres RLS;
- role master;
- service role nunca no frontend;
- candidato comum não acessa painel mestre;
- `career_engine_control` é inacessível a anon/authenticated por deny policy explícita.

Pendências pré-Beta:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`
`LEAKED_PASSWORD_PROTECTION=DISABLED/WARN`

## 15. Deploy / evidência

Frontend oficial:
`https://lsi-career-360.vercel.app/`

V11.1 produção:
`dpl_EjNc9WzK1uPCZFWhY8ympukcAMGG`

Verificado:
- deployment `READY`;
- target `production`;
- alias oficial presente;
- `aliasError=null`;
- fetch HTTP 200;
- HTML oficial carrega `app-h.js` no commit `2bff879b2b2a99815ed3933009f9a6a19a8a9501`;
- Vercel Runtime Errors sem ocorrências no checkpoint verificado.

Rollback V11:
`dpl_59kEVUkAGkkZZXfRcRP9p4duWoSF`

CI:
nenhum check/status do GitHub foi associado ao commit V11.1 no checkpoint consultado. Não declarar `CI_PASS`.

## 16. Custo / incubação

`COST_MODE=ZERO_CASH`

Filosofia:
- Provar a Custo Zero
- Autonomia desde a Origem
- Estrutura Espelho
- Evidência antes de capital
- Próximo Degrau

## 17. Próximos Degraus

1. teste humano autenticado da V11.1 no celular;
2. reprocessar/confirmar currículo com Parser 1.0.3;
3. validar Destaques/Liderança/Experiência na Minha Página e PDF;
4. hidratar catálogo público/curado de empregadores;
5. expandir Radar sem perder precisão;
6. currículo adaptado por oportunidade sem fabricação;
7. provar redirect allowlist global;
8. resolver leaked-password protection antes da Beta;
9. Career Learning Engine;
10. Professional Photo Studio com endpoint real;
11. Founding Beta 20 após decisão explícita;
12. Recruiter Agent B2B depois.

## 18. Recovery

Novo chat:
`Recovery LSI`

Ler:
- `docs/LSI_CANONICAL_INDEX.md`
- `docs/LSI_RECOVERY_CURRENT.md`
- este manifesto;
- release V11.1 quando tarefa envolver estado mais recente de Career 360.

## 19. DO NOT REDO

- não reconstruir Career;
- não copiar LinkedIn;
- não tornar foto obrigatória;
- não usar foto no matching;
- não reintroduzir formulário manual de vaga ao candidato;
- não reintroduzir service role no frontend;
- não transformar inferência em fato;
- não manter raw de currículo indefinidamente;
- não fingir catálogo amplo de empresas;
- não mostrar vaga ruim para preencher tela;
- não fingir CI PASS;
- não declarar Security Advisor sem warnings;
- não abrir Beta pública automaticamente;
- não deixar mudança material somente no chat.
