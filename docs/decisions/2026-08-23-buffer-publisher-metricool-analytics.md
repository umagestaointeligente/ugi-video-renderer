# ADR — UGI Publishing and Analytics Role Separation

Date: 2026-08-23
Status: ACCEPTED

## Decision
For UGI, Buffer is the sole official scheduler and publisher. Metricool is restricted to analytics-only, read-only use.

## Context
UGI experienced unreliable publication behavior when Metricool was used as a scheduling/publishing path. Buffer has been the stable publication path in the validated UGI workflow. To prevent future chats, operators or tools from reintroducing the same error, provider roles are now explicitly isolated.

## Rules
- Buffer: schedule, queue, publish, retry/recovery, publication status and readback.
- Metricool: analytics, performance metrics, timing signals and historical analysis only.
- Metricool must never create, update, schedule, reschedule, queue, publish or retry UGI posts.
- There is no Metricool publishing fallback.
- If Buffer is unavailable or publication cannot be proven, the slot is BLOCKED/NOT_PROVEN.
- Any future replacement of Buffer requires a new ADR, smoke test, rollback plan and policy update before production use.

## Verification sources
- docs/LOLA-PROJECT-CONTROL-PLANE.md
- config/ugi/growth-policy.json
- config/ugi/integration-routing.json

## Consequence
All UGI automation and future-chat handoffs must resolve provider roles from these persisted files before scheduling or publishing content.