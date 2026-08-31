const VERSION = 'packvalue-rapidapi-r1';
const MAX_ITEMS = 200;
const UNITS = {
  kg: {base:'kg', factor:1}, g:{base:'kg', factor:0.001},
  l:{base:'l', factor:1}, ml:{base:'l', factor:0.001},
  unit:{base:'unit', factor:1}, un:{base:'unit', factor:1}
};

function json(body,status=200){return new Response(JSON.stringify(body),{status,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}})}
function num(v,name,{min=0,max=1e9,allowZero=true}={}){const n=Number(v);if(!Number.isFinite(n)||n<min||n>max||(!allowZero&&n===0))throw new Error(`invalid_${name}`);return n}
function normalize(items){
  if(!Array.isArray(items)||items.length<1||items.length>MAX_ITEMS) throw new Error('items_must_have_1_to_200_entries');
  const rows=items.map((raw,index)=>{
    if(!raw||typeof raw!=='object'||Array.isArray(raw))throw new Error(`invalid_item_${index}`);
    const unitKey=String(raw.unit||'unit').trim().toLowerCase(), unit=UNITS[unitKey];
    if(!unit)throw new Error(`invalid_unit_${index}`);
    const price=num(raw.price,`price_${index}`,{allowZero:false});
    const packageSize=num(raw.packageSize??1,`packageSize_${index}`,{allowZero:false});
    const packageCount=num(raw.packageCount??1,`packageCount_${index}`,{max:1e6,allowZero:false});
    const shipping=num(raw.shipping??0,`shipping_${index}`);
    const discountPercent=num(raw.discountPercent??0,`discountPercent_${index}`,{max:100});
    const effectivePrice=price*(1-discountPercent/100)+shipping;
    const normalizedQuantity=packageSize*packageCount*unit.factor;
    return {inputIndex:index,name:String(raw.name||`Item ${index+1}`).trim().slice(0,120),baseUnit:unit.base,effectivePrice:Number(effectivePrice.toFixed(6)),normalizedQuantity:Number(normalizedQuantity.toFixed(9)),normalizedPrice:Number((effectivePrice/normalizedQuantity).toFixed(9)),normalizedLabel:`BRL/${unit.base}`};
  });
  for(const base of new Set(rows.map(x=>x.baseUnit))){
    const group=rows.filter(x=>x.baseUnit===base).sort((a,b)=>a.normalizedPrice-b.normalizedPrice||a.inputIndex-b.inputIndex);
    group.forEach((x,i)=>{rows[x.inputIndex].rankWithinUnit=i+1;rows[x.inputIndex].bestWithinUnit=i===0});
  }
  return rows;
}
function authorized(req,env){
  const expected=String(env.RAPIDAPI_PROXY_SECRET||'').trim();
  if(!expected)return false;
  const got=String(req.headers.get('x-rapidapi-proxy-secret')||'').trim();
  if(got.length!==expected.length)return false;
  let diff=0;for(let i=0;i<got.length;i++)diff|=got.charCodeAt(i)^expected.charCodeAt(i);return diff===0;
}
export default {async fetch(request,env){
  const url=new URL(request.url);
  if(request.method==='GET'&&url.pathname==='/health')return json({ok:true,service:'PackValue RapidAPI R1',version:VERSION,proxySecretConfigured:Boolean(env.RAPIDAPI_PROXY_SECRET),monetizationHandledBy:'rapidapi',piiCollected:false});
  if(request.method==='POST'&&url.pathname==='/v1/normalize'){
    if(!env.RAPIDAPI_PROXY_SECRET)return json({ok:false,error:'rapidapi_proxy_secret_not_configured'},503);
    if(!authorized(request,env))return json({ok:false,error:'rapidapi_proxy_not_authorized'},401);
    const len=Number(request.headers.get('content-length')||0);if(len>131072)return json({ok:false,error:'request_too_large'},413);
    let body;try{body=await request.json()}catch{return json({ok:false,error:'invalid_json'},400)}
    try{const results=normalize(body?.items);return json({ok:true,schemaVersion:'1.0',itemCount:results.length,results,financialOutcomeGuaranteed:false})}catch(e){return json({ok:false,error:String(e?.message||'invalid_input')},400)}
  }
  return json({ok:false,error:'not_found'},404);
}};
