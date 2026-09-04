# LSI Career 360 — UX V6 / Feedback Mestre

Data: 2026-09-04 BRT
Status: IMPLEMENTADO E PUBLICADO

## Motivo

O primeiro uso mestre real revelou que algumas telas ainda se comportavam como formulário operacional, transferindo trabalho ao candidato. A V6 reforça o princípio:

`O CLIENTE NÃO OPERA A BUSCA. O AGENTE OPERA; O CLIENTE CONFIRMA O QUE IMPORTA.`

## Mudanças de UX

### 1. Nome
- onboarding agora pede explicitamente **Nome completo**;
- validação do primeiro passo exige nome com pelo menos dois termos;
- saudações continuam usando apenas o primeiro nome.

### 2. Empresa atual
- campo passa a suportar autocomplete a partir de 2 caracteres;
- nova Edge Function autenticada `career-employer-suggest` consulta somente catálogo interno de empregadores/aliases;
- digitação livre continua permitida quando não houver sugestão;
- service role permanece somente no backend.

Estado atual do catálogo dedicado no momento desta versão:
- `career_employer_entities = 0`;
- `career_employer_aliases = 0`.

Portanto, a arquitetura do autocomplete está LIVE, mas a hidratação de um catálogo público/curado amplo ainda é Próximo Degrau. Não reutilizar dados privados de candidatos/recrutamento para popular o catálogo global sem governança específica.

### 3. Atribuições / competências
- removido o conceito de um campo livre principal;
- a interface oferece até 10 atribuições sugeridas conforme palavras do cargo informado;
- usuário marca somente as que realmente possui;
- inclui `Marcar todas`, `Limpar` e campo `Outras competências ou atribuições`;
- nenhuma sugestão vira fato sem confirmação explícita.

### 4. Currículo
O teste mestre mostrou que uma tentativa anterior de upload não concluiu o pipeline:
- consulta real de `career_documents` após o teste = 0 registros;
- o evento de confirmação existente indicava origem manual.

A V6 não mascara isso como sucesso. Agora:
- upload mostra estado de processamento;
- sucesso explícito: `Currículo recebido e processado com sucesso. Revise e confirme antes de usar os dados.`;
- falha permanece visível;
- após processamento aparece revisão antes da confirmação;
- após confirmação a interface informa remoção segura do arquivo bruto;
- `Minha Carreira` mostra nome do arquivo, data, status e dados estruturados extraídos quando existentes;
- usuário pode substituir o currículo quando quiser.

Segurança preservada:
- não manter arquivo bruto indefinidamente só para oferecer um visualizador;
- a experiência `Ver dados extraídos do currículo` usa o draft estruturado já protegido por ownership/RLS;
- `career-profile-confirm` V3 agora marca o documento como `deleted` e grava `deleted_at` quando a remoção imediata do objeto bruto for bem-sucedida.

### 5. Home / aderência
- Home passa a priorizar `Seu perfil` com percentual de completude dos dados essenciais;
- resumo mostra nome, cargo, objetivos, local, competências, proteções e estado do currículo;
- métricas do radar deixam de ser a única informação central;
- currículo é indicado como opcional, sem impedir perfil básico completo.

### 6. Oportunidades
O formulário manual `Empresa / Cargo / Modelo / Salário / Competências` foi removido da experiência normal do candidato.

Novo comportamento:
- aba Oportunidades é read-only para o candidato;
- deixa explícito que pesquisa, coleta e filtragem são trabalho do agente;
- o formulário manual permanece somente dentro do `Painel Mestre > Laboratório técnico de matching` para QA interno.

Limite real preservado:
- pesquisa automática externa de vagas ainda NÃO está conectada ao Master Pilot;
- não declarar radar autônomo de mercado como LIVE sem rota/evidência;
- não pedir ao candidato que cadastre vagas para compensar essa ausência.

### 7. Correção de navegação
Foi corrigida uma colisão CSS onde `.stack` podia sobrescrever `display:none` de uma aba inativa. Isso fazia Home, Minha Carreira e Oportunidades aparecerem empilhadas no mesmo scroll.

Nova regra:
- `.v { display:none!important }`;
- `.v.on { display:block!important }`.

Resultado esperado: uma aba = uma superfície visível.

## Backend novo

`career-employer-suggest`
- ACTIVE;
- JWT obrigatório;
- no máximo 8 sugestões;
- sem exposição de group keys ou associação entre candidato e empregador.

`career-profile-confirm`
- V3 ACTIVE;
- quando raw delete imediato passa, atualiza metadata do documento para `file_status=deleted` e `deleted_at=now()`.

## Frontend

Domínio oficial:
`https://lsi-career-360.vercel.app/`

Deployment de produção V6:
`dpl_3CVnsu8JqoxwqL1fZ18rFg3Ztaty`

Validações após deploy:
- deployment = READY;
- alias oficial aplicado;
- `/` = HTTP 200 / `text/html`;
- `/style.css` = HTTP 200 / `text/css`;
- `/app-b.js` = HTTP 200 / `application/javascript`;
- conteúdo V6 presente no domínio oficial.

## Próximo gargalo real

A UX agora deixa de transferir pesquisa de vaga ao usuário. O próximo salto funcional é conectar uma rota de pesquisa automática externa de oportunidades ao backend zero-cash/Próximo Degrau, preservando deduplicação, evidência, privacidade e filtros de salário/FIT.

## Recovery

Novo chat: `Recovery LSI`.

`LAST_VERIFIED_CHANGE=CAREER_UX_V6_FULL_NAME_EMPLOYER_AUTOCOMPLETE_ROLE_CHECKLIST_CV_EXPLICIT_STATUS_PROFILE_SUMMARY_CANDIDATE_JOB_FORM_REMOVED_TAB_VISIBILITY_FIXED`.
