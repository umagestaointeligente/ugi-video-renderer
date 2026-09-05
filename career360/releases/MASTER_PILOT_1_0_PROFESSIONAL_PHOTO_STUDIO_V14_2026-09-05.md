# LSI Career 360 — Professional Photo Studio V14

Data: 2026-09-05 BRT
Status: LOCAL POLISH BACKEND LIVE / UI VERSIONED NOT YET PROMOTED / GENERATIVE PROVIDER NOT CONNECTED

## Objetivo

Após o usuário enviar uma foto, o Career prepara uma versão profissional coerente com cargo atual e cargos-alvo, preservando identidade e mantendo a foto original separada.

Fluxo funcional zero-cash:
`UPLOAD ORIGINAL -> CONTEXTO DE CARREIRA -> ESTILO -> AJUSTE LOCAL NO NAVEGADOR -> ORIGINAL | PROFISSIONAL -> ACEITAR/MANTER ORIGINAL`

## Backend LIVE

Tabela canônica:
`career_professional_photo_jobs`

Estados:
- planned;
- generating;
- preview_ready;
- accepted;
- rejected;
- failed.

`career_profiles.active_professional_photo_job_id` guarda somente a variante aceita.
`career_profiles.photo_style_preference` guarda auto/executive/commercial/modern/creative/professional.

Edges ACTIVE / JWT required:
- `career-photo-studio`;
- `career-professional-photo-plan`;
- `career-professional-photo-decision`;
- `career-profile-photo` V5.

## Local Professional Polish — FUNCIONAL NO RUNTIME

O frontend já versionado em `career360/frontend/app-k.js` processa localmente no dispositivo:
- crop 4:5;
- segmentação pessoa/fundo;
- fundo neutro conforme estilo;
- ajustes suaves de brilho/contraste/saturação;
- export JPEG;
- upload privado da variante.

`career-photo-studio` recebe a variante, salva no bucket privado e retorna estado para comparação.

A UI mostra:
`Original | Versão profissional`

Ações:
- Usar versão profissional;
- Gerar outra;
- Usar foto original.

A original nunca é apagada ao aceitar uma variante.

## Contextualização

O contexto permitido usa apenas:
- cargo atual;
- cargos-alvo.

Estilos:
- executive;
- commercial;
- modern;
- creative;
- professional.

Cargo/senioridade servem somente para apresentação visual: enquadramento, fundo, luz e linguagem profissional.

## Regras duras

- preservar identidade;
- não alterar raça/etnia;
- não alterar gênero/apresentação de gênero;
- não rejuvenescer/envelhecer;
- não remodelar rosto;
- não alterar corpo;
- foto nunca entra no matching/FIT;
- foto continua opcional;
- original preservada;
- nenhuma variante vira principal sem aceite explícito.

## Seleção / rollback

`career-profile-photo` V5 retorna:
- `original`;
- `professional` quando houver accepted;
- `photo` = professional aceita; caso contrário, original.

Trocar a original:
- remove/invalida derivações antigas;
- limpa seleção profissional.

Excluir a foto:
- remove original e derivações associadas.

## Generative provider

`GENERATIVE_PHOTO_PROVIDER=NOT_CONFIGURED`

O Vault atual não contém credencial de provedor de imagem.
A rota `generate_ai` permanece fail-closed.

Não prometer mudança generativa de roupa/cenário enquanto não houver provider real.

## UI

`career360/frontend/app-k.js` = VERSIONED / NOT YET PROMOTED.

Não declarar `PHOTO_STUDIO_UI=LIVE` até o bundle oficial do Vercel carregar o módulo e o fluxo ser validado autenticado no Android.

## Segurança

RLS ativo na tabela canônica.
Cliente autenticado lê somente os próprios jobs.
Escrita de variantes/aceite é mediada pelo backend.

Security Advisor pós-DDL:
- nenhum novo lint estrutural de RLS;
- permanece apenas `auth_leaked_password_protection` desativado.

## Próximo passo exato

1. promover `app-k.js` junto com V12/V13 no bundle oficial;
2. testar no Android: original -> criar -> comparar -> aceitar -> voltar para original;
3. validar Minha Página / Meu Perfil / PDF usando automaticamente a variante aceita;
4. só depois avaliar um provider generativo como Próximo Degrau.

`LAST_VERIFIED_CHANGE=PHOTO_STUDIO_V14_LOCAL_POLISH_BACKEND_LIVE_APP_K_VERSIONED_NOT_PROMOTED_GENERATIVE_PROVIDER_NOT_CONFIGURED`
