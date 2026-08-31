import fs from 'node:fs';

const statePath = process.argv[2] || 'greenfield/payment-hub/provider-state-r1.json';
const probePath = process.argv[3] || null;
const outPath = process.argv[4] || 'generated/evidence/lsi-payment-route-council-r1.json';
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const probe = probePath && fs.existsSync(probePath) ? JSON.parse(fs.readFileSync(probePath, 'utf8')) : {};

function score(p) {
  let s = 0;
  if (p.live_receive_verified) s += 55;
  if (p.checkout_e2e_verified) s += 15;
  if (p.programmatic_checkout) s += 18;
  if (p.zero_incremental_cost_path) s += 12;
  if (p.connected) s += 10;
  if (!p.human_financial_onboarding_blocker) s += 8;
  if (!p.custody_or_private_key_blocker) s += 8;
  if (p.blocker) s -= 10;
  if (p.custody_or_private_key_blocker) s -= 20;
  if (p.human_financial_onboarding_blocker) s -= 12;
  return Math.max(0, Math.min(100, s));
}

function actionFor(p) {
  if (p.id === 'asaas_direct') {
    return p.checkout_e2e_verified === true || probe.asaas_checkout_e2e === true
      ? 'ROUTE_GREENFIELD_PRODUCT_REGISTRY_VIA_VERIFIED_ASAAS_RAIL'
      : 'RUN_ZERO_VALUE_MOVEMENT_E2E_CHECKOUT_PROBE';
  }
  if (p.id === 'x402_direct_base_usdc') return 'WAIT_FOR_USER_CONTROLLED_PAYTO_ADDRESS';
  if (p.id === 'apify_agentic_x402') return 'PREPARE_ACTOR_AND_STOP_ONLY_AT_KYC';
  if (p.id === 'stripe_checkout') return 'KEEP_ADAPTER_READY_AND_STOP_ONLY_AT_LIVE_ACCOUNT_ACTIVATION';
  if (p.id === 'rapidapi_marketplace') return 'PREPARE_PROVIDER_PACKAGE_AND_STOP_ONLY_AT_PAYOUT_SETUP';
  if (p.id === 'kiwify_marketplace') return 'HOLD_PRODUCT_PUBLICATION_AT_DASHBOARD_BOUNDARY_AND_PREPARE_API_RECONCILIATION';
  if (p.id === 'shopee_affiliate') return 'VERIFY_PAYOUT_READINESS_BEFORE_CLASSIFYING_RECEIVABLE';
  return 'RESEARCH';
}

const ranked = state.providers.map(p => ({
  id: p.id,
  rail: p.rail,
  score: score(p),
  status: p.live_receive_verified ? 'LIVE' : (p.blocker ? 'BLOCKED_OR_PARTIAL' : 'READY_TO_TEST'),
  blocker: p.blocker,
  next_action: actionFor(p),
  evidence: p.evidence
})).sort((a,b) => b.score - a.score || a.id.localeCompare(b.id));

const humanOnly = new Set([
  'WAIT_FOR_USER_CONTROLLED_PAYTO_ADDRESS',
  'KEEP_ADAPTER_READY_AND_STOP_ONLY_AT_LIVE_ACCOUNT_ACTIVATION',
  'HOLD_PRODUCT_PUBLICATION_AT_DASHBOARD_BOUNDARY_AND_PREPARE_API_RECONCILIATION',
  'VERIFY_PAYOUT_READINESS_BEFORE_CLASSIFYING_RECEIVABLE'
]);
const autonomousCandidates = ranked.filter(r => !humanOnly.has(r.next_action));
const next = autonomousCandidates.find(r => r.status !== 'LIVE') || ranked.find(r => r.id === 'asaas_direct');
const asaas = state.providers.find(p => p.id === 'asaas_direct');
const asaasE2e = Boolean(asaas?.checkout_e2e_verified || probe.asaas_checkout_e2e === true);

const report = {
  schema_version: '1.1',
  project: 'LSI_PAYMENT_HUB_R1',
  engine: 'LSI_PAYMENT_ROUTE_COUNCIL_R1',
  generated_at: new Date().toISOString(),
  policy: state.policy,
  asaas_checkout_e2e: asaasE2e,
  verified_primary_receive_rail: asaasE2e ? 'asaas_direct' : null,
  ranked_routes: ranked,
  selected_autonomous_next_action: next ? {id: next.id, action: next.next_action, score: next.score} : null,
  hard_rules: {
    never_generate_or_store_private_keys: true,
    never_claim_revenue_from_unpaid_checkout: true,
    never_bypass_kyc: true,
    never_move_real_value_in_acceptance_test: true,
    prefer_existing_live_receive_rail_for_new_greenfield_products: true
  }
};

fs.mkdirSync(outPath.split('/').slice(0,-1).join('/'), {recursive:true});
fs.writeFileSync(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
