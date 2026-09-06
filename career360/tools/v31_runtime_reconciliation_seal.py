from pathlib import Path
import re

REC=Path('docs/LSI_RECOVERY_CURRENT.md')
ROLE=Path('career360/releases/MASTER_PILOT_1_0_ROLE_GRAPH_V15_2026-09-05.md')
V16=Path('career360/releases/MASTER_PILOT_1_0_CLARITY_UI_V16_2026-09-06.md')

# Recovery
s=REC.read_text()
s=s.replace('`MATCH_ENGINE_V2=CHAMPION`\n`MATCH_ENGINE_V1=ROLLBACK`', '`MATCH_ENGINE_V31_ROLEGRAPH=CHAMPION`\n`MATCH_ENGINE_V2=ROLLBACK`\n`MATCH_ENGINE_V1=LEGACY_NOT_ROLLBACK`')

recon='''\n## 9B. Matching V3.1 — runtime reconciled\n\nA documentação anterior ficou stale após uma promoção real no Supabase. Pela regra `RUNTIME_COMPROVADO_VENCE_DOCUMENTO`, o histórico vivo foi auditado antes de qualquer rollback.\n\nMigration LIVE comprovada:\n`20260905183743 — career_matching_v31_promote_and_router`\n\nEla promoveu explicitamente:\n`MATCH_ENGINE_V31_ROLEGRAPH=CHAMPION`\n`MATCH_ENGINE_V2=ROLLBACK`\n\nControl plane atual:\n- `matching = v3.1-rolegraph / rollback v2.0 / active`;\n- `matching_role_graph = v3.1-rolegraph / rollback v2.0 / active`;\n- `matching_rolegraph_challenger = v2.1-rolegraph-challenger / paused`;\n- `role_graph = v1.1 / active`.\n\nEvidência registrada na promoção:\n- 7 synthetic positive cases;\n- 4 synthetic negative hard-gate cases;\n- corpus LIVE de 57;\n- 0 mudanças de classificação pré-promoção;\n- threshold 72;\n- role-fit floor 0.55.\n\nRevalidação viva em 2026-09-06:\n- 57 pares V2/V3.1;\n- 57/57 mesma classificação;\n- 0 mudanças de classe;\n- score: 3 subiram, 11 caíram, 43 iguais;\n- delta médio V3.1 - V2 = -0.69;\n- máximo +6.43; mínimo -7.50;\n- router não persistente confirmou `career_score_opportunity(...) == career_score_opportunity_v3(...)` no caso amostrado.\n\nFonte espelhada no GitHub:\n`career360/migrations/20260905183743_career_matching_v31_promote_and_router.sql`\ncommit `adb9f240b06c2d2ea1093eaf6a145f8836eac911`.\n\nReconciliação detalhada:\n`career360/docs/MATCHING_V31_RUNTIME_RECONCILIATION_2026-09-06.md`\ncommit `98a5c2566fb6c30c49788ea835d50f185162925d`.\n\nHardening de consumidores após a promoção:\n- `career-agent` V3 ACTIVE — SHA `0877ba595f53f680a2a926440aa0bfba59919460515501913cb1ae405eb36724`; source commit `b12ca88fcb38f5dcf7b3d8ef7e9cb01591f79a48`; lê apenas matches do champion;\n- `career-opportunity-research` V5 ACTIVE — SHA `c77784d8d50d3b861c8b9c61ede2ee385ef053d1d79da06e1305a84ac2bcbc40`; source commit `d2a2665c8823f1bbc10e4ad4d4cd94c8b2ea96a9`; mantém `role-search-v2` e calcula somente o champion via router canônico.\n\nEstados:\n`MATCHING_ROUTER_V31=LIVE`\n`CAREER_AGENT_CHAMPION_ISOLATION_V3=LIVE`\n`OPPORTUNITY_RESEARCH_CHAMPION_ALIGNMENT_V5=LIVE`\n`ROLE_SEARCH_PLAN_V2=LIVE`\n\nNenhum rollback foi executado: a promoção V3.1 foi comprovada como intencional e revalidada; o erro era documentação/consumidores stale.\n'''
if '## 9B. Matching V3.1 — runtime reconciled' not in s:
    marker='\n## 10. Radar / Matching\n'
    if marker not in s: raise SystemExit('Recovery matching marker missing')
    s=s.replace(marker,recon+marker,1)

s=s.replace('`CHAMPION=v2.0`\n`ROLLBACK=v1.0`', '`CHAMPION=v3.1-rolegraph`\n`ROLLBACK=v2.0`')
s=s.replace('Radar piloto: fontes estruturadas, rotação automática e `Pesquisar agora`.\n`AUTOMATED_OPPORTUNITY_RESEARCH=LIVE_PILOT_SCOPE`.', 'Radar piloto: fontes estruturadas, rotação automática e `Pesquisar agora`.\n`AUTOMATED_OPPORTUNITY_RESEARCH=LIVE_PILOT_SCOPE`.\n`career-opportunity-research` V5 usa o router do champion e mantém Role Search Plan V2; não executa challenger paralelo.')

pat=r'`LAST_VERIFIED_CHANGE=[^`]+`'
if len(re.findall(pat,s))!=1: raise SystemExit('Recovery LAST_VERIFIED_CHANGE cardinality')
s=re.sub(pat,'`LAST_VERIFIED_CHANGE=MATCHING_V31_ROLEGRAPH_CHAMPION_RUNTIME_RECONCILED_PROMOTION_MIGRATION_20260905183743_PROVEN_V2_ROLLBACK_CORPUS_57_OF_57_CLASS_STABLE_AGENT_V3_CHAMPION_ISOLATION_LIVE_RESEARCH_V5_CHAMPION_ALIGNMENT_LIVE_MAIL_RECEIPT_PRIMITIVES_LIVE_V16_FRONTEND_STILL_NOT_PROMOTED_VERCEL_CHAT_CONNECTOR_MUTATION_STILL_UNSCOPED_PRODUCTION_STILL_V14`',s,count=1)
REC.write_text(s)

# Role Graph release
r=ROLE.read_text()
r=r.replace('Status: ROLE GRAPH LIVE FOUNDATION / SEARCH PLAN LIVE / MATCHING V3 CHALLENGER / V2 REMAINS CHAMPION','Status: ROLE GRAPH V1.1 LIVE / SEARCH PLAN V2 LIVE / MATCHING V3.1 CHAMPION / V2 ROLLBACK')
new6='''## 6. Matching V3.1 — Champion\n\nFunção de engine:\n`career_score_opportunity_v3`\n\nRouter canônico:\n`career_score_opportunity`\n\nEngine LIVE:\n`v3.1-rolegraph`.\n\nO V3.1 preserva os hard gates do V2 para privacidade, salário, localização, modelo de trabalho e expiração, e usa Role Graph + scope + seniority no componente de cargo.\n\nPromoção comprovada no histórico vivo do Supabase:\n`20260905183743 — career_matching_v31_promote_and_router`.\n\nGovernança atual:\n- `MATCHING CHAMPION = v3.1-rolegraph`;\n- `ROLLBACK = v2.0`;\n- `ROLE GRAPH = v1.1 active`.\n\nEvidência de promoção registrada no runtime:\n- 7 casos sintéticos positivos;\n- 4 casos sintéticos negativos/hard-gate;\n- corpus 57;\n- 0 mudanças de classificação antes da promoção;\n- threshold 72;\n- role-fit floor 0.55.\n\nRevalidação 2026-09-06:\n- 57/57 pares V2/V3.1 mantiveram classificação;\n- 0 mudanças de classe;\n- scores: 3 subiram, 11 caíram, 43 ficaram iguais;\n- delta médio -0.69;\n- router genérico e V3.1 direto produziram o mesmo resultado no smoke não persistente amostrado.\n\nA migration viva foi espelhada em:\n`career360/migrations/20260905183743_career_matching_v31_promote_and_router.sql`.\n\nReconciliação detalhada:\n`career360/docs/MATCHING_V31_RUNTIME_RECONCILIATION_2026-09-06.md`.\n'''
r=re.sub(r'## 6\. Matching V3 — Challenger[\s\S]*?(?=\n## 7\.)',new6,r,count=1)
new8='''## 8. Radar V5\n\n`career-opportunity-research` V5 está ACTIVE.\n\nEm cada ciclo:\n1. lê champion/rollback do `career_engine_control`;\n2. mantém o Role Search Plan V2 pronto para usuários `agent_ready`;\n3. cada oportunidade nova/alterada é pontuada uma única vez pelo router canônico `career_score_opportunity`;\n4. telemetria registra `matching_engine`, `rollback_engine` e `champion_match_operations`;\n5. não existe mais execução paralela do antigo `v3.0-challenger` depois da promoção V3.1.\n\nSource commit:\n`d2a2665c8823f1bbc10e4ad4d4cd94c8b2ea96a9`.\n\nDeployed SHA:\n`c77784d8d50d3b861c8b9c61ede2ee385ef053d1d79da06e1305a84ac2bcbc40`.\n\nO `career-agent` V3 também foi alinhado ao champion para não somar linhas históricas de múltiplos engines.\nSource commit `b12ca88fcb38f5dcf7b3d8ef7e9cb01591f79a48`; deployed SHA `0877ba595f53f680a2a926440aa0bfba59919460515501913cb1ae405eb36724`.\n\nAs fontes ATS atuais fornecem boards completos; o Search Plan continua particularmente importante para matching e para futuras fontes keyword-based.\n'''
r=re.sub(r'## 8\. Radar V4[\s\S]*?(?=\n## 9\.)',new8,r,count=1)
r=r.replace('7. manter champion/challenger até V3 provar ganho real.','7. manter V2 como rollback operacional e revalidar V3.1 em corpus crescente antes de qualquer V4.')
r=r.replace('- não promover V3 antes do benchmark;','- não promover uma nova versão de matching sem benchmark e rollback comprovados;')
r=re.sub(r'`LAST_VERIFIED_CHANGE=[^`]+`','`LAST_VERIFIED_CHANGE=ROLE_GRAPH_V11_SEARCH_PLAN_V2_LIVE_MATCHING_V31_ROLEGRAPH_CHAMPION_V2_ROLLBACK_CORPUS_57_CLASS_STABLE_AGENT_V3_AND_RESEARCH_V5_ALIGNED`',r,count=1)
ROLE.write_text(r)

# V16 release append reconciliation summary
v=V16.read_text()
sec='''\n## Matching V3.1 runtime reconciliation\n\nA stale-documentation mismatch was found while continuing V16 readiness work. Live Supabase migration history proves that matching V3.1 was intentionally promoted on `20260905183743` with V2 retained as rollback.\n\nCurrent matching state:\n`MATCH_ENGINE_V31_ROLEGRAPH=CHAMPION`\n`MATCH_ENGINE_V2=ROLLBACK`\n\nCurrent-corpus revalidation: 57/57 V2/V3.1 pairs preserve classification; zero class changes.\n\nConsumers hardened after reconciliation:\n- `career-agent` V3 ACTIVE, champion-only match reads;\n- `career-opportunity-research` V5 ACTIVE, one champion router call per changed opportunity + Role Search Plan V2.\n\nCanonical evidence:\n`career360/docs/MATCHING_V31_RUNTIME_RECONCILIATION_2026-09-06.md`.\n\nThis backend matching reconciliation does not promote the V16 frontend.\n'''
if '## Matching V3.1 runtime reconciliation' not in v:
    marker='\n## Deployment state\n'
    if marker not in v: raise SystemExit('V16 Deployment state marker missing')
    v=v.replace(marker,sec+marker,1)
V16.write_text(v)

print('V31_RUNTIME_RECONCILIATION_DOCS_SEAL=PASS')
