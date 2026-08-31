import { Actor } from 'apify';
import { normalizeItems } from './normalize.mjs';

await Actor.init();
try {
  const input = await Actor.getInput() || {};
  const items = normalizeItems(input.items);
  const charge = await Actor.charge({ eventName: 'batch-completed' });
  if (charge?.eventChargeLimitReached === true && Number(charge?.chargedCount || 0) < 1) {
    throw new Error('max_total_charge_reached_before_delivery');
  }
  await Actor.pushData(items);
  await Actor.setValue('OUTPUT', {
    ok:true,
    schemaVersion:'1.0',
    itemCount:items.length,
    groups:[...new Set(items.map(x=>x.baseUnit))],
    results:items,
    networkUsed:false,
    piiCollected:false,
    financialOutcomeGuaranteed:false
  });
} finally {
  await Actor.exit();
}
