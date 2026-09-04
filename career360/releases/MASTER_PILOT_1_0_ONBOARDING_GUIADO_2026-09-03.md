# LSI Career 360 — Onboarding Guiado do Master Pilot 1.0

Data: 2026-09-03 BRT
Status: IMPLEMENTADO E PUBLICADO

## Objetivo

Reduzir carga cognitiva no primeiro uso e transformar o onboarding em uma experiência guiada, visual e progressiva.

Princípio preservado:
`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`

## Novo fluxo visual

Depois do login, quando `onboarding_status != agent_ready`, a pessoa entra em um passo a passo de 5 etapas:

1. **Sobre você**
   - nome;
   - cargo atual;
   - cidade;
   - UF.

2. **Seu objetivo**
   - cargos procurados;
   - localizações aceitas;
   - salário mínimo opcional;
   - salário alvo opcional.

3. **Proteção de Carreira**
   - situação de emprego atual;
   - empregador atual;
   - proteção do empregador atual;
   - empresas adicionais bloqueadas.

4. **Competências**
   - competências principais confirmadas pelo usuário.

5. **Currículo — agora ou depois**
   - PDF textual ou DOCX até 10 MB;
   - currículo é opcional para ativar o agente;
   - usuário pode incluir depois;
   - interface explica que o currículo ajuda a organizar/preencher automaticamente dados que ainda serão confirmados.

## Experiência

- barra de progresso 1/5;
- botões Próximo / Voltar;
- opção Continuar depois;
- no último passo, opção Fazer depois;
- estado temporário do passo a passo preservado em `sessionStorage`;
- Home mostra lembrete `Termine de preparar seu agente` para quem interromper;
- Minha Carreira permite revisar os dados e adicionar currículo posteriormente.

## Currículo

O upload continua usando o pipeline seguro já aprovado:
`QUARANTINE -> DEEP VALIDATION -> DRAFT -> HUMAN CONFIRMATION`.

Quando o parser encontra dados no currículo, o frontend só utiliza resultados para sugerir/preencher campos vazios. Nenhuma inferência vira fato sem confirmação.

## Login/senha

Mantido o controle mostrar/ocultar senha (olho) nos campos de senha e confirmação.

## Frontend

Domínio oficial:
`https://lsi-career-360.vercel.app/`

A versão guiada foi publicada como página autocontida (HTML + CSS + JS inline) para reduzir risco de falha de assets em navegadores móveis.

Validação após deploy:
- HTTP 200;
- `Content-Type: text/html; charset=utf-8`;
- conteúdo do onboarding guiado presente no domínio oficial.

## Estado mestre

A conta mestre real já criada permanece preservada:
- e-mail confirmado;
- role `master`;
- onboarding ainda pode ser concluído pelo novo fluxo guiado.

## Pendência antes de Beta pública

A configuração global do Supabase Auth para `Site URL` / allowlist de Redirect URLs ainda deve ser alinhada explicitamente ao domínio oficial. O frontend já envia `emailRedirectTo` para a URL oficial, mas não considerar configuração global concluída sem evidência do provider.

## Recovery

Em novo chat: `Recovery LSI`.

Última alteração funcional relevante:
`GUIDED_ONBOARDING_V5_LIVE`.