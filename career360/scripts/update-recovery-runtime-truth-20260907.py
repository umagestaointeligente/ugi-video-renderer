from pathlib import Path

p = Path('docs/LSI_RECOVERY_CURRENT.md')
s = p.read_text()

s = s.replace('Atualizado: 2026-09-06 BRT', 'Atualizado: 2026-09-07 BRT', 1)
old_status = '`CURRENT_STATUS=V14_PRODUCTION_STABLE_V15_V16_BROWSER_VALIDATED_BUNDLE_PINNED_WAITING_IN_CHAT_PROJECT_SCOPED_VERCEL_MUTATION`'
new_status = '`CURRENT_STATUS=V14_OFFICIAL_PRODUCTION_STABLE_V16_CLOUDFLARE_BROWSER_VALIDATED_ALTERNATIVE_DELIVERY_PROVEN_NOT_PROMOTED`'
if old_status not in s:
    raise SystemExit('HARD_STOP_CURRENT_STATUS_ANCHOR_MISSING')
s = s.replace(old_status, new_status, 1)
s = s.replace('`ROLE_INTELLIGENCE_V2_CHAMPION_ALIGNED=LIVE`', '`ROLE_INTELLIGENCE_V3_CHAMPION_ALIGNED=LIVE`', 1)

anchor = '`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`'
block = '''`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`
`CLOUDFLARE_V16_STATIC_PREVIEW=LIVE_VALIDATED_NOT_OFFICIAL`
`CLOUDFLARE_V16_BROWSER_PRELOGIN=PASS`
`CLOUDFLARE_FRONTEND_DELIVERY_ALTERNATIVE=PROVEN`
`VERCEL_NO_LONGER_SINGLE_FRONTEND_DELIVERY_PATH=TRUE`
`AUTH_EMAIL_CONFIRMATION_EXISTING_RUNTIME_USER=PASS`
`AUTH_REDIRECT_LOCALHOST=UX_BUG_NOT_CURRENT_CONFIRMATION_INTEGRITY_BLOCKER`
`SUPABASE_SERVER_REDIRECT_ALLOWLIST=NOT_YET_PROVEN_OR_MUTABLE_IN_APP`
`SUPABASE_MANAGEMENT_TOKEN_ROUTE=NOT_AVAILABLE`
`MATCH_ROUTER_V31_CROSS_REGRESSION=PASS_57_OF_57`
`MASTER_METRICS_CHAMPION_ALIGNMENT=PASS_57_EQ_57`
`RLS_PUBLIC_TABLES=PASS_47_OF_47_WITH_POLICY`
`SECURITY_DEFINER_ACL=PASS_51_ZERO_PUBLIC_ANON_AUTH_EXEC`
`SECURITY_ADVISOR=KNOWN_WARN_LEAKED_PASSWORD_PROTECTION_PLAN_LIMITATION`
`PERFORMANCE_ADVISOR=INFO_UNUSED_INDEXES_ONLY`
`ONET_V31_BULK=LIVE_DIAGNOSTIC_EVIDENCE_ONLY`
`LSI_ROUTE_COUNCIL_LLAMA=LIVE_PROVEN`
`LSI_GEMMA_GLM=DEGRADED_EMPTY_OUTPUT_NOT_CHAMPION`'''
if anchor not in s:
    raise SystemExit('HARD_STOP_GATE_ANCHOR_MISSING')
s = s.replace(anchor, block, 1)

marker = '## 3. Princípios duros'
insert = '''## 2A. Runtime truth seal — 2026-09-07

Documento de evidência detalhada:
`career360/docs/RUNTIME_TRUTH_HARDENING_2026-09-07.md`

Últimas provas vivas:
- LSI Llama fallback: run `34063813926`, 4/4 PASS, 4245 ms;
- Cloudflare static preview: run `34064086287` SUCCESS;
- Cloudflare browser smoke: run `34084862777`, job `101626832212`, 360/412/768/1180 PASS, runtime errors zero;
- official production promotion: NONE; Vercel V14 continua oficial;
- matching router vs V3.1: 57/57 exact, 0 mismatch;
- master metrics matches = champion matches = 57;
- public ordinary tables RLS+policy = 47/47;
- SECURITY DEFINER = 51, execute PUBLIC/anon/authenticated = 0, fixed search_path = 51/51;
- Security Advisor: somente WARN known `auth_leaked_password_protection`;
- Performance Advisor: somente INFO unused indexes;
- `career-role-intelligence` V3 ACTIVE SHA `54b68a6fbaf4d6e7831adcf7a42abd6871f18dab3b18a59cabf5a1e1012194da`;
- O*NET v31 = `live_bulk`, diagnostic evidence only, no auto-promotion;
- `auth.users`: 1 total, 1 confirmed, 1 signed-in; localhost redirect permanece UX bug;
- Supabase Management API token candidates em GitHub secrets = 0/6;
- applications/followups/mail_actions = 0/0/0; mail delivery continua PAUSED.

Regra: Cloudflare é rota alternativa comprovada; não substituir o frontend oficial nem abrir Beta sem gate explícito de promoção.

'''
if marker not in s:
    raise SystemExit('HARD_STOP_SECTION_ANCHOR_MISSING')
s = s.replace(marker, insert + marker, 1)

p.write_text(s)
