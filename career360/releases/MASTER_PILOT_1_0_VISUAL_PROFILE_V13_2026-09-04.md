# LSI Career 360 — Visual Profile V13

Data: 2026-09-04 BRT
Status: FRONTEND VERSIONED / NOT YET PROMOTED TO OFFICIAL VERCEL BUNDLE

## Objetivo

Reduzir a sensação de painel operacional e transformar o Career 360 em uma experiência profissional visual, agradável e consultável.

Princípio:
`COMPLEXIDADE POR TRÁS. IDENTIDADE PROFISSIONAL NA FRENTE.`

## Nova arquitetura de experiência

### Minha Página
Uso diário:
- identidade profissional resumida;
- agente trabalhando;
- Radar;
- alertas importantes;
- atalhos mínimos.

Não deve exibir formulários ou textos técnicos como elemento principal.

### Meu Perfil
Nova superfície visual interna.

Finalidade:
- usuário se reconhecer profissionalmente;
- revisar como o Career organizou sua história;
- permanecer mais tempo explorando seu perfil;
- reutilizar conteúdos em LinkedIn/currículo sem copiar interface ou trade dress de terceiros.

Arquivo:
`career360/frontend/app-j.js`

## Estrutura visual do Meu Perfil

- capa visual LSI;
- foto opcional;
- nome;
- headline;
- localização;
- selo `Só você vê por enquanto`;
- Sobre;
- Destaques profissionais;
- Liderança e escopo;
- trajetória em linha do tempo;
- competências em chips;
- cargos-alvo / direcionamento;
- formação;
- idiomas e certificações.

## Interações

Topo:
- `Copiar para LinkedIn`;
- `Baixar currículo`;
- `Editar informações`.

`Copiar para LinkedIn` abre um painel próprio com blocos separados:
- Headline;
- Sobre;
- Experiência;
- Competências.

Cada bloco pode ser copiado individualmente.

O conteúdo continua sujeito a revisão do usuário antes de publicação externa.

## Privacidade

`Meu Perfil` é interno por padrão.

Não existe nesta release:
- URL pública;
- compartilhamento externo automático;
- indexação;
- exposição a recrutadores.

O selo `Só você vê por enquanto` é obrigatório enquanto não existir controle de compartilhamento real.

Qualquer futura área compartilhável deve seguir:
`PRIVATE -> PREVIEW -> SELECT FIELDS -> EXPLICIT CONSENT -> SHARE/REVOKE`

## Relação com LinkedIn

A V13 oferece utilidade semelhante de apresentação profissional, sem copiar:
- layout;
- navegação;
- ícones proprietários;
- métricas;
- feed;
- conexões;
- trade dress.

A exportação é por conteúdo textual preparado para o usuário reutilizar onde quiser.

## Mobile

No celular:
- hero menor;
- foto 88 px;
- ações em grid;
- coluna única;
- destaques em cards;
- perfil mantém leitura visual sem parecer formulário.

## Integração com V12

Quando promovidas juntas:
- `app-i.js` = Proactive Agent card/status;
- `app-j.js` = Visual Profile/Meu Perfil.

A experiência desejada passa a ser:
`MINHA PÁGINA -> MEU PERFIL -> OPORTUNIDADES -> MEU AGENTE -> MAIS`

## Estado de deploy

Produção oficial atual continua V11.1:
`dpl_EjNc9WzK1uPCZFWhY8ympukcAMGG`

V13 está versionada, mas o bundle oficial ainda não carrega `app-j.js`.

Não declarar `VISUAL_PROFILE_V13=LIVE` até:
1. bundle Vercel carregar `app-i.js` e `app-j.js`;
2. alias `lsi-career-360.vercel.app` apontar para o deployment novo;
3. HTTP 200 validado;
4. runtime errors checados;
5. teste autenticado Android concluído.

## Do not fake

- não chamar perfil de público enquanto for privado;
- não expor contato/identidade externamente sem consentimento;
- não copiar LinkedIn;
- não inserir informação não confirmada;
- não declarar V13 LIVE antes de deploy comprovado.

`LAST_VERIFIED_CHANGE=VISUAL_PROFILE_V13_VERSIONED_INTERNAL_SHOWCASE_COPY_EXPORT_READY_NOT_YET_PROMOTED`
