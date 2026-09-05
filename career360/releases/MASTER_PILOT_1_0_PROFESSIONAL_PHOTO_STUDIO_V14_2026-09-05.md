# LSI Career 360 — Professional Photo Studio V14

Data: 2026-09-05 BRT
Status: CANONICAL BACKEND LIVE / LOCAL POLISH READY / IMG2IMG ADAPTER DEPLOYED / PROVIDER INFERENCE NOT YET PROVEN / UI VERSIONED NOT YET PROMOTED

## Objetivo

Depois que o usuário envia uma foto, o Career pode preparar uma versão profissional coerente com cargo atual e cargos-alvo, preservando identidade e mantendo a foto original separada.

Fluxo:
`UPLOAD ORIGINAL -> CONTEXTO DE CARREIRA -> ESTILO -> GERAR/AJUSTAR -> ORIGINAL | PROFISSIONAL -> USUÁRIO ESCOLHE`

A foto nunca é substituída silenciosamente.

## Modelo canônico

Migration:
`career360/migrations/20260905_career_professional_photo_studio_v1.sql`

Tabelas:
- `career_profile_photo_variants`;
- `career_profile_photo_settings`.

A rota transitória `career_professional_photo_jobs` foi removida porque estava vazia e duplicava o modelo canônico.
A rota transitória `career_professional_photo_versions` também foi removida antes de receber dados.

Migration de defesa para fresh environments:
`career360/migrations/20260905_career_professional_photo_cleanup_parallel_jobs_v1.sql`

O arquivo antigo `20260905_professional_photo_studio_v1.sql` ficou como no-op explícito para não recriar a rota retirada.

## Estado de dados verificado

- foto original existente: 1;
- variantes profissionais: 0;
- settings: 1;
- selected_kind: `original`;
- selected_variant_id: null;
- AI opt-in: true;
- tabelas paralelas jobs/versions: ausentes.

## Contextualização profissional

O Career usa somente dados profissionais confirmados para escolher a apresentação:
- cargo atual;
- cargos-alvo.

Estilos:
- `executive`;
- `commercial`;
- `modern`;
- `creative`;
- `professional`.

Exemplo do perfil mestre atual:
- cargo atual: Gerente de categoria;
- alvos: Head comercial / Diretor comercial;
- recomendação automática: `executive`.

Isso afeta somente apresentação visual — fundo, enquadramento, iluminação e, quando o provider generativo estiver disponível, linguagem visual/vestuário profissional. Nunca altera matching ou características pessoais.

## Regras duras de identidade

- preservar a mesma pessoa;
- não remodelar rosto;
- não rejuvenescer/envelhecer;
- não alterar tom de pele;
- não alterar raça/etnia;
- não alterar gênero/apresentação de gênero;
- não alterar corpo;
- não criar efeito beauty/glamour;
- preservar marcas e características distintivas;
- foto nunca entra no matching/FIT;
- foto continua opcional;
- original é preservada;
- variante só vira principal após aceite explícito.

## Backend

Edges ACTIVE / JWT required:
- `career-profile-photo` V8;
- `career-photo-studio` V8.

`career-profile-photo`:
- devolve a variante aceita quando o usuário a selecionou;
- caso contrário devolve a original;
- trocar a original invalida/remove derivações antigas;
- excluir foto remove original e derivações.

`career-photo-studio`:
- status original/selecionada/variantes;
- recomenda estilo pela carreira;
- `save_local_variant`;
- `generate_ai`;
- `accept`;
- `keep_original`;
- `reject`;
- `set_style`;
- `set_ai_opt_in`.

## IA image-to-image

Adapter implantado:
`@cf/runwayml/stable-diffusion-v1-5-img2img`

Configuração conservadora:
- `strength=0.28`;
- guidance 7;
- 20 steps;
- 768x768;
- negative prompt contra mudança de identidade/aparência;
- prompt contextual usa carreira apenas para apresentação.

Credenciais esperadas no runtime:
- `CLOUDFLARE_ACCOUNT_ID`;
- `CLOUDFLARE_API_TOKEN`.

Estado correto:
`PHOTO_STUDIO_AI_ADAPTER=DEPLOYED`
`CLOUDFLARE_PROVIDER_INFERENCE=NOT_YET_PROVEN`

Não declarar geração IA ponta a ponta LIVE até uma chamada autenticada produzir uma variante real e o usuário validar Antes/Depois.

## Fallback zero-cash local

Frontend versionado:
`career360/frontend/app-k.js`.

Se `ai_generation=false` ou a IA externa falhar, o cliente usa automaticamente o Local Professional Polish:
- crop 4:5;
- segmentação pessoa/fundo quando disponível;
- fundo profissional por estilo;
- ajustes leves de brilho/contraste/saturação;
- JPEG local;
- upload privado como variante;
- comparação Original x Profissional.

O local polish não promete trocar roupa de forma generativa.

## UX planejada V14

- CTA `✨ Melhorar` junto à foto;
- modal `Estúdio de Foto Profissional`;
- recomendação contextual;
- estilos opcionais;
- Original | Versão profissional;
- `Usar versão profissional`;
- `Gerar outra`;
- `Usar foto original`.

`PHOTO_STUDIO_UI=VERSIONED_NOT_YET_PROMOTED`.
Produção Vercel comprovada continua V11.1; não declarar V14 visual LIVE antes da promoção controlada e teste Android.

## Segurança

RLS permanece ativo no modelo canônico.
Cliente autenticado lê apenas dados próprios; escrita/aceite passa pelo backend.
Security Advisor após a limpeza:
- nenhum novo lint estrutural de RLS;
- permanece somente `auth_leaked_password_protection=DISABLED/WARN`.

## Próximos gates

1. promover `app-k.js` junto de V12/V13 sem quebrar o bundle V11.1;
2. testar Android autenticado;
3. validar Local Polish: original -> gerar -> comparar -> aceitar -> voltar para original;
4. provar credenciais/inferência Cloudflare, se configuradas;
5. se a IA gerar uma variante, validar preservação de identidade antes de qualquer promoção ampla;
6. validar Minha Página / Meu Perfil / PDF usando a variante aceita.

`LAST_VERIFIED_CHANGE=PHOTO_STUDIO_CANONICAL_VARIANTS_SETTINGS_RESTORED_PARALLEL_ROUTES_REMOVED_SD15_IMG2IMG_ADAPTER_DEPLOYED_PROVIDER_INFERENCE_UNPROVEN_APP_K_VERSIONED_NOT_PROMOTED`
