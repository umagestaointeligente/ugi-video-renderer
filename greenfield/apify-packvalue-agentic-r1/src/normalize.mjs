const UNIT = {
  kg: {base:'kg', factor:1},
  g: {base:'kg', factor:0.001},
  l: {base:'l', factor:1},
  ml: {base:'l', factor:0.001},
  unit: {base:'unit', factor:1},
  un: {base:'unit', factor:1}
};

function finiteNumber(value, name, {min=0, max=Number.MAX_SAFE_INTEGER, allowZero=true}={}) {
  const n = Number(value);
  if (!Number.isFinite(n) || n < min || n > max || (!allowZero && n === 0)) throw new Error(`invalid_${name}`);
  return n;
}

export function normalizeItems(items) {
  if (!Array.isArray(items) || items.length < 1 || items.length > 200) throw new Error('items_must_have_1_to_200_entries');
  const result = items.map((raw, index) => {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) throw new Error(`invalid_item_${index}`);
    const name = String(raw.name || `Item ${index+1}`).trim().slice(0,120);
    const unitKey = String(raw.unit || 'unit').trim().toLowerCase();
    const unit = UNIT[unitKey];
    if (!unit) throw new Error(`invalid_unit_${index}`);
    const price = finiteNumber(raw.price, `price_${index}`, {min:0, max:1e9, allowZero:false});
    const packageSize = finiteNumber(raw.packageSize ?? 1, `packageSize_${index}`, {min:0, max:1e9, allowZero:false});
    const packageCount = finiteNumber(raw.packageCount ?? 1, `packageCount_${index}`, {min:0, max:1e6, allowZero:false});
    const shipping = finiteNumber(raw.shipping ?? 0, `shipping_${index}`, {min:0, max:1e9});
    const discountPercent = finiteNumber(raw.discountPercent ?? 0, `discountPercent_${index}`, {min:0, max:100});
    const effectivePrice = (price * (1 - discountPercent / 100)) + shipping;
    const normalizedQuantity = packageSize * packageCount * unit.factor;
    const normalizedPrice = effectivePrice / normalizedQuantity;
    return {
      inputIndex:index,
      name,
      baseUnit:unit.base,
      effectivePrice:Number(effectivePrice.toFixed(6)),
      normalizedQuantity:Number(normalizedQuantity.toFixed(9)),
      normalizedPrice:Number(normalizedPrice.toFixed(9)),
      normalizedLabel:`BRL/${unit.base}`,
      assumptions:{discountAppliedBeforeShipping:true,packageCount}
    };
  });
  const groups = new Map();
  for (const item of result) {
    if (!groups.has(item.baseUnit)) groups.set(item.baseUnit, []);
    groups.get(item.baseUnit).push(item);
  }
  const ranked=[];
  for (const [,group] of groups) {
    group.sort((a,b)=>a.normalizedPrice-b.normalizedPrice || a.inputIndex-b.inputIndex);
    group.forEach((item,i)=>ranked.push({...item, rankWithinUnit:i+1, bestWithinUnit:i===0}));
  }
  ranked.sort((a,b)=>a.inputIndex-b.inputIndex);
  return ranked;
}
