# LSI Career 360 — Perfil Profissional + Currículo Inteligente V7

Data: 2026-09-04 BRT
Status: BACKEND FOUNDATION LIVE / FRONTEND EM PROMOÇÃO

## Objetivo de produto

Transformar o Career 360 de um painel funcional em uma experiência que surpreende positivamente o usuário:

`HISTÓRICO CONFIRMADO -> PERFIL PROFISSIONAL LSI -> CURRÍCULO INTELIGENTE -> DOWNLOAD/USO`

O produto não copia LinkedIn. Ele entrega utilidade semelhante de apresentação profissional com identidade, hierarquia visual, linguagem e componentes próprios da LSI.

## 1. Perfil Profissional LSI

Superfície prevista:
- foto de perfil opcional;
- nome completo;
- headline profissional;
- cargo atual;
- localização;
- resumo profissional;
- competências confirmadas;
- objetivos;
- trajetória confirmada;
- formação;
- idiomas;
- cursos/certificações;
- Proteção de Carreira.

Princípio:
`A PESSOA PRECISA SE RECONHECER NO PERFIL E SE SURPREENDER COM A QUALIDADE DA ORGANIZAÇÃO.`

## 2. Foto de perfil

Nova Edge Function LIVE:
`career-profile-photo`

Controles:
- JWT obrigatório;
- JPG/PNG/WebP;
- máximo 5 MB;
- validação por assinatura real do arquivo;
- SHA-256;
- bucket privado criado/gerenciado pelo backend;
- signed URL temporária para visualização pelo próprio usuário;
- substituição remove objeto anterior;
- exclusão pelo usuário;
- nenhum caminho bruto é exposto como URL pública permanente.

Regras duras:
- foto é opcional;
- foto NÃO participa do matching;
- foto NÃO altera FIT;
- foto NÃO é usada para inferir idade, raça, gênero, saúde ou qualquer atributo sensível;
- foto NÃO é exposta a empresa sem uma decisão explícita futura de identidade/disclosure;
- currículo PDF gerado começa com foto DESLIGADA por padrão; usuário decide se quer incluí-la.

Persistência:
`career_profile_media`
RLS: usuário lê apenas o próprio metadado; cliente não escreve diretamente.

## 3. Currículo Inteligente

Nova Edge Function LIVE:
`career-professional-profile`

Objetivo:
- reorganizar dados confirmados;
- produzir headline e resumo profissional mais claros;
- ordenar competências e evidências;
- preservar trajetória/formação/idiomas/certificações quando confirmados;
- gerar versões auditáveis;
- permitir ao usuário escolher uma versão principal.

Persistência:
`career_professional_profile_versions`

Cada versão guarda:
- número de versão;
- JSON profissional estruturado;
- hash das fontes confirmadas;
- status draft/accepted/superseded;
- datas.

Idempotência:
se as fontes confirmadas não mudaram, a geração reutiliza a versão com o mesmo `source_hash` em vez de criar duplicata.

## 4. Regra anti-fabricação

A inteligência pode:
- organizar;
- reescrever com clareza;
- priorizar informação;
- criar headline a partir de cargo/skills confirmados;
- transformar dados confirmados em resumo profissional;
- apontar lacunas.

A inteligência NÃO pode:
- promover cargo-alvo como se fosse cargo atual;
- inventar anos de experiência;
- inventar empresa;
- inventar resultado;
- inventar competência;
- inventar formação/certificação;
- inferir salário;
- inferir características sensíveis a partir de foto ou nome.

## 5. Experiência de download

Direção UX V7:
- botão `Gerar meu novo currículo`;
- preview `Seu Currículo Inteligente`;
- `Baixar PDF`;
- `Copiar resumo profissional`;
- `Usar esta versão como principal`;
- checkbox opcional `Incluir minha foto neste PDF`, DESLIGADO por padrão.

PDF é gerado no dispositivo do usuário a partir do perfil profissional estruturado, reduzindo exposição desnecessária de dados.

## 6. Próximo nível — currículo por oportunidade

Direção futura já prevista:
quando o radar automático encontrar uma oportunidade qualificada, o Career poderá criar:

`CURRÍCULO GERAL -> VERSÃO PARA A OPORTUNIDADE`

A adaptação apenas muda ênfase, ordem e redação de fatos confirmados. Nunca cria experiência para aumentar aderência.

## 7. Relação com LinkedIn

O Perfil Profissional LSI pode futuramente oferecer:
- headline pronta para copiar;
- seção Sobre pronta para copiar;
- bullets de experiência;
- competências recomendadas com base em fatos confirmados.

Não prometer alteração automática de LinkedIn sem integração oficialmente permitida.
Não copiar interface, métricas, ícones proprietários ou trade dress do LinkedIn.

## 8. Estado técnico verificado

Backend:
- migration `career_profile_media_and_generated_profiles_v1` = APPLIED;
- `career-profile-photo` = ACTIVE / JWT required;
- `career-professional-profile` = ACTIVE / JWT required;
- tabelas novas começaram com 0 registros, sem migração de dados privados existente.

Frontend V7 foi preparado localmente com:
- foto opcional no onboarding;
- página Perfil Profissional;
- preview de Currículo Inteligente;
- download PDF client-side;
- aceite de versão principal.

Não declarar FRONTEND_V7=LIVE até o deployment público ser validado no domínio oficial.

## Recovery

Novo chat: `Recovery LSI`.

`LAST_VERIFIED_CHANGE=PROFILE_PHOTO_PRIVATE_BACKEND_AND_PROFESSIONAL_PROFILE_VERSIONING_LIVE_FRONTEND_V7_PREPARED_NOT_YET_PROMOTED`
