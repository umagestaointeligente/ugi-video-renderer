# LSI CAREER 360 — MANIFESTO CURRENT

Status: MASTER_PILOT_1_0_ACTIVE
Versão do manifesto: 2.6
Data-base: 2026-09-04 BRT
Owner/CEO: Paulo
Orquestração: Lola / LSI

## 1. Missão

Entregar um agente de carreira que reduza esforço, proteja a busca, opere somente com fatos confirmados e continue trabalhando sem depender do usuário abrir o chat.

Posicionamento:
- IA para quem não quer aprender IA.
- Enquanto você trabalha na sua carreira, nós trabalhamos na sua próxima oportunidade.
- Evidência antes de promessa.

Princípios:
`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`
`O CLIENTE NÃO OPERA A BUSCA. O AGENTE OPERA; O CLIENTE CONFIRMA O QUE IMPORTA.`
`O CAREER NÃO DEPENDE DO USUÁRIO ABRIR O CHAT PARA CONTINUAR TRABALHANDO.`

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
`PROACTIVE_AGENT_CORE_V12=LIVE`
`PROACTIVE_DIGEST_CRON=LIVE`
`PROACTIVE_UI_V12=VERSIONED_NOT_YET_PROMOTED`
`MAIL_DECISION=LIVE`
`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`
`CANDIDATE_MANUAL_JOB_ENTRY=REMOVED`
`EMPLOYER_AUTOCOMPLETE_API=LIVE_CATALOG_HYDRATION_PENDING`
`REAL_AUTH_E2E=PASS`
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

Segurança atual:
- RLS e isolamento ativos;
- Security Advisor sem novo lint estrutural de RLS;
- `auth_leaked_password_protection=DISABLED/WARN` permanece pendente pré-Beta.

## 3. Superfície do cliente

Mobile-first, com complexidade fora do caminho principal:
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
`AUTH -> NOME COMPLETO/DADOS BÁSICOS -> OBJETIVO -> PROTEÇÃO -> ATRIBUIÇÕES -> CONTE DO SEU JEITO -> CURRÍCULO OPCIONAL -> CONFIRMAÇÃO -> AGENT_READY`

Nome completo é o dado canônico; primeiro nome é usado na saudação.

Objetivos:
- cargos-alvo;
- locais aceitos;
- salário mínimo opcional;
- salário alvo opcional.

Proteção de Carreira:
- situação de emprego;
- empresa atual;
- proteção da empresa atual;
- empresas adicionais bloqueadas.

Empresa:
- autocomplete após 2 caracteres;
- `career-employer-suggest` autenticada;
- digitação livre como fallback;
- catálogo ainda precisa de hidratação pública/curada.

Atribuições:
- sugestões contextuais;
- usuário confirma apenas o que é verdadeiro;
- sugestão nunca vira fato automaticamente.

Currículo:
- PDF textual ou DOCX até 10 MB;
- pode ser enviado agora ou depois;
- sucesso somente após ingest + processamento reais;
- usuário revisa antes de confirmar.

## 5. Minha Página — UX V11.1

Perfil profissional próprio da LSI, sem copiar interface, métricas ou trade dress do LinkedIn.

Estrutura:
- foto opcional;
- nome/headline/localização;
- resumo compacto;
- competências;
- Destaques profissionais;
- Liderança e escopo;
- Experiência;
- Formação.

Regra:
`LER PRIMEIRO -> EDITAR SOMENTE SE NECESSÁRIO`

## 6. Foto

`career-profile-photo=LIVE / JWT_REQUIRED`

- opcional;
- JPG/PNG/WebP até 5 MB;
- storage privado;
- signed URL;
- não participa do matching;
- não altera FIT;
- não inferir atributos sensíveis;
- não expor a empregador automaticamente.

PDF: foto desligada por padrão e opt-in do usuário.

`PROFESSIONAL_PHOTO_STUDIO=NOT_LIVE`

Futuro:
`ORIGINAL -> GERAR VARIAÇÃO -> PREVIEW -> USUÁRIO ESCOLHE ORIGINAL/NOVA -> ACEITE`

## 7. Currículo — Parser 1.0.3

Pipeline:
`FILE -> QUARANTINED -> DEEP VALIDATION -> DRAFT_REQUIRES_CONFIRMATION -> CONFIRMED -> RAW DELETE`

`career-document-process=ACTIVE / JWT_REQUIRED`
`PARSER_VERSION=career360-edge-parser/1.0.3`

Separa:
- resumo;
- impactos/destaques;
- transformações;
- liderança/escopo;
- trajetória;
- formação;
- competências;
- idiomas;
- certificações.

Regra:
`EXTRAÇÃO = CANDIDATO A FATO`
`CONFIRMAÇÃO DO USUÁRIO = FATO UTILIZÁVEL`

## 8. Perfil Profissional + Currículo Inteligente — V3

`career-professional-profile=ACTIVE / V3 / JWT_REQUIRED`
Persistência: `career_professional_profile_versions`

Fluxo:
`DADOS CONFIRMADOS -> VERSÃO PROFISSIONAL -> PREVIEW -> DOWNLOAD/ACEITE`

Pode organizar, priorizar e reescrever com clareza.
Não pode fabricar cargo, empresa, tempo de carreira, resultado, competência, formação, certificação ou salário.

Versionamento:
`draft -> accepted -> superseded`

PDF V11.1 suporta resumo, destaques, liderança/escopo, competências, experiência, formação, idiomas, certificações e foto opt-in.

Futuro:
`CURRÍCULO GERAL -> VERSÃO PARA OPORTUNIDADE`, alterando apenas ênfase/ordem/redação dos mesmos fatos confirmados.

## 9. Conte do Seu Jeito — V8

Fluxo:
`FALAR/ESCREVER -> ORGANIZAR -> MOSTRAR -> APROVAR/AJUSTAR/DESCARTAR -> PERFIL/CURRÍCULO`

Sugestões são contextuais ao cargo/carreira.
Somente narrativa `accepted` entra no Perfil/CV.
Raw é minimizado após aceite/rejeição.

## 10. Radar automático

`AUTOMATED_OPPORTUNITY_RESEARCH=LIVE_PILOT_SCOPE`

- 10 fontes públicas estruturadas no piloto atual;
- rotação automática aproximadamente horária;
- cobertura completa estimada ~4h no desenho atual;
- `Pesquisar agora` disponível;
- candidato vê apenas resultados que passam pelos filtros.

Último saneamento integral documentado:
- 126 oportunidades antigas ativas;
- 70 expiradas como ruído regional;
- 56 permaneceram no recorte piloto;
- 0 qualificadas naquele checkpoint.

Zero qualificada é estado válido.

## 11. Region Filter V2

Título + localização são sinais primários.
Descrição só conta quando contém formulação específica de elegibilidade/base Brasil/LATAM.
País não é gravado como BR indiscriminadamente.

## 12. Matching V2

`CHAMPION=v2.0`
`ROLLBACK=v1.0`

Entende:
- família profissional bilíngue/conceitual;
- senioridade;
- similaridade lexical;
- competências quando a fonte traz evidência;
- localização;
- modelo de trabalho;
- setor quando aplicável.

Gates de privacidade/requisito acontecem antes do score.
Threshold de referência: `72`.

Promoção: bateria 6/6 com cargo equivalente bilíngue, área errada, senioridade abaixo, localização proibida, salário abaixo do piso e empresa bloqueada.

## 13. Proactive Agent V12

Missão:
`PESQUISAR -> ANALISAR -> AGIR -> REGISTRAR -> ACOMPANHAR -> DETECTAR MUDANÇA -> AVISAR -> CONTINUAR`

Componentes LIVE:
- `career_activity_ledger`;
- `career_digest_preferences`;
- `career_digest_runs`;
- `career_notifications`;
- `career_applications` foundation;
- `career_mail_actions` foundation;
- `career-proactive-digest`;
- `career-proactive-status`.

Cadências suportadas:
`4h / 6h / 8h / 12h`.

A camada comercial pode alterar cadência. FIT e qualidade de matching permanecem iguais entre planos.

Conta piloto:
`plan_key=pilot`
`cadence_hours=4`

Cron:
`career-proactive-digest`
`7 * * * *`

O cron verifica a cada hora e só processa usuários cujo `next_digest_at` venceu.

QA real:
- primeiro ciclo forçado HTTP 200;
- 1 digest real criado;
- resumo registrou 1 oportunidade analisada / 0 qualificada na janela;
- segundo ciclo imediato processou 0 usuários, comprovando proteção contra duplicação.

QA transacional com rollback:
- candidatura `awaiting_user` -> Ledger + action_required;
- mensagem crítica -> Ledger + critical alert;
- nenhum dado QA persistido.

## 14. E-mail / autonomia

Reutiliza `career_action_permissions`.

Modos:
- `suggestion`;
- `one_tap`;
- `controlled_autopilot`.

Permissões:
- inbox monitoring;
- recruiter reply draft/send;
- follow-up draft/send;
- auto-send acknowledgement simples;
- auto-send disponibilidade simples;
- auto-send follow-up.

Regra dura:
`always_confirm_sensitive_email=true`.

Categorias sensíveis no gate:
- salary;
- offer;
- documents;
- identity;
- interview_commitment;
- legal.

`career-mail-decision=LIVE / JWT_REQUIRED`
Ações:
- get_policy;
- set_policy;
- approve;
- copy;
- dismiss.

Aprovar registra autorização. Não envia.

`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`.
Nenhuma mensagem recebe `sent` sem conector autenticado + receipt real.

## 15. UI Proativa V12

Arquivo versionado:
`career360/frontend/app-i.js`

Prevê na Minha Página:
- `Atualizações do seu agente`;
- última/próxima atualização;
- analisadas/qualificadas/candidaturas/respostas;
- alertas critical/action-required;
- badge no Meu Agente;
- `Atualizar agora`.

`PROACTIVE_UI_V12=VERSIONED_NOT_YET_PROMOTED`.
Não declarar LIVE antes de novo bundle Vercel carregar `app-i.js` e passar teste autenticado.

## 16. Proteção / Matching

`OPORTUNIDADE -> IDENTIFICAR EMPREGADOR -> RESOLVER GRUPO -> PORTA DE PRIVACIDADE -> MATCHING`

- bloqueado = `SILENT_BLOCK`;
- empregador não resolvido = `NO_DISCLOSURE`;
- idade/foto/plano nunca alteram FIT;
- salário estimado/oculto não vira fato.

## 17. Auth / dados

- Supabase Auth;
- Postgres RLS;
- service role nunca no frontend;
- candidato comum não acessa Painel Mestre.

Pendências pré-Beta:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`
`LEAKED_PASSWORD_PROTECTION=DISABLED/WARN`

## 18. Deploy / evidência

Frontend oficial:
`https://lsi-career-360.vercel.app/`

Produção visual V11.1:
`dpl_EjNc9WzK1uPCZFWhY8ympukcAMGG`

Verificado no checkpoint V11.1:
- `READY`;
- target production;
- alias oficial presente;
- HTTP 200;
- HTML carrega `app-h.js` commit `2bff879b2b2a99815ed3933009f9a6a19a8a9501`;
- sem runtime error no período verificado.

UI V12 ainda não promovida.

## 19. Custo / incubação

`COST_MODE=ZERO_CASH`

Filosofia:
- Provar a Custo Zero
- Autonomia desde a Origem
- Estrutura Espelho
- Evidência antes de capital
- Próximo Degrau

## 20. Próximos Degraus

1. promover `app-i.js` no bundle oficial e testar no Android;
2. conectar Gmail/Outlook com OAuth/consentimento individual;
3. ingestão de mensagem -> classificação -> resumo -> resposta sugerida;
4. envio somente após policy gate + receipt;
5. ligar submissão real de candidatura a `career_applications`;
6. follow-up scheduler por candidatura;
7. alertas críticos fora do digest;
8. reprocessar currículo real com Parser 1.0.3;
9. hidratar catálogo público/curado de empregadores;
10. expandir Radar sem perder precisão;
11. currículo por oportunidade sem fabricação;
12. provar redirect allowlist;
13. resolver leaked-password protection;
14. Career Learning Engine;
15. Professional Photo Studio com endpoint real;
16. Founding Beta 20 após decisão explícita;
17. Recruiter Agent B2B depois.

## 21. Recovery

Novo chat:
`Recovery LSI`

Ler:
- `docs/LSI_CANONICAL_INDEX.md`
- `docs/LSI_RECOVERY_CURRENT.md`
- este manifesto;
- `career360/releases/MASTER_PILOT_1_0_PROACTIVE_AGENT_V12_2026-09-04.md` quando a tarefa envolver proatividade/e-mail/candidaturas.

## 22. DO NOT REDO / DO NOT FAKE

- não reconstruir Career;
- não copiar LinkedIn;
- não tornar foto obrigatória;
- não usar foto/idade/plano no FIT;
- não reintroduzir formulário manual de vaga ao candidato;
- não transformar inferência em fato;
- não manter raw por conveniência;
- não fingir catálogo amplo;
- não mostrar vaga ruim para preencher tela;
- não fingir candidatura aplicada;
- não fingir e-mail enviado;
- não marcar `sent` a partir de `approved`;
- não declarar UI V12 LIVE antes do deployment validado;
- não fingir CI PASS;
- não declarar Security Advisor sem warnings;
- não abrir Beta automaticamente;
- não deixar mudança material somente no chat.
