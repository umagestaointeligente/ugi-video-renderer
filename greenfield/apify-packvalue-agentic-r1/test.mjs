import assert from 'node:assert/strict';
import { normalizeItems } from './src/normalize.mjs';

const out = normalizeItems([
  {name:'500g',price:12.9,packageSize:500,unit:'g'},
  {name:'1kg',price:21.5,packageSize:1,unit:'kg'},
  {name:'promo',price:25,packageSize:1,unit:'kg',discountPercent:20,shipping:1}
]);
assert.equal(out.length,3);
assert.equal(out.find(x=>x.name==='500g').normalizedPrice,25.8);
assert.equal(out.find(x=>x.name==='1kg').normalizedPrice,21.5);
assert.equal(out.find(x=>x.name==='promo').normalizedPrice,21);
assert.equal(out.find(x=>x.name==='promo').rankWithinUnit,1);
assert.equal(out.find(x=>x.name==='promo').bestWithinUnit,true);
assert.throws(()=>normalizeItems([]),/1_to_200/);
assert.throws(()=>normalizeItems([{name:'bad',price:1,packageSize:0,unit:'kg'}]),/packageSize/);
assert.throws(()=>normalizeItems([{name:'bad',price:1,packageSize:1,unit:'oz'}]),/invalid_unit/);
console.log('PACKVALUE_AGENTIC_CORE_TESTS=PASS');
