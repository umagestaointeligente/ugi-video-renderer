# LSI — RECOVERY POINTER

Status: CANÔNICO / LOCALIZADOR ESTÁVEL

Comando de recuperação entre chats:

`LSI::RECOVERY::CURRENT`

## Como recuperar

1. Ler este ponteiro no `main`.
2. O estado CURRENT do LSI está atualmente sendo desenvolvido na branch:
   `lsi-career360-beta1-foundation-20260902`
3. Nessa branch, ler nesta ordem:
   - `docs/LSI_CANONICAL_INDEX.md`
   - `docs/LSI_RECOVERY_CURRENT.md`
   - manifesto indicado por `CURRENT_FOCUS` (atualmente `docs/projects/LSI_CAREER360.md`)
4. Ler documentos especializados somente quando o manifesto indicar necessidade.
5. Quando estado operacional vivo importar, fazer readback da fonte/runtime antes de declarar PASS/READY/LIVE.

Resposta esperada do chat novo na primeira linha:

`LSI_RECOVERY=TRUE`

## Regra

Este arquivo é apenas um LOCALIZADOR. Não duplicar o snapshot CURRENT aqui.
Código/protótipo Career permanece isolado da produção até promoção pelos gates.

Quando a branch CURRENT mudar ou o conteúdo for promovido para `main`, atualizar somente este ponteiro.
