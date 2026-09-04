# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-04 BRT
Âncora humana: `Recovery LSI`
Alias técnico interno: `LSI::RECOVERY::CURRENT`

## 0. Estado global

`LSI_RECOVERY=TRUE`
`CURRENT_FOCUS=LSI_CAREER_360_MASTER_PILOT_1_0`
`CURRENT_STATUS=MASTER_PILOT_ACTIVE_V11_1_WITH_MATCHING_V2_RADAR_LIVE`
`VERIFIED_REVENUE=R$0,00` para lógica de incubação; reconfirmar antes de decisão monetária.

## 1. Fonte canônica

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `main`
Backend: Supabase `nxjdnzdxclszqyqrkwdk`, `sa-east-1`
Frontend oficial: `https://lsi-career-360.vercel.app/`
Vercel project: `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`
Arquitetura: `VERCEL STATIC FRONTEND -> SUPABASE AUTH/DATA/EDGE BACKEND`

Deployment de produção V11.1:
`dpl_EjNc9WzK1uPCZFWhY8ympukcAMGG`

Rollback imediato da camada visual V11:
`dpl_59kEVUkAGkkZZXfRcRP9p4duWoSF`

## 2. Estado comprovado do Master Pilot

`DEDICATED_PROJECT=PASS`
`AUTH=LIVE`
`MASTER_ROLE=LIVE`
`REAL_AUTH_E2E=PASS`
`SECURITY_P0=PASS_MASTER_PILOT_SCOPE_WITH_AUTH_WARNING`
`CAREER_PRIVACY_P0=PASS_MASTER_PILOT_SCOPE`
`MULTIUSER_ISOLATION=PASS`
`SAFE_FILE_PIPELINE=PASS_MASTER_PILOT_SCOPE`
`MATCH_ENGINE_V2=CHAMPION`
`MATCH_ENGINE_V1=ROLLBACK`
`NO_FABRICATION_GUARD=PASS_MASTER_PILOT_SCOPE`
`FRONTEND_HOSTING=PASS_VERCEL`
`GUIDED_ONBOARDING_V6=LIVE`
`PROFILE_CV_V7_V8=LIVE`
`UX_V11_1=LIVE`
`AUTOMATED_OPPORTUNITY_RESEARCH=LIVE_PILOT_SCOPE`
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

Security Advisor atual:
- sem lint estrutural de RLS pendente;
- permanece `auth_leaked_password_protection = WARN / DISABLED`.

Não declarar `PASS_ZERO_LINTS` enquanto esse WARN existir.

## 3. Princípios de produto

`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`
`O CLIENTE NÃO OPERA A BUSCA. O AGENTE OPERA; O CLIENTE CONFIRMA O QUE IMPORTA.`

- português por fora, padrão técnico por dentro;
- privacidade antes de matching;
- idade nunca entra no matching;
- foto nunca entra no matching/FIT;
- plano pago nunca altera FIT;
- salário oculto/estimado nunca vira fato;
- nada de currículo/perfil pode fabricar experiência, cargo, empresa, resultado, competência, formação ou certificação.

## 4. UX atual — V11.1 LIVE

Superfície principal do candidato:
- `Minha Página` = leitura profissional limpa;
- `Oportunidades` = Radar;
- `Meu Agente`;
- edição e suporte ficam em superfícies secundárias/`Mais`;
- Painel Mestre somente role master.

Minha Página:
- foto opcional;
- nome/headline/localização;
- resumo profissional com leitura compacta;
- competências;
- Destaques profissionais quando confirmados;
- Liderança e escopo quando confirmados;
- Experiência;
- Formação.

V11.1:
- reduz parede de texto;
- usa blocos compactos no mobile;
- Smart CV PDF inclui Destaques e Liderança quando disponíveis;
- checkbox de foto no PDF tenta incluir de fato a foto autorizada, convertendo a imagem para JPEG no dispositivo;
- recarrega perfil após geração/aceite/narrativa/currículo/foto.

Módulo frontend:
`career360/frontend/app-h.js`

Commit V11.1 carregado pela produção:
`2bff879b2b2a99815ed3933009f9a6a19a8a9501`

## 5. Currículo — Parser 1.0.3

`PARSER_VERSION=career360-edge-parser/1.0.3`
`career-document-process=ACTIVE / JWT_REQUIRED`

Parser 1.0.3 separa:
- resumo;
- `highlights_evidence`;
- `leadership_evidence`;
- `experience_evidence`;
- `education_evidence`;
- competências;
- idiomas;
- certificações.

Corpus real de QA comprovou que a versão anterior misturava seções e podia gerar `0 experience` mesmo quando havia trajetória no currículo.

QA do corpus real 1.0.3:
- 1 bloco de resumo;
- 4 itens de impacto executivo;
- 10 linhas de transformações/resultados;
- 3 linhas de liderança/escopo;
- 3 linhas de trajetória profissional.

Regra preservada:
`EXTRAIR -> MOSTRAR -> USUÁRIO CONFIRMA -> VIRA FATO`

Raw de currículo continua sujeito a minimização/remoção após confirmação. Não reconstruir automaticamente fatos de um raw já removido.

## 6. Perfil Profissional + Currículo Inteligente — V3 backend

Edge:
`career-professional-profile=ACTIVE / V3 / JWT_REQUIRED`

Persistência:
`career_professional_profile_versions`

Consome somente fonte confirmada:
- perfil básico;
- preferências;
- competências confirmadas;
- último draft de currículo `confirmed`;
- narrativa pessoal `accepted`.

Saída suporta:
- headline;
- resumo;
- skills;
- highlights;
- leadership;
- experience;
- education;
- languages;
- certifications.

Versionamento:
`draft -> accepted -> superseded`

## 7. Conte do Seu Jeito — V8

Backend LIVE:
- `career_personal_narratives_v1`;
- minimização de raw;
- Edge `career-personal-narrative` JWT required;
- Perfil Profissional usa somente narrativa `accepted`.

Fluxo:
`FALAR/ESCREVER -> ORGANIZAR -> MOSTRAR -> APROVAR/AJUSTAR/DESCARTAR -> PERFIL/CURRÍCULO`

Sugestões dinâmicas usam cargo atual + cargos-alvo e não inventam fatos.

## 8. Foto

Backend LIVE:
`career-profile-photo=JWT_REQUIRED`

- opcional;
- JPG/PNG/WebP até 5 MB;
- storage privado + signed URL;
- não entra no matching/FIT;
- não inferir atributos sensíveis;
- foto no currículo continua opt-in.

`PROFESSIONAL_PHOTO_STUDIO=NOT_LIVE`

Não mostrar botão de transformação profissional até existir geração image-to-image ponta a ponta + preview + aceite explícito original/nova.

## 9. Empresa / autocomplete

Edge `career-employer-suggest=LIVE`.
Autocomplete começa após 2 caracteres e permite digitação livre.

`EMPLOYER_CATALOG_HYDRATION=PENDING`

Não fingir cobertura ampla enquanto catálogo dedicado não estiver hidratado.

## 10. Radar automático — LIVE piloto

`AUTOMATED_OPPORTUNITY_RESEARCH=LIVE_PILOT_SCOPE`

Fontes piloto ativas: 10.
Ciclo automatizado: aproximadamente 1h por lote/rotação, cobertura completa em cerca de 4h no desenho atual.
Ação manual adicional: `Pesquisar agora`.

Region Filter V2:
- título/localização são sinais primários;
- descrição só é aceita como evidência regional quando contém formulação específica de elegibilidade Brasil/LATAM;
- país não é mais gravado como BR indiscriminadamente.

Última limpeza integral comprovada:
- 126 oportunidades anteriormente ativas;
- 70 expiradas como ruído regional;
- 56 permaneceram ativas no recorte piloto;
- 0 qualificadas para o perfil mestre naquele checkpoint.

Zero qualificada é estado válido: o agente não deve mostrar vaga ruim para parecer ocupado.

Edges:
- `career-opportunity-research` = LIVE, region-v2;
- `career-opportunity-list` = LIVE, lê somente motor campeão e só expõe qualificadas ativas ao candidato;
- `career-radar-status` = LIVE.

## 11. Matching V2 — CHAMPION

Governança:
`CHAMPION=v2.0`
`ROLLBACK=v1.0`

Tabela interna:
`career_engine_control`

V2 combina:
- família profissional bilíngue/conceitual;
- senioridade;
- similaridade lexical;
- competências quando há evidência de vaga;
- localização;
- modelo de trabalho;
- setor quando aplicável.

Gates anteriores ao score:
- privacidade;
- salário explícito abaixo do piso;
- modelo de trabalho explícito incompatível;
- localização não permitida quando aplicável.

Threshold de referência: `72`.

QA de promoção — 6/6 casos esperados:
1. Head of Sales remoto -> qualificado com salário a confirmar;
2. Director of Marketing -> BELOW_FIT;
3. Sales Development Representative -> BELOW_FIT;
4. localização não aceita -> BLOCKED_REQUIREMENT;
5. salário explícito abaixo do piso -> BLOCKED_REQUIREMENT;
6. empregador bloqueado -> BLOCKED_PRIVACY.

Migrations canônicas:
- `career360/migrations/20260904_matching_v2_control_and_helpers.sql`
- `career360/migrations/20260904_matching_v2_score.sql`

## 12. Proteção / Matching

`OPORTUNIDADE -> IDENTIFICAR EMPREGADOR -> RESOLVER GRUPO -> PORTA DE PRIVACIDADE -> MATCHING`

- bloqueado = `SILENT_BLOCK`;
- não resolvido = `NO_DISCLOSURE`;
- identidade continua sujeita às permissões do usuário;
- foto/idade/plano não alteram FIT.

## 13. Auth / redirect

Supabase Auth + RLS.
Service role nunca no frontend.

Pendência pré-Beta:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`

Pendência de segurança Auth:
`LEAKED_PASSWORD_PROTECTION=DISABLED/WARN`

## 14. Deploy / evidência

Produção V11.1:
`dpl_EjNc9WzK1uPCZFWhY8ympukcAMGG`

Estado verificado:
- `READY`;
- target `production`;
- alias `lsi-career-360.vercel.app` presente;
- `aliasError=null`;
- fetch do domínio oficial = HTTP 200;
- HTML oficial referencia `app-h.js` no commit `2bff879...`;
- Vercel Runtime Errors = nenhum erro no período verificado.

Observação CI:
GitHub não publicou status/check associado ao commit V11.1. Não declarar `CI_PASS` por inferência.

## 15. Próximos gargalos reais

1. teste humano autenticado da V11.1 no celular: leitura da Minha Página + PDF + foto opt-in;
2. reenviar/reprocessar um currículo pelo Parser 1.0.3 e confirmar o novo draft;
3. validar na interface os blocos Destaques/Liderança/Experiência após confirmação 1.0.3;
4. hidratar catálogo público/curado de empregadores;
5. ampliar fontes do Radar sem degradar precisão regional;
6. currículo adaptado por oportunidade sem fabricação;
7. provar redirect allowlist global;
8. habilitar/provar leaked-password protection ou registrar decisão alternativa antes da Beta;
9. Career Learning Engine;
10. Professional Photo Studio somente com endpoint real;
11. Founding Beta 20 somente após decisão explícita.

## 16. DO NOT REDO

- não reconstruir Career do zero;
- não copiar LinkedIn/trade dress/métricas;
- não tornar foto obrigatória;
- não usar foto no matching;
- não reintroduzir vaga manual ao candidato;
- não usar service role no frontend;
- não transformar inferência em fato;
- não conservar raw de currículo/narrativa por conveniência;
- não fingir cobertura de empregadores;
- não fingir oportunidade qualificada;
- não declarar CI PASS sem check real;
- não declarar Security Advisor zero warnings;
- não abrir Beta automaticamente;
- não criar recovery paralelo.

## 17. Arquivos de leitura sob demanda

Manifesto:
`docs/projects/LSI_CAREER360.md`

UX V6:
`career360/releases/MASTER_PILOT_1_0_UX_V6_2026-09-04.md`

Perfil/CV V7:
`career360/releases/MASTER_PILOT_1_0_PROFILE_CV_V7_2026-09-04.md`

Conte do Seu Jeito V8:
`career360/releases/MASTER_PILOT_1_0_CONTE_DO_SEU_JEITO_V8_2026-09-04.md`

V11.1:
`career360/releases/MASTER_PILOT_1_0_INTELLIGENCE_UX_V11_1_2026-09-04.md`

## 18. Última alteração verificada

`LAST_VERIFIED_CHANGE=UX_V11_1_PRODUCTION_MATCHING_V2_CHAMPION_REGION_V2_PARSER_1_0_3_PROFILE_V3_CANONICAL_SYNC`
