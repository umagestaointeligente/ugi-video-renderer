# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-02 BRT
Comando: `LSI::RECOVERY::CURRENT`

## 0. Estado global

`LSI_RECOVERY=TRUE`
`CURRENT_FOCUS=LSI_CAREER_360_BETA_1_0`
`CURRENT_STATUS=FOUNDATION_IN_PROGRESS`
`VERIFIED_REVENUE=R$0,00` para a lógica de incubação/reinvestimento discutida neste ciclo; qualquer estado financeiro vivo deve ser reconfirmado na fonte antes de decisão monetária.

## 1. Última decisão estrutural

Foi adotada uma arquitetura documental cirúrgica para continuidade entre chats:
- um índice canônico curto;
- um snapshot CURRENT sempre atualizado;
- um manifesto CURRENT por projeto;
- documentos especializados estáveis apenas quando necessários;
- ADR somente para mudanças arquiteturais materiais;
- runtime/evidência vence memória de conversa para estado operacional atual.

Comando único de recuperação: `LSI::RECOVERY::CURRENT`.

## 2. LSI Career 360 — estado atual

Repository: `umagestaointeligente/ugi-video-renderer`
Branch isolada: `lsi-career360-beta1-foundation-20260902`
PR Draft: `#25 — Career 360 Beta 1.0 — fundação zero-cost e protótipo PWA`
Main: NÃO ALTERADO por esta fundação.

Fundação já criada na branch:
- protótipo PWA navegável mobile/desktop;
- onboarding curto: currículo / voz / preenchimento gradual;
- upload local de PDF/DOCX no protótipo;
- dados do protótipo ainda sem backend remoto;
- Proteção de Carreira inicial;
- dashboard orientado a resultado;
- navegação em cinco áreas: Início / Oportunidades / Jornada / Carreira / Agente;
- entrada por texto e voz;
- manifest + service worker;
- fundação canônica Beta 1.0;
- Segurança e Privacidade P0;
- Contrato de Dados V1 desacoplado de fornecedor.

Documentos Career já existentes:
- `career360/docs/CAREER360_BETA1_FOUNDATION_V1.md`
- `career360/docs/CAREER360_SECURITY_PRIVACY_P0_V1.md`
- `career360/docs/CAREER360_DATA_CONTRACT_V1.md`

Protótipo:
- `career360/prototype/`

## 3. Princípios obrigatórios Career

### Produto
- PWA/web app primeiro; navegador + instalação opcional no dispositivo.
- Cliente não precisa ter ChatGPT.
- Interface guiada; caixa de texto vazia não é a experiência principal.
- Filosofia: `O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`
- Currículo PDF/DOCX deve pré-preencher o máximo possível e toda extração importante deve ser confirmada.
- Voz é entrada de primeira classe, mas instrução crítica extraída por voz precisa de confirmação.
- Poucos campos visíveis; divulgação progressiva.
- Português por Fora, Padrão Técnico por Dentro.

### Público/UX
- público amplo com atenção especial a profissionais experientes/40+ como hipótese de mercado, nunca como filtro de matching;
- interface sofisticada simples, legível, confortável e de baixa carga cognitiva;
- não assumir que 40+ é necessariamente mais fiel: medir;
- UX deve aprender por evidência, sem otimizar para vício/tempo de tela.

### Privacidade
- Proteção de Carreira é P0;
- empregador atual e grupo econômico identificado entram em bloqueio determinístico quando configurado;
- empresa bloqueada não recebe shortlist, candidatura, notificação ou sinal de existência;
- empresa desconhecida/confidencial não recebe identidade automaticamente;
- empresa B2B não pode pesquisar nominalmente se um funcionário usa Career 360;
- segregação entre Candidate Vault / Employer Vault / Matching;
- pagamento nunca aumenta FIT;
- idade nunca entra como sinal de matching.

### Segurança
- dados sensíveis não podem ser enviados a fornecedor gratuito inadequado apenas para manter custo zero;
- secrets nunca em Git;
- least privilege;
- logs/auditoria sem expor conteúdo desnecessário;
- Security P0 + Privacy P0 são gates antes de testers reais;
- suporte/incident recovery fazem parte do produto.

## 4. Incubadora LSI — regra transversal aprovada

Todo projeto novo deve nascer com dois pilares de entrada:

1. `PROVAR A CUSTO ZERO`
- custo incremental zero até Beta 1.0 quando tecnicamente/eticamente viável;
- free tier/open source/infra compartilhada podem ser usados;
- zero custo nunca vence segurança, privacidade ou legalidade.

2. `AUTONOMIA DESDE A ORIGEM`
- produto deve ser desenhado para operar, diagnosticar, recuperar e atender com mínima intervenção humana;
- SAC virtual/IA faz L0-L3; humano só em autoridade/ação inevitável;
- falha externa não deve queimar inteligência premium indefinidamente.

Requisito técnico transversal:
- `ESTRUTURA ESPELHO`: arquitetura preparada para próxima camada sem obrigar reconstrução do produto.
- investimento compra o `PRÓXIMO DEGRAU` completo, não pedaços sem utilidade.
- projeto ruim deve morrer barato; capital promove vencedores.

Exceção a custo zero somente via `EXCEPTIONAL_BUILD`: evidência muito forte, janela curta, downside limitado, custo controlado e payback plausível; nunca usar reservas/obrigações protegidas.

## 5. Infraestrutura progressiva

Objetivo: construir hoje para R$0 e arquitetar para escala futura sem pagar hoje pela capacidade futura.

Pilares previstos:
- Browser
- IA
- Reliability
- Security
- Database
- Observability
- Support
- Scale

Mecânica interna permitida:
- V1 live
- V2 shadow
- testes
- canary
- promoção gradual
- rollback

Regra externa: `ZERO_CUSTOMER_MIGRATION` — melhorias de infraestrutura não devem obrigar cliente a recriar conta, reinstalar app ou refazer perfil, salvo exigência inevitável de terceiro.

## 6. Caixa / ecossistema

Separar sempre:
- receita bruta;
- taxas/impostos/chargebacks/obrigações;
- reserva operacional;
- Growth Pool / reinvestimento empresarial;
- excedente realmente livre.

Dois níveis de alocação:
1. LSI Ecosystem Capital Allocator — decide projeto/prioridade.
2. Project Infrastructure Allocator — decide onde o projeto investe (browser, security, AI etc.).

NEXO Product e NEXO Capital são conceitos/caixas distintos.

## 7. NEXO — posição no ecossistema

NEXO = `Núcleo de Entendimento, eXplicação e Oportunidades`.
Tagline: `Entenda antes de investir.`

Direção:
- produto futuro de educação/inteligência financeira acessível;
- linguagem simples + camada profissional;
- começar pequeno e provar metodologia antes de transformar em produto maduro;
- execução financeira real, recomendações reguladas ou movimentação de dinheiro exigem gates próprios e não são presumidas.

NEXO deve receber incubação/progresso em paralelo conforme o allocator do ecossistema, sem drenar recursos críticos de produtos com clientes.

## 8. Ecossistema pós-Career

Tese: reter a relação com a LSI, não prender o usuário ao Career.

Caminhos definidos conceitualmente:
- Career 360
- Primeiros 90 Dias
- Management
- Career Guardian
- Cofre de Conquistas
- Promotion/Leadership
- Skills Radar
- Network/Personal Brand
- Sales
- Business

Quando Career cumpre a missão, classificar como `MISSÃO CUMPRIDA`, não falha de retenção.
Métrica futura: continuidade no ecossistema, não retenção artificial em um único agente.

## 9. Interface LSI — direção comum

Princípios:
- Menos configuração. Mais solução.
- Conte uma vez. A LSI organiza o resto.
- carregar dados existentes, extrair, mostrar e pedir confirmação;
- perguntas adicionais somente quando necessárias;
- salvar progresso;
- oferecer voz/texto;
- navegação simples;
- valor por visita > tempo de tela;
- Modo Conforto / acessibilidade;
- machine learning pode sugerir melhorias de UX, mas mudanças entram como versão em teste antes de promoção.

## 10. Bloqueios atuais antes de testers reais

`SECURITY_P0=NOT_YET_PROVEN`
`CAREER_PRIVACY_P0=NOT_YET_PROVEN`
`MULTIUSER_ISOLATION=NOT_YET_PROVEN`
`SAFE_FILE_PIPELINE=NOT_YET_PROVEN`
`MATCH_ENGINE_V1=NOT_YET_PROVEN`
`AUDIT_RECOVERY=NOT_YET_PROVEN`

Protótipo navegável existe, mas isso NÃO significa Beta pronta para pessoas reais.

## 11. Próxima sequência obrigatória

`NEXT_ACTION=`
1. consolidar manifesto CURRENT do Career e protocolo de recovery;
2. construir parser seguro PDF/DOCX com confirmação explícita;
3. autenticação + isolamento multiusuário;
4. Proteção de Carreira P0 completa;
5. Matching Engine V1;
6. audit log / checkpoints / recovery;
7. Security + Privacy P0 tests;
8. UX/visual QA;
9. somente então liberar Primeira Turma/Beta 1.0.

## 12. DO NOT REDO / DO NOT LOSE

- Não reconstruir Career do zero.
- Não mexer no `main` até gates/QA.
- Não confundir protótipo local com produção segura.
- Não ativar modelo/API paga enquanto ZERO-CASH mode estiver vigente sem decisão explícita de reinvestimento.
- Não prometer autonomia onde MFA/CAPTCHA/terceiros exigem humano.
- Não fabricar dados, vagas, resultados, depoimentos ou receita.
- Não transformar LinkedIn em automação não autorizada.
- Não criar 300 documentos fragmentados; atualizar CURRENT e manifestos estáveis.
- Não deixar decisão importante apenas na conversa.

## 13. Arquivos a ler para CURRENT_FOCUS

Obrigatórios:
- `docs/LSI_CANONICAL_INDEX.md`
- `docs/LSI_RECOVERY_CURRENT.md`
- `docs/projects/LSI_CAREER360.md`

Depois, somente conforme tarefa:
- segurança: `career360/docs/CAREER360_SECURITY_PRIVACY_P0_V1.md`
- dados: `career360/docs/CAREER360_DATA_CONTRACT_V1.md`
- fundação/UX: `career360/docs/CAREER360_BETA1_FOUNDATION_V1.md`

## 14. Last verified change

`LAST_VERIFIED_CHANGE=RECOVERY_ARCHITECTURE_CANONICALIZED_ON_CAREER_BRANCH`

O estado deve ser atualizado durante a execução, não apenas no fim do chat.