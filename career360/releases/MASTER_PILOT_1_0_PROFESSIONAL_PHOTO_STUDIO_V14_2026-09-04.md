# LSI Career 360 — Professional Photo Studio V14

Data: 2026-09-04 BRT
Status: BACKEND LIVE / FRONTEND VERSIONED NOT YET PROMOTED / GENERATIVE PROVIDER NOT CONFIGURED

## Objetivo

Depois do upload da foto, o Career pode oferecer uma versão mais profissional compatível com o contexto de carreira confirmado.

Fluxo:
`FOTO ORIGINAL -> CONTEXTO DE CARREIRA -> ESTILO RECOMENDADO -> AJUSTE -> ANTES/DEPOIS -> ACEITAR OU MANTER ORIGINAL`

## Regras duras

- preservar identidade facial e características reais;
- não alterar idade aparente;
- não alterar gênero ou características físicas;
- não afinar/modificar rosto ou corpo;
- não inferir atributos sensíveis;
- foto nunca entra no matching/FIT;
- original nunca é substituída silenciosamente;
- versão profissional só vira principal após aceite explícito.

## Contexto usado

Somente contexto profissional confirmado:
- cargo atual;
- cargos-alvo.

Exemplos de estilos:
- `executive` — liderança/direção;
- `corporate` — comercial/gestão/compras;
- `modern` — tecnologia/produto/dados;
- `creative` — marketing/criativo.

O contexto define apresentação, enquadramento e fundo; não define aparência física.

## Backend LIVE

Migration:
`career360/migrations/20260904_professional_photo_studio_v1.sql`

Hardening:
`career360/migrations/20260904_professional_photo_studio_trigger_hardening.sql`

Tabelas:
- `career_photo_preferences`;
- `career_photo_variants`.

Edge:
- `career-photo-studio` = ACTIVE / JWT required;
- `career-profile-photo` = V2 ACTIVE / JWT required.

`career-profile-photo` V2 agora retorna:
- original;
- variante profissional aceita, quando houver;
- `photo` como imagem de exibição escolhida.

Trocar a foto original invalida variantes antigas automaticamente.

## Local Professional Polish — zero-cash

Frontend versionado:
`career360/frontend/app-k.js`

Primeira rota real não generativa:
- processamento local no navegador;
- enquadramento 4:5;
- separação pessoa/fundo com segmentação local;
- fundo profissional neutro conforme estilo;
- ajustes suaves de brilho/contraste/saturação;
- export JPEG;
- upload privado da variante;
- comparação original x profissional;
- `Usar versão profissional` / `Voltar para original`.

O processamento local evita custo de inferência e mantém a imagem original preservada.

## Provider generativo

`GENERATIVE_PHOTO_PROVIDER=NOT_CONFIGURED`

O runtime não possui atualmente segredo/credencial de provedor de image-to-image.
Por isso o Career não deve fingir alteração generativa de roupa/cenário.

A arquitetura já separa `generation_mode = local_polish | generative` para permitir evolução posterior sem refazer o modelo de dados.

## Segurança

Security Advisor após a migration encontrou exposição indevida da função de trigger como RPC.
Foi corrigido com revoke de EXECUTE para `public`, `anon` e `authenticated`.

Security Advisor final:
- nenhum WARN novo do Estúdio;
- permanece apenas `auth_leaked_password_protection=DISABLED/WARN` já conhecido.

## Estado de UI

`PHOTO_STUDIO_UI=VERSIONED_NOT_YET_PROMOTED`

A produção oficial ainda está no bundle V11.1.
A próxima promoção visual deve carregar, de forma controlada:
- V11.1 existente;
- `app-i.js` Proactive Agent;
- `app-j.js` Meu Perfil;
- `app-k.js` Professional Photo Studio.

Não declarar Estúdio visual LIVE antes de validar o bundle oficial e Android autenticado.

`LAST_VERIFIED_CHANGE=PROFESSIONAL_PHOTO_STUDIO_BACKEND_LIVE_LOCAL_POLISH_UI_VERSIONED_GENERATIVE_PROVIDER_NOT_CONFIGURED`
