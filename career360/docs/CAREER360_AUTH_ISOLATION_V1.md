# LSI Career 360 — Autenticação e Isolamento Multiusuário V1

Status: DESIGN CANÔNICO / PROJETO SUPABASE CAREER AINDA NÃO CRIADO
Data: 2026-09-02 BRT

## 1. Objetivo

Garantir que cada cliente do Career 360 acesse somente o próprio workspace e que nenhuma falha de interface, URL, ID ou consulta permita acesso cruzado entre usuários.

Princípio:
`A INTERFACE NÃO É FRONTEIRA DE SEGURANÇA.`

Autorização precisa existir no banco/backend mesmo se o cliente adulterar requisições.

## 2. Rota candidata Beta 1.0

- Supabase Auth para identidade/sessão.
- Postgres + Row Level Security para isolamento por linha.
- Publishable key no cliente quando necessário; nunca service_role/secret key.
- PWA Career 360 como cliente.
- operações sensíveis podem passar por adapter/Edge/Worker, mas devem preservar o JWT do usuário e o controle de ownership sempre que possível.

A escolha permanece atrás das capacidades lógicas:
- `LSI_AUTH`
- `LSI_STORAGE`
- `LSI_DATA`

Assim a Estrutura Espelho permite troca futura de provider.

## 3. Projeto isolado obrigatório

Career 360 NÃO pode compartilhar projeto Supabase com `lsi-revenue-autopilot` nem com outro produto que possua dados, segredos ou políticas próprias.

Motivos:
- reduzir blast radius;
- evitar grants/RLS acidentais entre domínios;
- permitir backup/retention independentes;
- permitir evolução e migração sem afetar produtos estáveis;
- separar segredos e auditoria.

O projeto real deve ser criado como projeto dedicado do Career quando a organização for explicitamente selecionada e o custo do conector for confirmado.

## 4. Identidade

Chave primária de ownership:
`auth.users.id` / `auth.uid()`.

O cliente não escolhe `user_id` de outra pessoa como autoridade.
Toda tabela de usuário tem `user_id uuid not null references auth.users(id)`.

Nunca autorizar com:
- e-mail recebido do frontend;
- nome de usuário;
- query parameter;
- `user_metadata` editável pelo usuário;
- campo hidden no formulário.

## 5. Sessão

Requisitos:
- sessão emitida pelo provider de Auth;
- HTTPS obrigatório;
- tokens nunca registrados em logs;
- logout encerra a sessão do cliente;
- operações de alto risco poderão exigir reautenticação/MFA futuramente;
- expiração/revogação precisa fazer parte dos testes antes de produção.

## 6. RLS

Toda tabela exposta precisa:
1. `ENABLE ROW LEVEL SECURITY`;
2. `REVOKE` dos grants padrão;
3. grant mínimo para `authenticated`;
4. policy explícita por operação;
5. ownership com `(select auth.uid()) = user_id`;
6. `UPDATE` com `USING` + `WITH CHECK`;
7. testes positivos e negativos.

`TO authenticated` sozinho NÃO é autorização suficiente.

## 7. Perfis Candidate vs Employer

Beta B2C implementa somente Candidate side.

No futuro B2B:
- identidade corporativa e memberships em tabelas próprias;
- Candidate Vault e Employer Vault separados;
- matching consome apenas campos permitidos;
- empresa não recebe acesso direto ao workspace do candidato;
- B2B não recebe endpoint de busca nominal para descobrir se empregado usa Career.

## 8. Dados de currículo

Fluxo:
`AUTH -> UPLOAD -> QUARANTINE -> VALIDATE -> PARSE -> DRAFT -> CONFIRM -> FACTS`

`career_documents` e `career_profile_drafts` são legíveis apenas pelo dono.
Criação/alteração de status do documento deve ser operação server-side do pipeline, não campo livre do cliente.

O cliente pode confirmar fatos, mas não marcar arbitrariamente um arquivo como `safe_for_parse`.

## 9. Permissões de ação

Separar preferência de carreira de autorização operacional.

Tabela dedicada:
`career_action_permissions`.

Exemplos independentes:
- pesquisar oportunidade;
- customizar CV;
- preparar candidatura;
- enviar candidatura;
- preparar contato;
- enviar contato;
- divulgar identidade.

Default de ações irreversíveis/sensíveis = FALSE até confirmação explícita.

## 10. Audit trail

`career_audit_events`:
- leitura do próprio usuário quando adequado;
- INSERT não concedido diretamente ao frontend;
- emissão por backend/serviço controlado;
- metadata_safe sem corpo integral de currículo, token ou PII desnecessária.

## 11. Anti-IDOR / BOLA

Testes obrigatórios:
- usuário A lê A = PASS;
- usuário A atualiza A = PASS conforme grant;
- usuário A lê B = DENY;
- usuário A atualiza B = DENY;
- usuário A exclui B = DENY;
- usuário não autenticado = DENY;
- tentativa trocando UUID na URL/body = DENY;
- tentativa via filtro/query direto = DENY;
- draft/document de B inacessível a A;
- bloco de empregador de B inacessível a A.

## 12. Storage de currículo

Bucket futuro precisa ser privado.
Objeto deve usar caminho interno não confiável no filename do usuário.
Exemplo lógico:
`<user_id>/<document_id>/resume.bin`

O nome original é apenas display metadata sanitizada.

Políticas precisam impedir:
- listar objetos de outro user_id;
- baixar objeto de outro user_id;
- substituir objeto de outro user_id;
- upload sem autenticação.

Upload de currículo não fica liberado até Storage policies + pipeline de quarentena serem testados.

## 13. Free tier e produção

Free tier pode ser usado para Primeira Turma apenas enquanto limites, disponibilidade e segurança forem adequados.

Não prometer SLA de produção baseado em free tier.
Monitorar capacidade e usar `Próximo Degrau` antes do limite afetar cliente.

A infraestrutura paga futura deve poder entrar via Estrutura Espelho sem recriar contas/perfis.

## 14. Gates

`MULTIUSER_ISOLATION=PASS` exige:
- projeto Career isolado;
- Auth funcional;
- schema aplicado;
- RLS/grants aplicados;
- testes A/B/anon executados;
- advisors de segurança revisados;
- nenhuma finding crítica/alta não aceita formalmente;
- evidência registrada.

Documento/schema no Git não equivale a PASS.

## 15. Próximo passo

1. manter schema executável versionado no Git;
2. selecionar/criar projeto Supabase dedicado quando autorizado pelo fluxo de organização/custo;
3. aplicar schema de forma controlada;
4. testar RLS;
5. revisar advisors;
6. só então conectar a PWA a dados reais de tester.
