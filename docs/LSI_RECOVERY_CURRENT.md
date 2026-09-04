# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-04 BRT
Âncora humana: `Recovery LSI`
Alias técnico: `LSI::RECOVERY::CURRENT`

## 0. Estado global

`LSI_RECOVERY=TRUE`
`CURRENT_FOCUS=LSI_CAREER_360_MASTER_PILOT_1_0`
`CURRENT_STATUS=MASTER_PILOT_READY_FOR_MASTER_USE_UX_V6_V7_BACKEND_FOUNDATION`
`VERIFIED_REVENUE=R$0,00` para lógica de incubação; reconfirmar antes de decisão monetária.

## 1. Fonte canônica / runtime

Repository: `umagestaointeligente/ugi-video-renderer`
Branch canônica: `main`
PR fundação #25: MERGED

Backend: Supabase `LSI Career 360`, ref `nxjdnzdxclszqyqrkwdk`, região `sa-east-1`.
Frontend oficial: `https://lsi-career-360.vercel.app/`
Vercel project id: `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`.

Arquitetura:
`VERCEL FRONTEND -> SUPABASE AUTH/DATA/EDGE BACKEND`

Não usar Supabase Edge Function como superfície HTML.

## 2. Produto entregue

Master Pilot 1.0:
- Auth individual;
- role `master` por hash de e-mail autorizado;
- onboarding guiado;
- currículo PDF/DOCX em quarentena privada;
- parser determinístico + confirmação humana;
- Proteção de Carreira;
- Matching V1;
- Meu Agente;
- SAC `Resolver agora`;
- Painel Mestre agregado;
- audit trail / retenção de raw;
- frontend responsivo no Vercel.

Princípios:
`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`
`O CLIENTE NÃO OPERA A BUSCA. O AGENTE OPERA; O CLIENTE CONFIRMA O QUE IMPORTA.`

## 3. UX atual — V6 LIVE

Feedback do primeiro uso mestre real gerou a V6.

### Onboarding
1. **Nome completo** — não ambíguo; primeiro nome é usado apenas na saudação.
2. Objetivos de carreira.
3. Proteção de Carreira.
4. **Atribuições/competências por seleção**: até 10 sugestões conforme cargo, `Marcar todas`, `Limpar` e campo `Outras`.
5. Currículo agora ou depois.

### Empresa
- autocomplete após 2 caracteres;
- Edge autenticada `career-employer-suggest` = ACTIVE;
- digitação livre permanece fallback;
- catálogo dedicado amplo ainda NÃO está hidratado: `career_employer_entities=0` e `career_employer_aliases=0` no readback de 2026-09-04;
- não reutilizar dados privados de candidatos/recrutamento como catálogo global sem governança.

### Home
- prioriza cartão `Seu perfil` e completude de dados essenciais;
- resume nome, cargo, objetivos, local, competências, proteções e estado de currículo;
- radar continua visível, porém não domina a experiência com zeros.

### Navegação
Correção crítica:
`.v { display:none!important }`
`.v.on { display:block!important }`

Agora: **uma aba = uma superfície**.

### Oportunidades
- formulário manual de vaga REMOVIDO da experiência do candidato;
- candidato recebe radar read-only;
- formulário `Empresa/Cargo/Modelo/Salário/Skills` existe apenas em `Painel Mestre > Laboratório técnico de matching`;
- pesquisa automática externa ainda NÃO está conectada ao Master Pilot; não fingir que está e não transferir cadastro de vagas para o candidato.

## 4. Currículo — incidente real e correção V6

Readback após o primeiro upload real do usuário mestre:
- `career_documents = 0`;
- evento de confirmação existente indicava `source=manual`.

Conclusão: a tentativa de upload observada na UX anterior NÃO concluiu o pipeline.

V6:
- estado de processamento visível;
- sucesso explícito apenas após `ingest + process`;
- falha fica visível;
- `Minha Carreira` mostra metadata/status e permite trocar arquivo;
- latest structured draft pode ser aberto em `Ver dados extraídos do currículo`;
- não manter raw indefinidamente só para oferecer visualizador.

`career-profile-confirm` V3 = ACTIVE:
- após raw delete imediato bem-sucedido, metadata passa para `file_status=deleted`, `deleted_at=now()`, storage path nulo;
- dados estruturados/confirmados continuam disponíveis sob RLS.

## 5. Frontend V6 — evidência

Deployment produção:
`dpl_3CVnsu8JqoxwqL1fZ18rFg3Ztaty`

Estado: `READY`
Aliases incluem `lsi-career-360.vercel.app`.

Validação:
- `/` = HTTP 200 / `text/html`;
- `/style.css` = HTTP 200 / `text/css`;
- `/app-b.js` = HTTP 200 / `application/javascript`;
- conteúdo V6 presente no domínio oficial.

Release detalhada:
`career360/releases/MASTER_PILOT_1_0_UX_V6_2026-09-04.md`

## 6. V7 — Perfil Profissional + Currículo Inteligente

Decisão de produto aprovada após feedback mestre: aumentar valor percebido entregando ao usuário um **Perfil Profissional LSI** próprio e um **Currículo Inteligente** gerado a partir de dados confirmados.

### Backend LIVE

Migration aplicada:
`career_profile_media_and_generated_profiles_v1`

Tabelas:
- `career_profile_media`;
- `career_professional_profile_versions`.

Edge Functions LIVE / JWT obrigatório:
- `career-profile-photo`;
- `career-professional-profile`.

### Foto
- opcional;
- JPG/PNG/WebP até 5 MB;
- assinatura real + SHA-256;
- storage privado;
- signed URL temporária;
- usuário pode substituir/remover;
- foto NUNCA participa do matching;
- foto NUNCA altera FIT;
- não inferir atributos sensíveis;
- foto no PDF fica DESLIGADA por padrão.

### Perfil Profissional / Currículo Inteligente
A inteligência pode reorganizar e reescrever com clareza dados confirmados, mas não pode fabricar:
- cargo;
- experiência;
- tempo de carreira;
- empresa;
- competência;
- formação;
- certificação;
- resultado.

Versionamento:
- draft / accepted / superseded;
- source hash para evitar versões duplicadas quando os dados não mudaram;
- aceite explícito do usuário para tornar versão principal.

Direção frontend V7 preparada localmente:
- foto opcional no onboarding e Perfil;
- aba `Meu Perfil` com identidade visual própria;
- preview `Seu Currículo Inteligente`;
- `Gerar meu novo currículo`;
- `Baixar PDF` client-side;
- `Copiar resumo profissional`;
- `Usar esta versão como principal`;
- opção de incluir foto no PDF, desligada por padrão.

IMPORTANTE:
`FRONTEND_V7=NOT_YET_PROVEN_LIVE`
Não declarar V7 visual publicada até deploy de produção + validação do domínio oficial.

Release:
`career360/releases/MASTER_PILOT_1_0_PROFILE_CV_V7_2026-09-04.md`

## 7. Auth / segurança

Conta mestre real:
- e-mail confirmado;
- role `master`.

Incidente anterior:
- e-mail de confirmação havia redirecionado para `localhost:3000`;
- frontend hoje envia `emailRedirectTo=https://lsi-career-360.vercel.app/?email-confirmado=1`.

PENDÊNCIA pré-Beta:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`

Último hardening comprovado antes da V7:
`SECURITY_ADVISOR=PASS_ZERO_LINTS`
`MULTIUSER_ISOLATION=PASS`
`PRIVATE_STORAGE=PASS`
`DIRECT_CLIENT_STORAGE_WRITE=DENIED_BY_RLS`

Não transformar estes PASS em promessa além do escopo testado.

## 8. Matching / privacidade

- privacidade antes do score;
- idade nunca entra;
- foto nunca entra;
- pagamento nunca altera FIT;
- salário oculto/estimado não vira fato;
- salário explicitamente abaixo do piso pode bloquear;
- `SILENT_BLOCK` para empresa protegida;
- `NO_DISCLOSURE` para empregador não resolvido.

## 9. Gates

`DEDICATED_PROJECT=PASS`
`SECURITY_P0=PASS_MASTER_PILOT_SCOPE`
`CAREER_PRIVACY_P0=PASS_MASTER_PILOT_SCOPE`
`MULTIUSER_ISOLATION=PASS`
`SAFE_FILE_PIPELINE=PASS_MASTER_PILOT_SCOPE`
`MATCH_ENGINE_V1=PASS`
`NO_FABRICATION_GUARD=PASS_MASTER_PILOT_SCOPE`
`FRONTEND_HOSTING=PASS_VERCEL`
`GUIDED_ONBOARDING_V6=LIVE`
`CANDIDATE_MANUAL_JOB_ENTRY=REMOVED`
`EMPLOYER_AUTOCOMPLETE_API=LIVE_CATALOG_HYDRATION_PENDING`
`PROFILE_PHOTO_PRIVATE_BACKEND=LIVE`
`PROFESSIONAL_PROFILE_VERSIONING_BACKEND=LIVE`
`FRONTEND_V7=NOT_YET_PROVEN_LIVE`
`MASTER_PILOT=READY_FOR_MASTER_USE_V6`
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

## 10. Próximo gargalo real

Dois trilhos imediatos:

1. promover/validar frontend V7 de Perfil Profissional + Currículo Inteligente;
2. conectar `AUTOMATED_OPPORTUNITY_RESEARCH` sem transferir trabalho ao candidato.

Pesquisa automática precisa nascer com:
- custo zero / Próximo Degrau compatível;
- evidência de fonte;
- deduplicação;
- expiração/fechamento;
- privacidade antes de matching;
- filtros de localização/modelo/salário/FIT;
- nenhum bypass de CAPTCHA/MFA;
- checkpoint e tratamento de dependência externa.

Currículo por oportunidade é próximo nível:
`CURRÍCULO GERAL -> VERSÃO PARA OPORTUNIDADE`, sempre com os mesmos fatos confirmados e apenas mudança de ênfase/ordem/redação.

## 11. DO NOT REDO

- não reconstruir Career do zero;
- não reintroduzir formulário manual de vaga ao candidato;
- não copiar interface/trade dress/métricas do LinkedIn;
- não usar foto no matching;
- não tornar foto obrigatória;
- não usar Supabase Edge como hospedagem HTML;
- não reintroduzir service role no frontend;
- não transformar inferência em fato;
- não manter raw de currículo indefinidamente por conveniência;
- não fingir pesquisa automática de vagas como LIVE;
- não declarar frontend V7 LIVE antes de prova;
- não abrir Beta pública automaticamente;
- não criar recovery paralelo.

## 12. NEXT_ACTION

1. promover frontend V7 para produção e validar página/JS/CSS no domínio oficial;
2. usuário mestre testar foto + Perfil Profissional + geração/download de Currículo Inteligente;
3. reenviar currículo real e exigir confirmação explícita de `ingest + process`;
4. hidratar catálogo público/curado de empregadores;
5. construir rota automática de pesquisa de oportunidades;
6. evoluir para currículo adaptado por oportunidade sem fabricação;
7. provar Site URL/Redirect allowlist antes de Beta;
8. Founding Beta 20 somente após decisão explícita.

## 13. Última alteração verificada

`LAST_VERIFIED_CHANGE=PROFILE_PHOTO_PRIVATE_BACKEND_AND_PROFESSIONAL_PROFILE_VERSIONING_LIVE_FRONTEND_V7_PREPARED_NOT_YET_PROMOTED`
