from pathlib import Path
import re

REC=Path('docs/LSI_RECOVERY_CURRENT.md')
REL=Path('career360/releases/MASTER_PILOT_1_0_CLARITY_UI_V16_2026-09-06.md')

SOURCE_COMMIT='96cd4254eb972e8267e0bf3d39e37cf0da86f72c'
EDGE_SHA='aa677838765e62fe683309fee53832a9b36cf0e8d0bd176a773e1eee8300e83f'

s=REC.read_text()

# Add explicit live state once.
anchor='`PROACTIVE_AGENT_CORE_V12=LIVE`\n`PROACTIVE_UI_V12=LIVE`\n'
insert='`PROACTIVE_AGENT_CORE_V12=LIVE`\n`PROACTIVE_UI_V12=LIVE`\n`PROACTIVE_DIGEST_TRUTH_V2=LIVE`\n'
if '`PROACTIVE_DIGEST_TRUTH_V2=LIVE`' not in s:
    if anchor not in s: raise SystemExit('global proactive state anchor missing')
    s=s.replace(anchor,insert,1)

# Add backend truth hardening under V12, before V13.
section='''\n### V12 truthfulness hardening — digest V2 LIVE\n\n`career-proactive-digest` foi promovida para V2 após readback vivo do código publicado.\n\nEvidência canônica:\n- source commit: `96cd4254eb972e8267e0bf3d39e37cf0da86f72c`;\n- Supabase Edge Function: `career-proactive-digest` V2 `ACTIVE`;\n- deployed `ezbr_sha256`: `aa677838765e62fe683309fee53832a9b36cf0e8d0bd176a773e1eee8300e83f`;\n- empty-state factual: `Nenhuma novidade relevante foi registrada nesta janela.`;\n- frase antiga `seu agente continua ativo` removida do código publicado por não constituir prova de atividade;\n- autenticação preservada: cron exige secret validado por `career_validate_proactive_cron_secret`; ação manual exige `Bearer` validado por `auth.getUser()`.\n\nEstado:\n`PROACTIVE_DIGEST_TRUTH_V2=LIVE`\n\nEsse LIVE é exclusivamente do backend de digest. Não altera o gate de promoção da UI V15/V16.\n'''
marker='\n## 5. V13 — Meu Perfil Visual LIVE\n'
if '### V12 truthfulness hardening — digest V2 LIVE' not in s:
    if marker not in s: raise SystemExit('V13 marker missing')
    s=s.replace(marker,section+marker,1)

# Add read-only Supabase security audit before redirect discussion in section 12.
sec12='''\n### Supabase security readiness — read-only audit 2026-09-06\n\nAuditoria viva, sem mutação de banco:\n- 43/43 tabelas ordinárias do schema `public` com RLS habilitado e pelo menos uma policy;\n- policies de dados do usuário verificadas com `auth.uid() = user_id`; UPDATEs auditados possuem `USING` + `WITH CHECK` quando aplicável;\n- funções `SECURITY DEFINER` do schema `public`: `EXECUTE=false` para PUBLIC/anon/authenticated e `EXECUTE=true` para service_role;\n- `search_path` explicitamente configurado nas funções privilegiadas auditadas;\n- nenhuma view/materialized view encontrada no schema `public`;\n- buckets `career-profile-private` e `career-resumes-quarantine` permanecem `public=false`;\n- `storage.objects` com RLS habilitado e sem policy direta para cliente, mantendo acesso privilegiado pelas Edge Functions;\n- funções sem `verify_jwt` auditadas usam autenticação interna apropriada (secret validado, sessão/master quando aplicável) ou são redirect-only;\n- media/foto e documentos auditados vinculam operações privilegiadas ao `user_id` autenticado.\n\nAdvisor atual:\n- Security: somente `auth_leaked_password_protection=DISABLED/WARN`;\n- Performance: somente INFOs de unused indexes esperados no piloto; sem duplicate-index/unindexed-FK WARN.\n\nEstado:\n`SUPABASE_SECURITY_READINESS_READ_ONLY_AUDIT=PASS`\n\nLimites conhecidos permanecem:\n`LEAKED_PASSWORD_PROTECTION=KNOWN_PLAN_LIMITATION_NOT_UPGRADED`\n`SUPABASE_SERVER_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`\n'''
redirect_anchor='Redirect de confirmação usado pelo cliente:\n'
if '### Supabase security readiness — read-only audit 2026-09-06' not in s:
    if redirect_anchor not in s: raise SystemExit('redirect anchor missing')
    s=s.replace(redirect_anchor,sec12+'\n'+redirect_anchor,1)

# Refresh last verified change while preserving frontend not-promoted truth.
pat=r'`LAST_VERIFIED_CHANGE=[^`]+`'
if len(re.findall(pat,s))!=1: raise SystemExit('LAST_VERIFIED_CHANGE cardinality')
last='`LAST_VERIFIED_CHANGE=PROACTIVE_DIGEST_TRUTH_V2_LIVE_SOURCE_96CD425_EDGE_SHA_AA677838_SUPABASE_SECURITY_READINESS_READ_ONLY_PASS_43_OF_43_PUBLIC_TABLES_RLS_SERVICE_ONLY_SECURITY_DEFINER_PRIVATE_STORAGE_V16_FRONTEND_STILL_NOT_PROMOTED_VERCEL_CHAT_CONNECTOR_MUTATION_STILL_UNSCOPED_PRODUCTION_STILL_V14`'
s=re.sub(pat,last,s,count=1)
REC.write_text(s)

r=REL.read_text()
relsec='''\n## Backend truthfulness alignment\n\nThe proactive backend was audited against the V16 truthfulness policy before UI promotion.\n\n`career-proactive-digest` V2 is LIVE with a factual no-event state:\n`Nenhuma novidade relevante foi registrada nesta janela.`\n\nEvidence:\n- canonical source commit `96cd4254eb972e8267e0bf3d39e37cf0da86f72c`;\n- deployed Edge Function V2 `ACTIVE`;\n- deployed SHA `aa677838765e62fe683309fee53832a9b36cf0e8d0bd176a773e1eee8300e83f`;\n- legacy claim `seu agente continua ativo` absent from deployed source;\n- cron-secret and authenticated-user authorization paths preserved.\n\n`PROACTIVE_DIGEST_TRUTH_V2=LIVE`\n\nThis backend LIVE state does not promote the V16 frontend.\n\n## Supabase security readiness read-only audit\n\nBefore promotion, the live project was audited without schema/data mutation:\n- 43/43 ordinary public tables have RLS enabled and at least one policy;\n- audited user-owned policies bind access to `auth.uid() = user_id`;\n- public `SECURITY DEFINER` functions are not executable by PUBLIC, anon, or authenticated; service_role retains execution;\n- no public views/materialized views were found;\n- both Career 360 storage buckets are private and direct storage object access remains RLS-gated;\n- audited unauthenticated-at-edge functions enforce internal secrets/session/master checks as appropriate, except the redirect-only app function;\n- photo/media/document privileged paths were verified to scope ownership by authenticated user id.\n\nKnown limitations remain unchanged:\n- leaked-password protection is disabled on the current plan;\n- hosted Supabase Auth redirect allowlist is not exposed by the available connector and remains `NOT_YET_PROVEN`.\n\n`SUPABASE_SECURITY_READINESS_READ_ONLY_AUDIT=PASS`\n'''
marker='\n## Deployment state\n'
if '## Backend truthfulness alignment' not in r:
    if marker not in r: raise SystemExit('release deployment marker missing')
    r=r.replace(marker,relsec+marker,1)
REL.write_text(r)
print('V16_BACKEND_TRUTH_SECURITY_SEAL=PASS')
