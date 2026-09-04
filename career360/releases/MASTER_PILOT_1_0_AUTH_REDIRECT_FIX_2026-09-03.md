# LSI Career 360 — Correção de confirmação de e-mail e senha

Data: 2026-09-03 BRT
Status: IMPLEMENTADO NO FRONTEND / PROVIDER URL CONFIG A VALIDAR

## Incidente observado

Após criação da conta e confirmação do e-mail, o Supabase redirecionou o usuário para `http://localhost:3000`, causando `ERR_CONNECTION_REFUSED` no celular.

O cadastro não foi perdido. A confirmação de e-mail ocorreu corretamente no backend.

## Causa

O projeto nasceu com configuração de desenvolvimento em que o Site URL padrão do Supabase Auth ainda apontava para localhost. O frontend também não informava explicitamente um destino de confirmação no `signUp` inicial.

## Correções aplicadas no frontend hospedado

1. Cadastro agora envia `emailRedirectTo` explicitamente para:
   `https://lsi-career-360.vercel.app/?email-confirmado=1`
2. A tela reconhece `email-confirmado=1` e orienta o usuário a entrar.
3. Campos de senha e confirmação ganharam controle mostrar/ocultar senha (olho).
4. Mensagens permanecem em português.
5. App segue autocontido em uma única página para reduzir falhas de assets em mobile.

## Estado do usuário mestre testado

- e-mail confirmado = TRUE;
- role = `master`;
- onboarding = `started`.

## Observação de governança

A configuração global de `Site URL` / `Redirect URLs` do Supabase Auth deve permanecer alinhada ao domínio oficial da aplicação. O frontend não deve depender de localhost em produção.

## Domínio oficial do piloto

`https://lsi-career-360.vercel.app/`

## Recovery

Em novo chat: `Recovery LSI`.
