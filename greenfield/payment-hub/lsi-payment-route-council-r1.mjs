import fs from 'node:fs';

const statePath = process.argv[2] || 'greenfield/payment-hub/provider-state-r1.json';
const probePath = process.argv[3] || null;
const outPath = process.argv[4] || 'generated/evidence/lsi-payment-route-council-r1.json';
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));
const probe = probePath && fs.existsSync(probePath) && fs.statSync(probePath).size > 0 ? JSON.parse(fs.readFileSync(probePath, 'utf8')) : {};

function score(p) {
  let s = 0;
  if (p.live_receive_verified) s += 55;
  if (p.checkout_e2e_verified) s += 15;
  if (p.package_qa_verified) s += 10;
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
  if (p.id === 'apify_agentic_x402') return p.package_qa_verified ? 'WAIT_AT_APIFY_DEVELOPER_KYC_AND_ACCOUNT_CONNECTION' : 'PREPARE_ACTOR_AND_STOP_ONLY_AT_KYC';
  if (p.id === 'stripe_checkout') return p.package_qa_verified ? 'WAIT_AT_STRIPE_LIVE_ACCOUNT_ACTIVATION' : 'PREPARE_STRIPE_TESTMODE_ADAPTER';
  if (p.id === 'rapidapi_marketplace') return p.package_qa_verified ? 'WAIT_AT_RAPIDAPI_PROJECT_PROXY_SECRET_AND_PAYPAL_PAYOUT' : 'PREPARE_PROVIDER_PACKAGE_AND_STOP_ONLY_AT_PAYOUT_SETUP';
  if (p.id === 'kiwify_marketplace') return p.package_qa_verified ? 'WAIT_AT_KIWIFY_LEAST_PRIVILEGE_API_KEY_AND_EXISTING_PRODUCT' : 'PREPARE_KIWIFY_RECONCILIATION_ADAPTER';
  if (p.id === 'shopee_affiliate') return 'VERIFY_PAYOUT_READINESS_BEFORE_CLASSIFYING_RECEIVABLE';
  return 'RESEARCH';
}

const ranked = state.providers.map(p => ({
  id: p.id,
  rail: p.rail,
  score: score(p),
  status: p.live_receive_verified ? 'LIVE' : (p.package_qa_verified ? 'PACKAGE_READY_EXTERNAL_BOUNDARY' : (p.blocker ? 'BLOCKED_OR_PARTIAL' : 'READY_TO_TEST')),
  blocker: p.blocker,
  package_qa_verified:Boolean(p.package_qa_verified),
  next_action: actionFor(p),
  evidence: p.evidence
})).sort((a,b) => b.score - a.score || a.id.localeCompare(b.id));

const humanOnly = new Set([
  'WAIT_FOR_USER_CONTROLLED_PAYTO_ADDRESS',
  'WAIT_AT_APIFY_DEVELOPER_KYC_AND_ACCOUNT_CONNECTION',
  'WAIT_AT_STRIPE_LIVE_ACCOUNT_ACTIVATION',
  'WAIT_AT_RAPIDAPI_PROJECT_PROXY_SECRET_AND_PAYPAL_PAYOUT',
  'WAIT_AT_KIWIFY_LEAST_PRIVILEGE_API_KEY_AND_EXISTING_PRODUCT',
  'VERIFY_PAYOUT_READINESS_BEFORE_CLASSIFYING_RECEIVABLE'
]);
const autonomousCandidates = ranked.filter(r => !humanOnly.has(r.next_action) && r.status !== 'LIVE');
const next = autonomousCandidates[0] || null;
const asaas = state.providers.find(p => p.id === 'asaas_direct');
const asaasE2e = Boolean(asaas?.checkout_e2e_verified || probe.asaas_checkout_e2e === true);

const report = {
  schema_version: '1.2',
  project: 'LSI_PAYMENT_HUB_R1',
  engine: 'LSI_PAYMENT_ROUTE_COUNCIL_R1',
  generated_at: new Date().toISOString(),
  policy: state.policy,
  asaas_checkout_e2e: asaasE2e,
  verified_primary_receive_rail: asaasE2e ? 'asaas_direct' : null,
  ranked_routes: ranked,
  selected_autonomous_next_action: next ? {id: next.id, action: next.next_action, score: next.score} : null,
  external_boundaries: ranked.filter(r => humanOnly.has(r.next_action)).map(r => ({id:r.id, blocker:r.blocker, action:r.next_action})),
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
