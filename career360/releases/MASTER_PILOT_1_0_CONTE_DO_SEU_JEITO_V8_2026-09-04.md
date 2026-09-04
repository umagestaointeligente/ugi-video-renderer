# LSI Career 360 — Conte do Seu Jeito V8

Data: 2026-09-04 BRT
Status: BACKEND LIVE / FRONTEND A INCORPORAR NA PRÓXIMA PROMOÇÃO

## Objetivo

Adicionar uma etapa opcional para o usuário contar, por voz ou texto, aspectos da sua trajetória, liderança, estilo de trabalho, preferências e pontos fortes que não aparecem bem em um currículo tradicional.

Fluxo canônico:
`FALAR OU ESCREVER -> TRANSCRIÇÃO/TEXTO -> ORGANIZAÇÃO PROFISSIONAL -> MOSTRAR AO USUÁRIO -> APROVAR/AJUSTAR/DESCARTAR -> USAR NO PERFIL/CURRÍCULO`

Regra central:
`NADA VIRA FATO OU TEXTO OFICIAL SEM APROVAÇÃO DO USUÁRIO.`

## Experiência desejada

Card de onboarding/perfil:
**Conte do seu jeito**

Ações:
- `🎙️ Falar`
- `✍️ Escrever`
- `Agora não`

Depois da entrada:
- mostrar `Você contou`;
- mostrar `Nós organizamos assim`;
- permitir `Está perfeito`, `Quero ajustar`, `Tentar outra versão`, `Não usar`.

## Comece por aqui — sugestões dinâmicas

A pessoa não deve receber um campo vazio sem orientação.

Nova ação backend:
`career-personal-narrative -> action=prompts`

A função consulta somente contexto profissional necessário do próprio usuário:
- cargo atual;
- cargos-alvo.

A partir disso, devolve sugestões contextualizadas.

Exemplos universais:
- `Sou o tipo de profissional que...`
- `Uma coisa que faço muito bem é...`
- `No trabalho, eu gosto especialmente de...`
- `As pessoas costumam me procurar quando precisam de...`
- `Um desafio que eu gosto de resolver é...`

Exemplos para liderança/gestão:
- `Quando lidero uma equipe, eu procuro...`
- `Meu jeito de desenvolver pessoas é...`
- `Quando preciso tomar uma decisão difícil, eu...`

Exemplos para comercial/compras/categorias:
- `Em uma negociação importante, meu ponto forte é...`
- `Eu gosto de transformar dados de mercado em...`
- `Quando uma categoria ou negócio precisa melhorar resultado, eu começo por...`

Também existem conjuntos contextuais iniciais para tecnologia/produto, RH/People, finanças e operações.

UX recomendada:
- mostrar apenas 3 sugestões de cada vez em `Comece por aqui`;
- botão `Quero mais ideias` revela outras;
- depois da primeira resposta, oferecer temas como Liderança, Resultados, Decisão, Transformação, Pontos fortes, Jeito de trabalhar, Motivação, Aprendizados e Próximo passo;
- nunca exigir que o usuário responda todas.

Objetivo: estimular lembranças e evidências úteis sem transformar a experiência em entrevista ou formulário longo.

## Voz

Direção zero-cash para o piloto:
- usar reconhecimento de voz do navegador/dispositivo quando suportado;
- LSI recebe o texto transcrito, não precisa armazenar o áudio bruto;
- interface deve informar que a transcrição por voz pode depender do serviço de reconhecimento do navegador/dispositivo;
- fallback sempre disponível por texto.

## Backend LIVE

Migration aplicada:
`career_personal_narratives_v1`

Tabela:
`career_personal_narratives`

Edge Function:
`career-personal-narrative`

Status:
`ACTIVE / JWT_REQUIRED / VERSION=3`

Ações suportadas:
- `prompts` — devolve sugestões baseadas em cargo atual + cargos-alvo;
- `generate` — cria rascunho que exige confirmação;
- `accept` — aceita texto proposto ou texto editado pelo usuário;
- `reject` — descarta.

Modos de origem:
- `text`;
- `voice_transcript`.

## Minimização de dados

Migration adicional aplicada:
`career_personal_narratives_minimize_raw_v1`

Após aceite:
- texto bruto/original é removido do registro;
- permanece a versão profissional aceita;
- audit event registra que houve confirmação e limpeza do bruto.

Após rejeição:
- texto bruto também é limpo.

Assim o sistema não precisa conservar indefinidamente uma fala espontânea que possa conter informação desnecessária ou sensível.

## Integração com Perfil Profissional

`career-professional-profile` foi promovida para V2.

Ela consulta a narrativa pessoal mais recente com `status=accepted`.
Somente essa versão aprovada pode alimentar o resumo do Perfil Profissional e, futuramente, o Currículo Inteligente.

O source hash do perfil inclui a narrativa aceita, portanto uma alteração aprovada pode gerar nova versão do Perfil Profissional sem sobrescrever silenciosamente a anterior.

## Limite de inteligência no modo zero-cash atual

A transformação inicial é conservadora/determinística:
- remove vícios orais básicos;
- normaliza pontuação/espaços;
- preserva o sentido original;
- não inventa fatos;
- sugere temas de carreira apenas como apoio visual;
- sugestões de conversa são orientadas ao cargo, não afirmações sobre o usuário.

Em níveis futuros de inteligência, uma camada de linguagem mais sofisticada poderá propor redações melhores, desde que continue submetendo tudo à aprovação do usuário e nunca fabrique experiência.

## Próximo passo de frontend

Incorporar esta etapa na próxima promoção visual junto com Perfil Profissional + Currículo Inteligente.

Frontend esperado:
- bloco `Comece por aqui` com 3 chips contextuais;
- `Quero mais ideias`;
- `🎙️ Falar` / `✍️ Escrever`;
- comparação `Você contou` x `Nós organizamos assim`;
- aprovação/ajuste/descarte.

Não declarar `CONTE_DO_SEU_JEITO_FRONTEND=LIVE` antes de deploy e validação no domínio oficial.

## Recovery

Novo chat: `Recovery LSI`.

`LAST_VERIFIED_CHANGE=PERSONAL_NARRATIVE_V3_ROLE_AWARE_PROMPTS_LIVE_USER_CONFIRMATION_REQUIRED_RAW_TEXT_MINIMIZED_PROFILE_GENERATOR_USES_ONLY_ACCEPTED_NARRATIVE_FRONTEND_PENDING`
