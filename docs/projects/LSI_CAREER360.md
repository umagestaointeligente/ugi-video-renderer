# LSI CAREER 360 — MANIFESTO CURRENT

Status: ACTIVE_BUILD
Versão do manifesto: 1.0
Data-base: 2026-09-02 BRT
Owner/CEO: Paulo
Orquestração: Lola / LSI

## 1. Missão

Construir um agente de carreira B2C e, futuramente, um Recruiter Agent B2B conectados por inteligência de matching bilateral, com experiência simples, privacidade forte, automação responsável e aprendizado contínuo.

Posicionamento central:
- IA para quem não quer aprender IA.
- Enquanto você trabalha na sua carreira, nós trabalhamos na sua próxima oportunidade.
- Evidência antes de promessa.

## 2. Estado atual

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `lsi-career360-beta1-foundation-20260902`
PR: Draft #25
Main: não alterado por esta fundação.

Estado: protótipo PWA + documentação P0 em construção.
Não está aprovado para testers reais ainda.

## 3. Arquivos de produto existentes

Fundação:
- `career360/docs/CAREER360_BETA1_FOUNDATION_V1.md`

Segurança/privacidade:
- `career360/docs/CAREER360_SECURITY_PRIVACY_P0_V1.md`

Contrato de dados:
- `career360/docs/CAREER360_DATA_CONTRACT_V1.md`

Protótipo:
- `career360/prototype/index.html`
- `career360/prototype/manifest.webmanifest`
- `career360/prototype/sw.js`
- demais assets do diretório.

## 4. Superfície do cliente

Formato aprovado para Beta 1.0:
- web app/PWA;
- funciona via navegador;
- pode ser instalado como app quando o dispositivo suportar;
- mesma conta entre celular e desktop;
- cliente não precisa possuir conta ChatGPT.

Navegação principal inicial:
1. Início
2. Oportunidades
3. Jornada
4. Carreira
5. Agente

Princípio UX:
`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`

Entradas principais:
- upload de currículo PDF/DOCX;
- voz;
- texto;
- preenchimento gradual como fallback.

## 5. Onboarding Beta 1.0

Fluxo desejado:
1. Boas-vindas.
2. Escolher currículo / voz / preenchimento gradual.
3. Extrair dados do currículo quando fornecido.
4. Mostrar o que foi entendido.
5. Usuário confirma/corrige.
6. Perguntar somente lacunas relevantes.
7. Configurar objetivo de carreira.
8. Configurar Proteção de Carreira.
9. Configurar preferências de atuação/autonomia.
10. `AGENT_READY=true`.
11. Só então iniciar eventual janela de prova de valor/trial.

Não exigir dezenas de campos visíveis.
Salvar progresso.

## 6. Proteção de Carreira — P0

Fluxo obrigatório antes de qualquer divulgação de identidade:

`OPORTUNIDADE -> IDENTIFICAR_EMPREGADOR -> RESOLVER_GRUPO -> PORTA_DE_PRIVACIDADE -> MATCHING/APRESENTAÇÃO`

Regras:
- usuário informa/confirma empregador atual;
- grupo econômico/aliases identificados entram em deny graph quando aplicável;
- usuário pode bloquear empresas adicionais;
- ex-empregadores extraídos do CV podem ser apresentados para seleção de bloqueio;
- empresa bloqueada = `SILENT_BLOCK`;
- empresa desconhecida = `NO_DISCLOSURE` até resolução/consentimento;
- nenhum B2B pode consultar se empregado específico usa Career;
- matching não usa idade;
- pagamento nunca altera FIT;
- identidade inicialmente minimizada/anonimizada quando possível.

## 7. Matching V1 — princípios

Sinais permitidos/desenhados:
- experiência real;
- competências verificadas/confirmadas;
- senioridade;
- responsabilidades;
- localização/modelo de trabalho;
- faixa remuneratória/compatibilidade quando houver base;
- setor;
- preferências explícitas;
- resultados anteriores do funil como sinais de aprendizado, sem fabricar causalidade.

Não fabricar fatos para aumentar aderência.
Não usar decisão automatizada como rejeição humana final no lado B2B.
Explicar fatores relevantes do match.

## 8. Learning Engine

Aprender com:
- match apresentado;
- aceito/rejeitado e motivo;
- candidatura;
- resposta;
- entrevista;
- avanço;
- oferta;
- contratação;
- tempo;
- erro;
- intervenção humana;
- qualidade da experiência.

Produção não deve autoaprender sem controle.
Usar versão atual + versão em teste/challenger.
Hard policies de privacidade/segurança não podem ser enfraquecidas pelo aprendizado.

## 9. Suporte e recuperação

Objetivo: suporte como parte do produto.

Camadas internas:
- L0 prevenção/determinístico;
- L1 self-heal/retry/checkpoint;
- L2 agente de recuperação econômico;
- L3 inteligência avançada;
- L4 autoridade humana quando inevitável.

Externamente, comunicar estados simples:
- Resolvido
- Preciso de Você
- Bloqueio Externo

Sol Extra High/razonamento premium, quando futuramente habilitado por orçamento, é escalada curta e limitada; nunca loop infinito diante de falha externa.

## 10. Infraestrutura e custo

Regra de incubação:
`PROVAR A CUSTO ZERO` até Beta 1.0 quando seguro/viável.

Sem custo zero às custas de:
- privacidade;
- segurança;
- termos de plataforma;
- confiabilidade crítica.

Arquitetura deve usar abstrações para permitir Estrutura Espelho e troca de provider sem migração do cliente.

Capacidades abstratas previstas:
- LSI_AI
- LSI_BROWSER
- LSI_STORAGE
- LSI_AUTH
- LSI_EMAIL
- LSI_OBSERVABILITY
- LSI_SUPPORT

## 11. Estrutura Espelho

Produção futura não deve ser alterada diretamente para testar upgrade arriscado.

Fluxo interno:
`CURRENT -> SHADOW -> TEST -> CANARY -> PROMOTE -> ROLLBACK_IF_NEEDED`

Regra externa:
- cliente não recria conta;
- cliente não refaz perfil;
- cliente não reinstala app por mudança de infraestrutura, salvo exigência inevitável de terceiro.

Investimentos futuros compram o `PRÓXIMO DEGRAU` útil de capacidade.

## 12. Segurança de dados

Antes de testers reais, provar no mínimo:
- autenticação segura;
- autorização server-side;
- segregação multiusuário;
- isolamento Candidate/Employer;
- upload seguro;
- validação de tipo/tamanho de arquivo;
- malware/file scanning quando aplicável;
- criptografia em trânsito;
- proteção de dados armazenados;
- logs sem PII desnecessária;
- audit trail;
- rate limiting/anti-abuse;
- backup/recovery coerente com arquitetura;
- secret management;
- direitos de exclusão/exportação conforme desenho jurídico aplicável.

Nenhum segredo ou dado real de cliente em Git.

## 13. Beta / Primeira Turma

Objetivo inicial: cerca de 20 testers reais, diversos em senioridade, setor, região e situação profissional.

Beta é programa estruturado de validação, não prova de sucesso comercial por si só.

Medir:
- relevância do match;
- onboarding completion;
- time to first value;
- aplicações/ações concluídas;
- respostas/entrevistas quando ocorrerem;
- erros/incidentes;
- taxa de resolução autônoma;
- tempo poupado;
- satisfação;
- intenção/pagamento quando houver teste comercial.

Depoimentos/cases somente reais, autorizados e sem exigir elogio falso.

## 14. Ecossistema pós-Career

Career é porta de entrada, não prisão.

Missão cumprida pode encaminhar para:
- Primeiros 90 Dias;
- Management;
- Career Guardian;
- Cofre de Conquistas;
- Skills/Promotion/Leadership;
- Sales;
- Business;
- outros agentes LSI.

Métrica desejada: continuidade no ecossistema.

## 15. Gates de promoção

Antes de testers reais:
- `SECURITY_P0=PASS`
- `CAREER_PRIVACY_P0=PASS`
- `MULTIUSER_ISOLATION=PASS`
- `SAFE_FILE_PIPELINE=PASS`
- `NO_FABRICATION_GUARD=PASS`
- `AUDIT_RECOVERY=PASS`
- `CORE_RELIABILITY=PASS`
- `BETA_ENVIRONMENT=PASS`

Matching V1 deve estar funcional e QA aprovado para o escopo escolhido.

## 16. NEXT ACTION

Ordem atual:
1. parser seguro PDF/DOCX + extração estruturada;
2. tela de confirmação/correção;
3. auth + isolamento multiusuário;
4. Proteção de Carreira P0;
5. Matching Engine V1;
6. audit/checkpoints/recovery;
7. testes Security/Privacy P0;
8. UX/visual QA;
9. liberação controlada da Primeira Turma.

## 17. READ_NEXT_IF_NEEDED

Se tarefa = segurança/privacidade:
`career360/docs/CAREER360_SECURITY_PRIVACY_P0_V1.md`

Se tarefa = dados/schema/providers:
`career360/docs/CAREER360_DATA_CONTRACT_V1.md`

Se tarefa = UX/fundação/protótipo:
`career360/docs/CAREER360_BETA1_FOUNDATION_V1.md`

Não ler os três automaticamente se a tarefa não exigir.

## 18. DO NOT REDO

- não criar outro protótipo paralelo sem necessidade;
- não mergear main antes dos gates;
- não ativar backend sensível antes de isolamento;
- não tratar upload local do protótipo como pipeline seguro de produção;
- não quebrar privacidade para aumentar conversão;
- não inventar fatos de CV;
- não bypassar MFA/CAPTCHA;
- não depender de um provider específico no domínio lógico;
- não deixar mudança material apenas no chat.
