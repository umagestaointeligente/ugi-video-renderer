# LSI Career 360 — Master Pilot 1.0 — Intelligence + UX V11.1

Data: 2026-09-04 BRT
Status: `LIVE_MASTER_PILOT_SCOPE`

## Objetivo

Reduzir densidade visual da experiência diária e aumentar a qualidade real do agente antes de ampliar o piloto.

## Produção

Frontend oficial:
`https://lsi-career-360.vercel.app/`

Deployment V11.1:
`dpl_EjNc9WzK1uPCZFWhY8ympukcAMGG`

Commit do módulo V11.1 carregado pelo HTML oficial:
`2bff879b2b2a99815ed3933009f9a6a19a8a9501`

Rollback V11:
`dpl_59kEVUkAGkkZZXfRcRP9p4duWoSF`

## UX V11.1

Minha Página passa a priorizar leitura:
- resumo compacto com `Ver mais`;
- competências em chips;
- Destaques profissionais em blocos curtos;
- Liderança e escopo separado;
- Experiência compacta;
- Formação compacta;
- mobile reduz ainda mais os blocos da primeira leitura.

A edição continua disponível, mas não domina o fluxo diário.

## Smart CV V11.1

PDF client-side agora suporta:
- resumo profissional;
- Destaques profissionais;
- Liderança e escopo;
- competências;
- experiência;
- formação;
- idiomas;
- cursos/certificações.

Foto:
- continua opcional;
- checkbox desligado por padrão;
- quando ativado, a foto privada autorizada é convertida localmente para JPEG antes da inclusão no PDF;
- foto nunca participa de matching/FIT.

## Parser 1.0.3

`career360-edge-parser/1.0.3 = ACTIVE`

Corrige mistura estrutural observada no parser anterior e reconhece separadamente:
- resumo;
- impactos/destaques;
- transformações de negócio;
- liderança/escopo;
- trajetória profissional;
- formação;
- competências;
- idiomas;
- certificações.

QA do corpus real usado para validar o parser:
- 1 resumo;
- 4 impactos executivos;
- 10 linhas de transformações/resultados;
- 3 linhas de liderança/escopo;
- 3 linhas de trajetória profissional.

Nada extraído vira fato sem confirmação.

## Perfil Profissional V3

`career-professional-profile = ACTIVE / V3`

Novas propriedades estruturadas:
- `highlights`;
- `leadership`;
- `experience`;
- `education`;
- `languages`;
- `certifications`.

Fonte permitida:
- perfil confirmado;
- preferências confirmadas;
- competências confirmadas;
- último currículo `confirmed`;
- narrativa `accepted`.

## Matching V2

Governança:
`CHAMPION=v2.0`
`ROLLBACK=v1.0`

V2 acrescenta interpretação de:
- família profissional bilíngue/conceitual;
- senioridade;
- similaridade lexical;
- competências quando disponíveis;
- localização/modelo/setor.

QA de promoção: 6/6 casos esperados passaram.

Migrations versionadas:
- `20260904_matching_v2_control_and_helpers.sql`;
- `20260904_matching_v2_score.sql`.

## Region Filter V2 / Radar

Problema corrigido:
menções genéricas a Brasil/LATAM em textos institucionais não podem fazer uma vaga global aparecer como brasileira.

Saneamento comprovado no piloto:
- 126 oportunidades ativas antes do filtro;
- 70 expiradas como ruído regional;
- 56 permaneceram no recorte piloto;
- zero qualificada para o perfil mestre naquele checkpoint.

Regra de produto:
`ZERO QUALIFICADA É MELHOR DO QUE VAGA ERRADA.`

## Evidência operacional

- Vercel deployment `READY`;
- target `production`;
- alias oficial presente;
- `aliasError=null`;
- domínio oficial responde HTTP 200;
- HTML oficial referencia o módulo V11.1 exato;
- Vercel Runtime Errors: nenhum erro no período verificado.

GitHub CI:
- nenhum status/check associado ao commit V11.1 no checkpoint consultado;
- portanto `CI_PASS` não é declarado.

Security Advisor:
- sem lint estrutural de RLS pendente no checkpoint atual;
- permanece `auth_leaked_password_protection=DISABLED/WARN`.

## Não incluído nesta release

- Professional Photo Studio image-to-image;
- Beta pública;
- Career Learning Engine;
- currículo adaptado automaticamente por oportunidade;
- catálogo amplo de empregadores;
- resolução do WARN de leaked-password protection.

## Próximo gate humano

Abrir o domínio oficial autenticado em mobile e validar:
1. Minha Página;
2. leitura de resumo;
3. foto;
4. geração de novo Perfil/CV;
5. PDF sem foto;
6. PDF com foto opt-in;
7. Radar;
8. fluxo de edição secundário.
