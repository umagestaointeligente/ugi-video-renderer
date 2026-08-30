const VERSION = "lsi-packvalue402-shadow-r1-2026-08-30";
const TARGET_PRICE_USD = 0.001;

const UNIT_TABLE = {
  mg:{dimension:"mass",base:"g",factor:0.001},
  g:{dimension:"mass",base:"g",factor:1}, gram:{dimension:"mass",base:"g",factor:1}, grams:{dimension:"mass",base:"g",factor:1},
  kg:{dimension:"mass",base:"g",factor:1000}, kilogram:{dimension:"mass",base:"g",factor:1000}, kilograms:{dimension:"mass",base:"g",factor:1000},
  oz:{dimension:"mass",base:"g",factor:28.349523125}, ounce:{dimension:"mass",base:"g",factor:28.349523125}, ounces:{dimension:"mass",base:"g",factor:28.349523125},
  lb:{dimension:"mass",base:"g",factor:453.59237}, lbs:{dimension:"mass",base:"g",factor:453.59237}, pound:{dimension:"mass",base:"g",factor:453.59237}, pounds:{dimension:"mass",base:"g",factor:453.59237},
  ml:{dimension:"volume",base:"ml",factor:1}, milliliter:{dimension:"volume",base:"ml",factor:1}, milliliters:{dimension:"volume",base:"ml",factor:1}, millilitre:{dimension:"volume",base:"ml",factor:1}, millilitres:{dimension:"volume",base:"ml",factor:1},
  cl:{dimension:"volume",base:"ml",factor:10}, dl:{dimension:"volume",base:"ml",factor:100},
  l:{dimension:"volume",base:"ml",factor:1000}, liter:{dimension:"volume",base:"ml",factor:1000}, liters:{dimension:"volume",base:"ml",factor:1000}, litre:{dimension:"volume",base:"ml",factor:1000}, litres:{dimension:"volume",base:"ml",factor:1000},
  floz:{dimension:"volume",base:"ml",factor:29.5735295625}, fl_oz:{dimension:"volume",base:"ml",factor:29.5735295625},
  gal:{dimension:"volume",base:"ml",factor:3785.411784}, gallon:{dimension:"volume",base:"ml",factor:3785.411784}, gallons:{dimension:"volume",base:"ml",factor:3785.411784},
  ct:{dimension:"count",base:"item",factor:1}, count:{dimension:"count",base:"item",factor:1}, item:{dimension:"count",base:"item",factor:1}, items:{dimension:"count",base:"item",factor:1},
  pc:{dimension:"count",base:"item",factor:1}, pcs:{dimension:"count",base:"item",factor:1}, piece:{dimension:"count",base:"item",factor:1}, pieces:{dimension:"count",base:"item",factor:1},
  unit:{dimension:"count",base:"item",factor:1}, units:{dimension:"count",base:"item",factor:1}, each:{dimension:"count",base:"item",factor:1}, ea:{dimension:"count",base:"item",factor:1}
};

function json(data,status=200){return new Response(JSON.stringify(data),{status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store","x-lsi-version":VERSION}})}
function n(v,f=0){const x=Number(v);return Number.isFinite(x)?x:f}
function s(v,max=300){return String(v??"").slice(0,max)}
function round(v,d=6){const p=10**d;return Math.round((v+Number.EPSILON)*p)/p}
function cleanUnit(u){return s(u,40).toLowerCase().replace(/\./g,"").replace(/\s+/g,"_").replace(/^fl_?oz$/,"floz")}
function parseNum(v){return Number(String(v).replace(",","."))}

export function parsePackText(input){
  const raw=s(input,300).trim();
  if(!raw) throw new Error("text_required");
  const t=raw.toLowerCase().replace(/,/g,".").replace(/×/g,"x").replace(/fl\s*oz/g,"floz");
  let outer=1, count=1, qty=null, unit=null;
  const outerMatch=t.match(/(?:case\s+of|box\s+of|carton\s+of)\s*(\d{1,4})/i);
  if(outerMatch) outer=parseInt(outerMatch[1],10);
  const nested=t.match(/(?:case\s+of|box\s+of|carton\s+of)\s*\d{1,4}\s*[,;:-]?\s*(\d{1,4})\s*x\s*(\d+(?:\.\d+)?)\s*(mg|kg|g|oz|lb|lbs|ml|cl|dl|l|floz|gal)\b/i);
  if(nested){count=parseInt(nested[1],10);qty=parseNum(nested[2]);unit=nested[3]}
  if(qty===null){
    const m=t.match(/(\d{1,4})\s*x\s*(\d+(?:\.\d+)?)\s*(mg|kg|g|oz|lb|lbs|ml|cl|dl|l|floz|gal)\b/i);
    if(m){count=parseInt(m[1],10);qty=parseNum(m[2]);unit=m[3]}
  }
  if(qty===null){
    const p=t.match(/(\d{1,4})\s*(?:pack|packs|pk|ct|count|units?|items?|pcs?|pieces?)\s*(?:of)?\s*(\d+(?:\.\d+)?)?\s*(mg|kg|g|oz|lb|lbs|ml|cl|dl|l|floz|gal)?\b/i);
    if(p){count=parseInt(p[1],10);if(p[2]&&p[3]){qty=parseNum(p[2]);unit=p[3]}else{qty=1;unit="item"}}
  }
  if(qty===null){
    const m=t.match(/(\d+(?:\.\d+)?)\s*(mg|kg|g|oz|lb|lbs|ml|cl|dl|l|floz|gal)\b/i);
    if(m){qty=parseNum(m[1]);unit=m[2]}
  }
  if(qty===null){
    const m=t.match(/\b(\d{1,5})\s*(?:ct|count|units?|items?|pcs?|pieces?|each|ea)\b/i);
    if(m){qty=1;count=parseInt(m[1],10);unit="item"}
  }
  if(qty===null||!unit) throw new Error("unresolved_pack_expression");
  count*=outer;
  const key=cleanUnit(unit); const spec=UNIT_TABLE[key];
  if(!spec) throw new Error(`unsupported_unit:${key}`);
  if(!(count>0&&qty>0)) throw new Error("non_positive_quantity");
  const baseQuantity=count*qty*spec.factor;
  return {raw,count,quantity_each:qty,input_unit:key,dimension:spec.dimension,base_unit:spec.base,base_quantity:round(baseQuantity,6)};
}

export function normalizeOffer(input={}){
  let parsed;
  if(input.text){parsed=parsePackText(input.text)}
  else{
    const count=n(input.count,1), qty=n(input.quantity,0), key=cleanUnit(input.unit), spec=UNIT_TABLE[key];
    if(!spec) throw new Error(`unsupported_unit:${key||"missing"}`);
    if(!(count>0&&qty>0)) throw new Error("non_positive_quantity");
    parsed={raw:null,count,quantity_each:qty,input_unit:key,dimension:spec.dimension,base_unit:spec.base,base_quantity:round(count*qty*spec.factor,6)};
  }
  const price=n(input.price,NaN); if(!Number.isFinite(price)||price<0) throw new Error("invalid_price");
  const shipping=n(input.shipping,0), tax=n(input.tax,0), discount=n(input.discount,0), yieldPct=n(input.yield_pct,100), dilution=n(input.dilution,1);
  if(shipping<0||tax<0||discount<0||yieldPct<=0||yieldPct>100||dilution<=0) throw new Error("invalid_adjustment");
  const currency=s(input.currency||"USD",12).toUpperCase();
  const effectiveCost=Math.max(0,price+shipping+tax-discount);
  const usableBase=parsed.base_quantity*(yieldPct/100)*dilution;
  const baseUnitPrice=effectiveCost/usableBase;
  let display_basis, display_quantity, display_price;
  if(parsed.dimension==="mass"){display_basis="kg";display_quantity=1000;display_price=baseUnitPrice*1000}
  else if(parsed.dimension==="volume"){display_basis="L";display_quantity=1000;display_price=baseUnitPrice*1000}
  else {display_basis="item";display_quantity=1;display_price=baseUnitPrice}
  return {
    label:s(input.label||input.text||"offer",160),currency,price:round(price,6),shipping:round(shipping,6),tax:round(tax,6),discount:round(discount,6),effective_cost:round(effectiveCost,6),
    yield_pct:round(yieldPct,4),dilution:round(dilution,6),...parsed,usable_base_quantity:round(usableBase,6),
    price_per_base_unit:round(baseUnitPrice,9),display_basis,display_price:round(display_price,6)
  };
}

export function compareOffers(offers){
  if(!Array.isArray(offers)||offers.length<2||offers.length>25) throw new Error("offers_must_contain_2_to_25_items");
  const rows=offers.map(normalizeOffer); const dims=new Set(rows.map(x=>x.dimension)); const currencies=new Set(rows.map(x=>x.currency));
  if(dims.size!==1) throw new Error("incompatible_dimensions");
  if(currencies.size!==1) throw new Error("mixed_currencies_not_supported");
  const ranked=[...rows].sort((a,b)=>a.price_per_base_unit-b.price_per_base_unit);
  const best=ranked[0].price_per_base_unit, worst=ranked[ranked.length-1].price_per_base_unit;
  ranked.forEach((x,i)=>{x.rank=i+1;x.premium_vs_best_pct=best>0?round((x.price_per_base_unit/best-1)*100,3):null});
  return {winner:ranked[0].label,currency:ranked[0].currency,dimension:ranked[0].dimension,display_basis:ranked[0].display_basis,saving_vs_most_expensive_pct:worst>0?round((1-best/worst)*100,3):0,offers:ranked};
}

async function readBody(req){try{return await req.json()}catch{throw new Error("invalid_json")}}

export default {
  async fetch(req){
    const u=new URL(req.url);
    if(req.method==="GET"&&u.pathname==="/health") return json({ok:true,service:"PackValue402",version:VERSION,mode:"SHADOW_NO_SETTLEMENT",target_price_usd:TARGET_PRICE_USD,wallet_bound:false,money_movement:false,production_payments:false,external_paid_provider:false});
    if(req.method==="GET"&&u.pathname==="/.well-known/agent.json") return json({name:"PackValue402",description:"Agent-native multipack and unit-economics normalizer for shopping and procurement decisions.",version:VERSION,payment:{mode:"SHADOW_NO_SETTLEMENT",target_price_usd:TARGET_PRICE_USD,wallet_bound:false},tools:[{name:"normalize_pack",method:"GET",path:"/v1/normalize"},{name:"compare_pack_value",method:"POST",path:"/v1/compare"}]});
    if(req.method==="GET"&&u.pathname==="/v1/normalize"){
      try{const out=normalizeOffer({text:u.searchParams.get("text"),price:u.searchParams.get("price"),shipping:u.searchParams.get("shipping"),tax:u.searchParams.get("tax"),discount:u.searchParams.get("discount"),yield_pct:u.searchParams.get("yield_pct")||100,dilution:u.searchParams.get("dilution")||1,currency:u.searchParams.get("currency")||"USD"});return json({ok:true,mode:"SHADOW_NO_SETTLEMENT",result:out})}catch(e){return json({ok:false,error:s(e.message,200)},400)}
    }
    if(req.method==="POST"&&u.pathname==="/v1/compare"){
      try{const body=await readBody(req);const out=compareOffers(body.offers);return json({ok:true,mode:"SHADOW_NO_SETTLEMENT",target_price_usd:TARGET_PRICE_USD,result:out})}catch(e){return json({ok:false,error:s(e.message,200)},400)}
    }
    return json({ok:false,error:"not_found"},404);
  }
};
