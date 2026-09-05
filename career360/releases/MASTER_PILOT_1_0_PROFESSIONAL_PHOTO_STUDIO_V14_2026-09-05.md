# LSI Career 360 — Professional Photo Studio V14

Data: 2026-09-05 BRT
Status: BACKEND LIVE / LOCAL PROFESSIONAL POLISH LIVE / UI LIVE IN OFFICIAL PRODUCTION

## Objetivo

Depois que o usuário envia uma foto, o Career prepara uma versão profissional coerente com cargo atual e cargos-alvo, preservando a identidade e mantendo a original separada.

Fluxo:
`UPLOAD ORIGINAL -> CONTEXTO DE CARREIRA -> ESTILO -> AJUSTE PROFISSIONAL -> ORIGINAL | PROFISSIONAL -> USUÁRIO ESCOLHE`

A foto nunca é substituída silenciosamente.

## Modelo canônico

Tabelas:
- `career_profile_photo_variants`;
- `career_profile_photo_settings`.

Migration base:
`career360/migrations/20260905_career_professional_photo_studio_v1.sql`

Hardening/runtime:
`career360/migrations/20260905_career_photo_studio_local_runtime_v2.sql`

Rotas/tabelas experimentais vazias foram removidas após readback e verificação de dependências. Não criar um segundo modelo paralelo.

## Contextualização profissional

O Career usa somente:
- cargo atual;
- cargos-alvo.

Estilos:
- `executive`;
- `commercial`;
- `modern`;
- `creative`;
- `professional`.

O contexto profissional influencia somente apresentação: enquadramento, fundo, luz, acabamento e linguagem visual. Não altera rosto, corpo, idade, tom de pele, identidade ou qualquer característica sensível.

## Regras duras

- foto opcional;
- original privada é preservada;
- versão profissional só vira ativa após aceite explícito;
- `Usar foto original` reverte a seleção;
- novo upload da original invalida/remove variantes antigas;
- foto nunca entra no matching/FIT;
- não inferir atributos sensíveis;
- não expor foto a empregadores automaticamente.

## Backend LIVE

Edges ACTIVE / JWT required:
- `career-photo-studio` V11;
- `career-profile-photo` V10.

`career-photo-studio` suporta:
- leitura de original/selecionada/variantes;
- recomendação automática de estilo;
- `save_local_variant`;
- `accept`;
- `keep_original`;
- `reject`;
- `set_style`;
- `set_ai_opt_in`.

O runtime atual opera em modo zero-cash:
`local-studio-v1`.

`generate_ai` permanece fail-closed como `AI_PROVIDER_NOT_CONFIGURED`; não existe promessa de geração externa nesta release.

`career-profile-photo` devolve como `photo` a variante profissional aceita/selecionada. Caso contrário devolve a original. Também retorna a original separadamente e limpa variantes antigas quando uma nova original é enviada.

## Local Professional Polish LIVE

Frontend:
`career360/frontend/app-k.js`.

Processamento no aparelho:
- crop profissional 4:5;
- segmentação pessoa/fundo quando MediaPipe estiver disponível;
- fundo neutro coerente com o estilo;
- brilho/contraste/saturação leves;
- fallback de canvas sem segmentação se a biblioteca externa falhar;
- geração JPEG local;
- upload privado da variante;
- comparação Original x Profissional;
- aceite ou retorno à original.

O modo local não promete trocar roupa nem reconstruir aparência.

## UX LIVE

A interface oferece:
- CTA `✨ Melhorar` junto à foto;
- `Estúdio de Foto Profissional`;
- recomendação contextual;
- escolha de estilo;
- Original | Versão profissional;
- `Usar versão profissional`;
- `Gerar outra`;
- `Usar foto original`.

Bundle promovido junto com V12 e V13.

Produção:
`dpl_98eN1wuVyk4wQmnYpG2jjsZ1ZazU`

Alias confirmado:
`https://lsi-career-360.vercel.app/`

Gates comprovados:
- produção = READY;
- HTML oficial carrega `app-i.js`, `app-j.js` e `app-k.js`;
- Vercel runtime errors/fatal no novo deployment: nenhum no período verificado;
- `career-photo-studio` runtime atual = V11;
- `career-profile-photo` runtime atual = V10.

## Segurança

RLS permanece ativo no modelo canônico.
Authenticated lê somente seus próprios registros; escrita de variantes/settings não é liberada diretamente ao cliente.

Security Advisor pós-ajuste:
- nenhum novo lint estrutural de RLS;
- permanece apenas `auth_leaked_password_protection=DISABLED/WARN`.

## Próximo gate humano

Teste Android autenticado:
1. abrir foto -> `✨ Melhorar`;
2. confirmar recomendação de estilo;
3. criar versão profissional;
4. comparar Original x Profissional;
5. aceitar;
6. confirmar foto nova na Minha Página / Meu Perfil / PDF;
7. voltar para a original e confirmar rollback visual.

`LAST_VERIFIED_CHANGE=PHOTO_STUDIO_V14_BACKEND_V11_PROFILE_PHOTO_V10_LOCAL_POLISH_AND_UI_LIVE_OFFICIAL_PRODUCTION`
