# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-04 BRT
Âncora humana: `Recovery LSI`
Alias técnico interno: `LSI::RECOVERY::CURRENT`

## 0. Estado global

`LSI_RECOVERY=TRUE`
`CURRENT_FOCUS=LSI_CAREER_360_MASTER_PILOT_1_0`
`CURRENT_STATUS=MASTER_PILOT_READY_FOR_MASTER_USE_V6_WITH_V7_V8_BACKEND_LIVE_FRONTEND_PROMOTION_PENDING`
`VERIFIED_REVENUE=R$0,00` para lógica de incubação; reconfirmar antes de decisão monetária.

## 1. Fonte canônica

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `main`
Backend: Supabase `nxjdnzdxclszqyqrkwdk`, `sa-east-1`
Frontend oficial: `https://lsi-career-360.vercel.app/`
Arquitetura: `VERCEL FRONTEND -> SUPABASE AUTH/DATA/EDGE BACKEND`

## 2. Estado comprovado do Master Pilot

`DEDICATED_PROJECT=PASS`
`AUTH=LIVE`
`MASTER_ROLE=LIVE`
`REAL_AUTH_E2E=PASS`
`SECURITY_P0=PASS_MASTER_PILOT_SCOPE`
`CAREER_PRIVACY_P0=PASS_MASTER_PILOT_SCOPE`
`MULTIUSER_ISOLATION=PASS`
`SAFE_FILE_PIPELINE=PASS_MASTER_PILOT_SCOPE`
`MATCH_ENGINE_V1=PASS`
`NO_FABRICATION_GUARD=PASS_MASTER_PILOT_SCOPE`
`FRONTEND_HOSTING=PASS_VERCEL`
`GUIDED_ONBOARDING_V6=LIVE`
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

Último Security Advisor comprovado antes das extensões V7/V8: `PASS_ZERO_LINTS`.
Não extrapolar PASS além do escopo testado.

## 3. Princípios de produto

`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`
`O CLIENTE NÃO OPERA A BUSCA. O AGENTE OPERA; O CLIENTE CONFIRMA O QUE IMPORTA.`

- português por fora, padrão técnico por dentro;
- privacidade antes de matching;
- idade nunca entra no matching;
- foto nunca entra no matching;
- plano pago nunca altera FIT;
- salário oculto/estimado nunca vira fato;
- nada de currículo/perfil pode fabricar experiência, cargo, empresa, resultado, competência, formação ou certificação.

## 4. UX V6 — LIVE

Onboarding atual:
1. Nome completo;
2. objetivo de carreira;
3. Proteção de Carreira;
4. competências/atribuições por seleção;
5. currículo agora ou depois.

Correções V6:
- uma aba = uma superfície;
- candidato não preenche vaga manualmente;
- Home prioriza completude do perfil;
- upload de currículo só mostra sucesso após `ingest + process` reais;
- formulário manual de oportunidade existe somente no Laboratório do Painel Mestre.

`AUTOMATED_OPPORTUNITY_RESEARCH=NOT_YET_LIVE`

## 5. Empresa / autocomplete

Edge `career-employer-suggest=LIVE`.
Autocomplete começa após 2 caracteres e permite digitação livre.

Pendência:
`EMPLOYER_CATALOG_HYDRATION=PENDING`
No último readback, catálogo dedicado estava vazio; não fingir cobertura ampla.

## 6. V7 — Perfil Profissional LSI + Currículo Inteligente

Backend LIVE:
- `career-profile-photo` JWT required;
- `career-professional-profile` JWT required;
- `career_profile_media`;
- `career_professional_profile_versions`.

Foto:
- opcional;
- JPG/PNG/WebP até 5 MB;
- storage privado + signed URL;
- não entra no matching/FIT;
- não inferir atributos sensíveis;
- foto no currículo fica desligada por padrão.

Currículo Inteligente:
- usa somente dados confirmados;
- versões `draft / accepted / superseded`;
- source hash evita duplicações;
- pode reorganizar e reescrever, não inventar fatos.

Frontend V7 preparado, mas:
`FRONTEND_V7=NOT_YET_PROVEN_LIVE`

Release:
`career360/releases/MASTER_PILOT_1_0_PROFILE_CV_V7_2026-09-04.md`

## 7. V8 — Conte do Seu Jeito

Backend LIVE:
- migration `career_personal_narratives_v1`;
- migration `career_personal_narratives_minimize_raw_v1`;
- Edge `career-personal-narrative` V3 / JWT required;
- `career-professional-profile` V2 usa apenas narrativa `accepted`.

Fluxo:
`FALAR/ESCREVER -> ORGANIZAR -> MOSTRAR -> APROVAR/AJUSTAR/DESCARTAR -> PERFIL/CURRÍCULO`

Ações backend:
- `prompts`;
- `generate`;
- `accept`;
- `reject`.

### Sugestões dinâmicas

`action=prompts` consulta apenas:
- cargo atual;
- cargos-alvo.

Devolve sugestões contextuais em vez de pergunta genérica.
UX desejada:
- 3 sugestões em `Comece por aqui`;
- `Quero mais ideias`;
- depois temas como Liderança, Resultados, Decisão, Transformação, Pontos fortes, Jeito de trabalhar, Motivação, Aprendizados e Próximo passo.

Exemplos:
- `Sou o tipo de profissional que...`
- `Uma coisa que faço muito bem é...`
- `Quando lidero uma equipe, eu procuro...`
- `Em uma negociação importante, meu ponto forte é...`

Minimização:
- texto bruto é limpo após aceite ou rejeição;
- só texto profissional aceito pode alimentar Perfil/CV.

`CONTE_DO_SEU_JEITO_FRONTEND=NOT_YET_LIVE`

Release:
`career360/releases/MASTER_PILOT_1_0_CONTE_DO_SEU_JEITO_V8_2026-09-04.md`

## 8. Auth / redirect

Conta mestre real:
- e-mail confirmado;
- role `master`.

Frontend envia:
`emailRedirectTo=https://lsi-career-360.vercel.app/?email-confirmado=1`

Pendência pré-Beta:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`

## 9. Proteção / Matching

`OPORTUNIDADE -> IDENTIFICAR EMPREGADOR -> RESOLVER GRUPO -> PORTA DE PRIVACIDADE -> MATCHING`

- bloqueado = `SILENT_BLOCK`;
- não resolvido = `NO_DISCLOSURE`;
- score de referência = 72;
- explicação acompanha classificação.

## 10. Próximos gargalos reais

1. promover e validar frontend V7 + V8 no domínio oficial;
2. teste mestre de foto + Perfil Profissional + Currículo Inteligente + `Conte do seu jeito`;
3. reteste real de upload de currículo;
4. hidratar catálogo público/curado de empregadores;
5. conectar `AUTOMATED_OPPORTUNITY_RESEARCH`;
6. evoluir para currículo adaptado por oportunidade sem fabricação;
7. provar redirect allowlist global;
8. Career Learning Engine;
9. Founding Beta 20 somente após decisão explícita.

## 11. DO NOT REDO

- não reconstruir Career do zero;
- não copiar LinkedIn/trade dress/métricas;
- não tornar foto obrigatória;
- não usar foto no matching;
- não reintroduzir vaga manual ao candidato;
- não usar service role no frontend;
- não transformar inferência em fato;
- não conservar raw de currículo/narrativa por conveniência;
- não fingir pesquisa automática como LIVE;
- não declarar V7/V8 frontend LIVE sem prova;
- não abrir Beta automaticamente;
- não criar recovery paralelo.

## 12. Arquivos de leitura sob demanda

Manifesto:
`docs/projects/LSI_CAREER360.md`

V6:
`career360/releases/MASTER_PILOT_1_0_UX_V6_2026-09-04.md`

V7:
`career360/releases/MASTER_PILOT_1_0_PROFILE_CV_V7_2026-09-04.md`

V8:
`career360/releases/MASTER_PILOT_1_0_CONTE_DO_SEU_JEITO_V8_2026-09-04.md`

## 13. Última alteração verificada

`LAST_VERIFIED_CHANGE=PERSONAL_NARRATIVE_V3_ROLE_AWARE_PROMPTS_LIVE_USER_CONFIRMATION_REQUIRED_FRONTEND_V8_PENDING`
