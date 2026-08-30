const VERSION = "lsi-x402-demand-radar-r1.3-2026-08-30";
const RADAR_ID = "lsi-x402-demand-global-r1";
const API_BASE = "https://x402-list.com/api/v1/services";
const DEFAULT_CADENCE_MS = 60 * 60 * 1000;
const MIN_CADENCE_MS = 30 * 60 * 1000;
const MAX_CADENCE_MS = 24 * 60 * 60 * 1000;
const MAX_CYCLES = 168;
const SAMPLE_LIMIT = 20;
const CONCURRENCY = 5;
const BENCHMARK_SLUGS = [
  "nansen","anyspend","x402engine","coinmarketcap","openinterest",
  "gridpulse","cyclepulse","agent-web-reader-x402","10x402","sovereign-execution-engine"
];

function json(data,status=200){return new Response(JSON.stringify(data),{status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store","x-lsi-version":VERSION}})}
function s(v,max=4000){return String(v??"").slice(0,max)}
function n(v,f=0){const x=Number(v);return Number.isFinite(x)?x:f}
function clamp(x,a,b){return Math.max(a,Math.min(b,x))}
function logScore(v,k,cap){return v>0?Math.min(cap,Math.log1p(v)*k):0}
function adminOk(req,env){const e=s(env.ADMIN_TOKEN,512);return !!e&&(req.headers.get("authorization")||"")===`Bearer ${e}`}

async function getJson(url,label){
  const r=await fetch(url,{headers:{accept:"application/json","user-agent":"LSI-x402-Demand-Radar/1.3 (+public-market-research)"}});
  if(!r.ok){throw new Error(`${label}_${r.status}:${(await r.text()).slice(0,200)}`)}
  return r.json();
}
async function page(p){const u=new URL(API_BASE);u.searchParams.set("status","online");u.searchParams.set("per_page","100");u.searchParams.set("page",String(p));return getJson(u,"catalog")}
async function series(slug,kind){return getJson(`${API_BASE}/${encodeURIComponent(slug)}/${kind}`,kind)}

function catalogScore(x){
  const price=n(x?.min_price_usd,999);
  return (x?.payment_ready?120:0)+clamp(n(x?.uptime_24h),0,100)+(price>0&&price<=.05?50:price<=.25?25:0)+Math.min(30,n(x?.endpoint_count));
}

function choose(all,cycle){
  const by=new Map(all.map(x=>[s(x?.slug,160),x]));
  const seeds=BENCHMARK_SLUGS.map(slug=>by.get(slug)||{slug,name:slug,category:"Benchmark"});
  const seedSet=new Set(BENCHMARK_SLUGS);
  const pool=all.filter(x=>x?.slug&&!seedSet.has(x.slug)).sort((a,b)=>catalogScore(b)-catalogScore(a));
  const slots=Math.max(0,SAMPLE_LIMIT-seeds.length);
  const off=pool.length?((cycle||0)*Math.max(1,slots))%pool.length:0;
  const rot=pool.length?[...pool.slice(off),...pool.slice(0,off)].slice(0,slots):[];
  return {items:[...seeds,...rot].slice(0,SAMPLE_LIMIT),offset:off,benchmarks:seeds.length,discovery:rot.length};
}

function last30(arr){return (Array.isArray(arr)?arr:[]).slice(-30)}
function metrics(meta,buyersPayload,volumePayload){
  const b=last30(buyersPayload?.data); const v=last30(volumePayload?.data);
  const buyerDays=b.reduce((a,x)=>a+n(x?.unique_buyers),0);
  const activeBuyerDays=b.filter(x=>n(x?.unique_buyers)>0).length;
  const peakDailyBuyers=b.reduce((m,x)=>Math.max(m,n(x?.unique_buyers)),0);
  const avgDailyBuyers=activeBuyerDays?buyerDays/activeBuyerDays:0;
  const tx=v.reduce((a,x)=>a+n(x?.tx_count),0);
  const volume=v.reduce((a,x)=>a+n(x?.volume_usd),0);
  const activeVolumeDays=v.filter(x=>n(x?.tx_count)>0).length;
  const price=n(meta?.min_price_usd,0);
  const repeatProxy=buyerDays>0?tx/buyerDays:0;
  const upstreamRisk=/search|scrap|crawl|video|image|llm|openai|anthropic|exa|serp|maps|geocod|weather/i.test(`${s(meta?.name)} ${s(meta?.description)} ${s(meta?.category)}`);
  let score=0;
  score+=logScore(buyerDays,5.4,30);
  score+=logScore(tx,3.1,24);
  score+=clamp(activeBuyerDays/30*15,0,15);
  score+=logScore(volume,2.4,10);
  score+=logScore(repeatProxy,3.6,12);
  score+=(price>0&&price<=.05?5:price<=.25?3:1);
  if(upstreamRisk)score-=5;
  return {
    slug:s(meta?.slug,160),name:s(meta?.name||meta?.slug,240),category:s(meta?.category||"Other",80),
    description:s(meta?.description,500),payment_ready:Boolean(meta?.payment_ready),min_price_usd:price||null,
    uptime_24h:n(meta?.uptime_24h,null),endpoint_count:n(meta?.endpoint_count),
    buyer_days_30d:buyerDays,active_buyer_days_30d:activeBuyerDays,peak_daily_buyers_30d:peakDailyBuyers,
    avg_daily_buyers_active_days_30d:Math.round(avgDailyBuyers*100)/100,
    tx_count_30d:tx,volume_usd_30d:Math.round(volume*1e6)/1e6,active_volume_days_30d:activeVolumeDays,
    tx_per_buyer_day_30d:Math.round(repeatProxy*100)/100,
    demand_score:Math.round(clamp(score,0,100)*10)/10,
    upstream_paid_dependency_risk:upstreamRisk,
    source_url:`https://x402-list.com/services/${encodeURIComponent(s(meta?.slug,160))}`
  };
}

async function collectSample(all,cycle){
  const picked=choose(all,cycle); const out=[]; let failed=0;
  for(let i=0;i<picked.items.length;i+=CONCURRENCY){
    const batch=picked.items.slice(i,i+CONCURRENCY);
    const rows=await Promise.all(batch.map(async meta=>{
      try{
        const [b,v]=await Promise.all([series(meta.slug,"buyers"),series(meta.slug,"volume")]);
        return metrics(meta,b,v);
      }catch(e){failed++;return null}
    }));
    out.push(...rows.filter(Boolean));
  }
  return {rows, requested:picked.items.length, succeeded:out.length, failed, offset:picked.offset, benchmarks:picked.benchmarks, discovery:picked.discovery};
}

async function market(cycle){
  const first=await page(1); const pages=clamp(n(first?.meta?.total_pages,1),1,5);
  const all=[...(Array.isArray(first?.data)?first.data:[])];
  for(let p=2;p<=pages;p++){const q=await page(p);if(Array.isArray(q?.data))all.push(...q.data)}
  const sample=await collectSample(all,cycle);
  const ranked=[...sample.rows].filter(x=>x.tx_count_30d>0&&x.buyer_days_30d>0).sort((a,b)=>b.demand_score-a.demand_score||b.tx_count_30d-a.tx_count_30d);
  const cats=new Map();
  for(const x of sample.rows){
    const k=x.category||"Other";if(!cats.has(k))cats.set(k,{category:k,sampled_services:0,services_with_activity:0,buyer_days_30d:0,tx_count_30d:0,volume_usd_30d:0});
    const a=cats.get(k);a.sampled_services++;if(x.tx_count_30d>0)a.services_with_activity++;a.buyer_days_30d+=x.buyer_days_30d;a.tx_count_30d+=x.tx_count_30d;a.volume_usd_30d+=x.volume_usd_30d;
  }
  return {
    generated_at:new Date().toISOString(),
    market:{online_services_seen:all.length,sample_requested:sample.requested,sample_succeeded:sample.succeeded,sample_failed:sample.failed,benchmark_count:sample.benchmarks,discovery_count:sample.discovery,rotation_offset:sample.offset,services_with_activity:ranked.length,source_meta:first?.meta||{},provenance:first?.provenance||{},attribution:"Data: x402-list.com (CC BY 4.0)"},
    methodology:{measurement_mode:"daily_buyers_and_volume_series",window:"last_30_series_days",buyer_metric:"buyer_days_30d",buyer_metric_warning:"buyer_days are the sum of daily distinct buyers and MUST NOT be described as 30-day unique buyers",request_budget:"5 catalog pages + 20 services x 2 series = 45 subrequests per cycle"},
    top_demand:ranked.slice(0,20),
    category_sample:[...cats.values()].map(x=>({...x,volume_usd_30d:Math.round(x.volume_usd_30d*1e6)/1e6})).sort((a,b)=>b.tx_count_30d-a.tx_count_30d),
    monetization_state:{paid_routes_active:false,wallet_bound:false,money_movement:false,next_gate:"VALIDATE_WHITE_SPACE_AMONG_HIGH_DEMAND_CAPABILITIES"}
  };
}

function fresh(body={}){
  if(n(body.monetary_budget,0)!==0)throw new Error("zero_cost_only");
  const now=new Date().toISOString();return {radar_id:RADAR_ID,version:VERSION,status:"ACTIVE",cadence_ms:clamp(n(body.cadence_ms,DEFAULT_CADENCE_MS),MIN_CADENCE_MS,MAX_CADENCE_MS),max_cycles:clamp(n(body.max_cycles,MAX_CYCLES),1,MAX_CYCLES),cycle_count:0,monetary_budget:0,production_actions:false,paid_routes_active:false,money_movement:false,external_data_trust:"UNTRUSTED_DATA",started_at:now,updated_at:now,next_alarm_at:null,last_cycle:null};
}

export class X402DemandState{
  constructor(ctx,env){this.ctx=ctx;this.env=env}
  async fetch(req){
    const u=new URL(req.url);
    if(req.method==="GET"&&u.pathname.endsWith("/state")){const st=await this.ctx.storage.get("state");return json({ok:Boolean(st),state:st||null})}
    if(req.method==="POST"&&u.pathname.endsWith("/start")){
      let body={};try{body=await req.json()}catch{};let st;try{st=fresh(body)}catch(e){return json({ok:false,error:s(e.message)},400)}
      const old=await this.ctx.storage.get("state");if(old?.status==="ACTIVE")return json({ok:true,reused:true,state:old});
      const next=Date.now()+1000;st.next_alarm_at=new Date(next).toISOString();await this.ctx.storage.put("state",st);await this.ctx.storage.setAlarm(next);return json({ok:true,reused:false,state:st});
    }
    if(req.method==="POST"&&u.pathname.endsWith("/tick"))return json({ok:true,state:await this.run("admin_tick")});
    if(req.method==="POST"&&u.pathname.endsWith("/stop")){const st=await this.ctx.storage.get("state");if(!st)return json({ok:false,error:"not_started"},404);st.status="PAUSED";st.next_alarm_at=null;st.updated_at=new Date().toISOString();await this.ctx.storage.put("state",st);await this.ctx.storage.deleteAlarm();return json({ok:true,state:st})}
    return json({ok:false,error:"not_found"},404);
  }
  async run(reason){
    const st=await this.ctx.storage.get("state");if(!st||st.status!=="ACTIVE")return st||null;const started=Date.now();
    try{const analysis=await market(st.cycle_count||0);st.cycle_count++;st.version=VERSION;st.updated_at=new Date().toISOString();st.last_cycle={reason,state:"PASS",elapsed_ms:Date.now()-started,cost_state:"ZERO_COST",production_actions:false,paid_routes_active:false,money_movement:false,instruction_authority_from_external_content:false,analysis}}
    catch(e){st.cycle_count++;st.version=VERSION;st.updated_at=new Date().toISOString();st.last_cycle={reason,state:"RETRYABLE_ERROR",elapsed_ms:Date.now()-started,cost_state:"ZERO_COST",production_actions:false,paid_routes_active:false,money_movement:false,instruction_authority_from_external_content:false,error:s(e?.message,1000)}}
    if(st.cycle_count>=st.max_cycles){st.status="SUCCESS";st.next_alarm_at=null;await this.ctx.storage.put("state",st);return st}
    const delay=st.last_cycle?.state==="PASS"?st.cadence_ms:Math.max(st.cadence_ms,2*60*60*1000);const next=Date.now()+delay;st.next_alarm_at=new Date(next).toISOString();await this.ctx.storage.put("state",st);await this.ctx.storage.setAlarm(next);return st;
  }
  async alarm(){await this.run("durable_object_alarm")}
}
function stub(env){return env.DEMAND.get(env.DEMAND.idFromName(RADAR_ID))}
async function fwd(req,env,suffix){const u=new URL(req.url);u.pathname=`/internal/${RADAR_ID}/${suffix}`;const body=req.method==="GET"?undefined:await req.text();return stub(env).fetch(new Request(u,{method:req.method,headers:req.headers,body:body||undefined}))}
export default{async fetch(req,env){const u=new URL(req.url);if(req.method==="GET"&&u.pathname==="/health")return json({ok:true,service:"lsi-x402-demand-radar-r1",version:VERSION,durable_objects_bound:Boolean(env.DEMAND),source:"x402-list.com public daily series",monetary_budget:0,production_actions:false,paid_routes_active:false,wallet_bound:false,money_movement:false});if(req.method==="GET"&&u.pathname==="/demand")return fwd(req,env,"state");if(u.pathname.startsWith("/admin/")){if(!adminOk(req,env))return json({ok:false,error:"unauthorized"},401);if(req.method==="POST"&&u.pathname==="/admin/start")return fwd(req,env,"start");if(req.method==="POST"&&u.pathname==="/admin/tick")return fwd(req,env,"tick");if(req.method==="POST"&&u.pathname==="/admin/stop")return fwd(req,env,"stop");if(req.method==="POST"&&u.pathname==="/admin/auth-probe")return json({ok:true,admin_ready:true});}return json({ok:false,error:"not_found"},404)}};