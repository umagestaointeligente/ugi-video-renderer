# LSI Career 360 — Professional Photo Studio V14

Data: 2026-09-05 BRT
Status: FOUNDATION LIVE / GENERATION PROVIDER NOT CONNECTED / UI NOT PROMOTED

## Objetivo

Após o usuário enviar uma foto, o Career pode preparar uma versão profissional coerente com cargo atual, senioridade e cargos-alvo, preservando identidade e mantendo a foto original separada.

Fluxo alvo:
`UPLOAD ORIGINAL -> CONTEXTO DE CARREIRA -> STYLE PLAN -> IMAGE-TO-IMAGE -> ORIGINAL | PROFISSIONAL -> ACEITAR/MANTER ORIGINAL`

## Backend LIVE

Tabela:
`career_professional_photo_jobs`

Estados:
- planned;
- generating;
- preview_ready;
- accepted;
- rejected;
- failed.

`career_profiles.active_professional_photo_job_id` guarda apenas a seleção aceita.

Edge Functions:
- `career-professional-photo-plan` = ACTIVE / JWT_REQUIRED;
- `career-professional-photo-decision` = ACTIVE / JWT_REQUIRED;
- `career-profile-photo` = ACTIVE V5 / JWT_REQUIRED.

## Contextualização

O planner lê somente:
- cargo atual;
- cargos-alvo;
- foto original existente.

Estilos determinísticos atuais:
- executive_contemporary;
- business_natural;
- modern_professional;
- creative_professional;
- professional_natural.

Cargo/senioridade servem somente para apresentação visual: enquadramento, luz, roupa e fundo.

## Regras duras

- preservar identidade;
- não alterar raça/etnia;
- não alterar gênero/apresentação de gênero;
- não rejuvenescer/envelhecer;
- não remodelar rosto;
- não alterar corpo;
- não usar foto para matching/FIT;
- não tornar foto obrigatória;
- não substituir original sem aceite explícito;
- não apagar original ao aceitar uma versão profissional.

## Seleção / rollback

`career-profile-photo` V5 devolve:
- original;
- professional, quando houver accepted;
- photo = professional aceita; caso contrário, original.

Ao trocar a foto original:
- versões profissionais antigas são invalidadas/removidas;
- seleção ativa volta para original.

Ao excluir a foto:
- original e derivações profissionais associadas são removidas.

## Generation provider

`PROFESSIONAL_PHOTO_GENERATION_PROVIDER=NOT_CONNECTED`

Não existe secret/provider de geração de imagem configurado no runtime atual.
O Vault contém somente secrets operacionais de cron/pipeline.

Portanto:
- planner = LIVE;
- versionamento/aceite/rollback = LIVE;
- geração image-to-image = NOT LIVE;
- botão de geração não deve ser exposto como funcional até provider real produzir preview.

## Segurança

RLS ativo na tabela nova.
Cliente autenticado pode ler somente os próprios jobs.
Escrita ocorre somente por backend/service role.

Security Advisor pós-DDL:
- nenhum novo lint estrutural de RLS;
- permanece apenas WARN conhecido `auth_leaked_password_protection` desativado.

## Próximo passo exato

1. conectar provider image-to-image com custo/limite compatível com o piloto;
2. geração recebe original privado + prompt contextual;
3. salvar derivada no bucket privado;
4. marcar `preview_ready`;
5. UI mostra Original | Profissional;
6. usuário escolhe;
7. `career-professional-photo-decision` aceita/rejeita;
8. endpoint principal passa a servir a versão aceita automaticamente.

`LAST_VERIFIED_CHANGE=PROFESSIONAL_PHOTO_STUDIO_V14_FOUNDATION_LIVE_PLAN_DECISION_VERSIONING_ROLLBACK_READY_GENERATION_PROVIDER_NOT_CONNECTED_UI_NOT_PROMOTED`
