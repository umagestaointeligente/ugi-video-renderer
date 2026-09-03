# LSI — ÍNDICE CANÔNICO DE CONTINUIDADE

Status: CANÔNICO
Versão: 1.0
Data-base: 2026-09-02 BRT
Objetivo: permitir continuidade exata entre chats sem reler uma biblioteca inteira e sem reconstruir estado por memória.

## 1. Âncora única de recuperação

Em um chat novo, o usuário precisa digitar apenas:

`Recovery LSI`

Essa é a âncora humana oficial e deve disparar todo o protocolo canônico de recuperação.

Alias técnico interno de compatibilidade:

`LSI::RECOVERY::CURRENT`

O usuário NÃO precisa conhecer nem digitar o alias técnico.

Resposta esperada na primeira linha:

`LSI_RECOVERY=TRUE`

O novo chat deve então fazer READBACK VIVO seguindo a ordem mínima abaixo e continuar do último NEXT_ACTION confirmado.

## 2. Ordem mínima obrigatória de leitura

1. `docs/LSI_CANONICAL_INDEX.md` — este arquivo; regras e mapa.
2. `docs/LSI_RECOVERY_CURRENT.md` — snapshot curto do estado atual do ecossistema.
3. Manifesto do projeto marcado como `CURRENT_FOCUS` no snapshot.
4. Somente os documentos especializados explicitamente listados pelo manifesto como `READ_NEXT_IF_NEEDED`.
5. Runtime/evidência atual quando a ação depender de estado operacional vivo.

NÃO ler todos os documentos do repositório por padrão.
NÃO reconstruir decisões por memória de conversa.
NÃO assumir que documentação antiga representa estado operacional atual.

## 3. Precedência de verdade

Para ESTADO OPERACIONAL ATUAL:
1. Evidência/readback vivo do runtime ou sistema fonte.
2. `LSI_RECOVERY_CURRENT.md`.
3. Manifesto CURRENT do projeto.
4. Evidência versionada recente.
5. Documentos históricos.
6. Memória de conversa.

Para POLÍTICA/ARQUITETURA INTENCIONAL:
1. Documento canônico vigente do projeto.
2. ADR/decisão estrutural mais recente.
3. Configuração versionada.
4. Conversa apenas quando ainda não promovida a documento canônico.

Se runtime e documento divergirem, registrar a divergência; runtime vence para descrever o que está acontecendo agora, enquanto Git define o que deveria estar configurado.

## 4. Arquitetura documental enxuta

Cada projeto LSI ativo deve manter no máximo estes núcleos:

- `docs/projects/<PROJETO>.md` — manifesto CURRENT: propósito, arquitetura, estado, gates, bloqueios, próximos passos.
- `docs/<projeto>/...` — documentos especializados somente quando um assunto merece detalhe próprio (ex.: segurança, contrato de dados).
- `config/<projeto>/...` — política não secreta legível por máquina, quando aplicável.
- `docs/decisions/...` — somente decisões arquiteturais materiais; não criar ADR para cada conversa.
- evidência/runtime — fora do manifesto; guardar apenas recibos/sumários necessários.

## 5. Regra anti-documento-gigante

`LSI_RECOVERY_CURRENT.md` é sempre SOBRESCRITO/ATUALIZADO; não cresce indefinidamente.
Meta: <= 250 linhas.

Manifesto CURRENT de projeto:
Meta: <= 350 linhas.

Quando um tópico exigir profundidade, criar ou atualizar UM documento especializado estável em vez de expandir o manifesto sem limite.

Não criar cópias quase idênticas com V2/V3/V4 para cada pequena alteração. Git já é o histórico. Criar nova versão nominal apenas quando houver mudança incompatível ou marco relevante.

## 6. Regra de atualização obrigatória

Qualquer mudança material deve atualizar, na mesma rodada ou imediatamente depois:

1. artefato/código/política afetada;
2. manifesto CURRENT do projeto;
3. `docs/LSI_RECOVERY_CURRENT.md` se a mudança alterar estado, blocker, prioridade, arquitetura de alto nível ou NEXT_ACTION;
4. ADR apenas se houver decisão estrutural relevante.

Exemplos de mudança material:
- lançamento de beta;
- mudança de provedor/arquitetura;
- nova integração;
- alteração de segurança/privacidade;
- primeiro cliente/receita comprovada;
- novo blocker;
- migração de infraestrutura;
- mudança de prioridade entre projetos;
- promoção de protótipo para produção.

## 7. Política de nomenclatura

Para cliente/comercial/documentação executiva: Português por Fora.
Para código/chaves/logs quando tecnicamente útil: Padrão Técnico por Dentro.

Exemplos externos preferidos:
- Estrutura Espelho
- Próximo Degrau
- Proteção de Carreira
- Preciso de Você
- Missão Cumprida
- Cofre de Conquistas

Chaves internas podem continuar como `SHADOW`, `ROLLBACK`, `CANARY`, `CIRCUIT_BREAKER`, etc.

## 8. Recuperação deve ser cirúrgica

Ao receber `Recovery LSI` — ou o alias técnico interno — o novo chat deve retornar de forma compacta:

`LSI_RECOVERY=TRUE`
`CURRENT_FOCUS=`
`CURRENT_STATUS=`
`LAST_VERIFIED_CHANGE=`
`CURRENT_BLOCKERS=`
`NEXT_ACTION=`
`DO_NOT_REDO=`
`FILES_READ=`

Depois deve prosseguir autonomamente, salvo autenticação/consentimento humano inevitável.

## 9. Regra de não perder contexto

Antes de um chat atingir limite, a operação não depende de o usuário criar manualmente um handoff novo. O estado canônico deve já estar atualizado ao longo do trabalho.

A conversa é interface de trabalho.
Git/documentação canônica é memória operacional durável.
Runtime/evidência é prova do estado real.

## 10. Projetos atualmente registrados neste índice

- LSI Career 360 — manifesto: `docs/projects/LSI_CAREER360.md`
- LSI Incubadora — política transversal incorporada no snapshot CURRENT até ganhar manifesto próprio quando houver múltiplos projetos em incubação simultânea.
- NEXO — registrado no snapshot CURRENT; aprofundamento permanece em sua documentação canônica própria e deve ser recuperado quando se tornar CURRENT_FOCUS.
- UGI e outros projetos estáveis permanecem isolados; não devem ser reconstruídos ou alterados pelo fluxo Career sem readback específico.

## REGRA FINAL

Um chat novo deve conseguir recuperar o ponto exato de trabalho lendo poucos arquivos curtos.
Detalhe existe sob demanda; estado atual nunca deve depender de reler toda a história.

Para o usuário, a recuperação começa e termina com uma frase simples:

`Recovery LSI`