const VERSION = "lsi-revenue-monitor-r1-2026-08-29";
const ORDER_PREFIX = "lola/commerce/orders/";
const DEFAULT_START = "2026-08-29T22:23:00.000Z";
const DEFAULT_TARGET = 100;
const DEFAULT_PRODUCT = "UGI-MATERIAL-PRIORIDADES-001";

function json(data, status=200){return new Response(JSON.stringify(data),{status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store"}})}
function authorized(req,env){const got=req.headers.get("x-lsi-revenue-key")||"";return Boolean(env.MONITOR_KEY)&&got===env.MONITOR_KEY}
function finiteMoney(v){const n=Number(v);return Number.isFinite(n)&&n>=0?n:0}
async function sha(s){const b=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(String(s)));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join("").slice(0,16)}

async function listAll(bucket,prefix){let cursor;const objects=[];do{const page=await bucket.list({prefix,cursor,limit:1000});objects.push(...page.objects);cursor=page.truncated?page.cursor:undefined}while(cursor);return objects}

async function aggregate(env,{start,productId,target}){
  const startMs=Date.parse(start);if(!Number.isFinite(startMs))throw new Error("invalid_start");
  const objects=await listAll(env.MEDIA,ORDER_PREFIX);
  let paidCount=0,gross=0,latest=null;const fingerprints=[];let inspected=0,invalid=0;
  for(const meta of objects){
    const obj=await env.MEDIA.get(meta.key);if(!obj)continue;inspected++;
    let order;try{order=await obj.json()}catch{invalid++;continue}
    if(String(order?.paymentStatus||"").toLowerCase()!=="paid")continue;
    if(productId&&String(order?.productId||"")!==productId)continue;
    const paidAt=String(order?.paidAt||"");const paidMs=Date.parse(paidAt);if(!Number.isFinite(paidMs)||paidMs<startMs)continue;
    const amount=finiteMoney(order?.amount);paidCount++;gross+=amount;
    if(!latest||paidMs>Date.parse(latest))latest=paidAt;
    if(fingerprints.length<50)fingerprints.push(await sha(order?.referenceId||meta.key));
  }
  gross=Math.round((gross+Number.EPSILON)*100)/100;
  return {paid_count:paidCount,gross_brl:gross,target_brl:target,target_met:gross>=target,start,product_id:productId,latest_paid_at:latest,order_fingerprints:fingerprints,orders_inspected:inspected,invalid_order_json:invalid,authoritative_source:"UGI_R2_ORDER_LEDGER_UPDATED_BY_PROVIDER_WEBHOOK",payment_status_required:"paid",pii_exposed:false,write_capability:false};
}

export default {async fetch(request,env){
  const url=new URL(request.url);
  if(request.method==="GET"&&url.pathname==="/health")return json({ok:true,service:"lsi-revenue-monitor",version:VERSION,r2_bound:Boolean(env.MEDIA),auth_configured:Boolean(env.MONITOR_KEY),read_only:true,write_capability:false,zero_cost_policy:true});
  if(!authorized(request,env))return json({ok:false,error:"unauthorized"},401);
  if(request.method==="GET"&&url.pathname==="/v1/summary"){
    try{const result=await aggregate(env,{start:url.searchParams.get("start")||DEFAULT_START,productId:url.searchParams.get("product_id")||DEFAULT_PRODUCT,target:finiteMoney(url.searchParams.get("target")||DEFAULT_TARGET)});return json({ok:true,version:VERSION,...result})}catch(e){return json({ok:false,error:String(e?.message||e)},400)}
  }
  return json({ok:false,error:"not_found"},404);
}};
