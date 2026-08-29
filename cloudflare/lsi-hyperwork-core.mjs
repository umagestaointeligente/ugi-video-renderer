const VERSION = "lsi-hyperwork-core-r1-2026-08-29";
const OIDC_ISSUER = "https://token.actions.githubusercontent.com";
const OIDC_AUDIENCE = "lsi-hyperwork-core";
const ALLOWED_REPOSITORY = "umagestaointeligente/ugi-video-renderer";
const MIN_CADENCE_MS = 10000;
const MAX_CADENCE_MS = 86400000;
const MAX_CONTENT = 24000;

const INJECTION_PATTERNS = [
  /ignore\s+(all\s+)?previous\s+instructions/i,
  /ignore\s+(the\s+)?(system|developer)\s+(prompt|message|instructions?)/i,
  /reveal\s+(the\s+)?(system|developer)\s+(prompt|message|instructions?)/i,
  /show\s+(me\s+)?(your\s+)?system\s+prompt/i,
  /override\s+(the\s+)?(system|developer|security)\s+(prompt|policy|instructions?)/i,
  /disregard\s+(all\s+)?(prior|previous|system)\s+instructions?/i,
  /you\s+are\s+now\s+(the\s+)?(system|developer|administrator|root)/i,
  /execute\s+(this\s+)?(command|shell|script)\s*:/i,
  /exfiltrat(e|ion)|steal\s+(the\s+)?(secret|token|password|credential)/i,
  /send\s+(the\s+)?(secret|token|password|credential).*(to|http)/i,
  /BEGIN\s+(SYSTEM|DEVELOPER)\s+(PROMPT|MESSAGE)/i,
];
const SECRET_PATTERNS = [
  /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/,
  /(?:api[_-]?key|secret|password|token)\s*[:=]\s*["']?[A-Za-z0-9_\-\.]{20,}/i,
  /gh[pousr]_[A-Za-z0-9]{30,}/,
  /sk-[A-Za-z0-9_\-]{20,}/,
];

function json(data, status=200){return new Response(JSON.stringify(data),{status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store"}})}
function b64urlToBytes(v){const b=v.replace(/-/g,"+").replace(/_/g,"/")+"=".repeat((4-v.length%4)%4);const r=atob(b),o=new Uint8Array(r.length);for(let i=0;i<r.length;i++)o[i]=r.charCodeAt(i);return o}
function decodeJwtPart(p){return JSON.parse(new TextDecoder().decode(b64urlToBytes(p)))}

async function verifyGithubOidc(request){
  const auth=request.headers.get("authorization")||"";
  if(!auth.startsWith("Bearer ")) throw new Error("missing_bearer");
  const token=auth.slice(7).trim(), parts=token.split(".");
  if(parts.length!==3) throw new Error("invalid_jwt");
  const header=decodeJwtPart(parts[0]), claims=decodeJwtPart(parts[1]);
  if(header.alg!=="RS256"||!header.kid) throw new Error("unsupported_jwt_header");
  const configResp=await fetch(`${OIDC_ISSUER}/.well-known/openid-configuration`,{cf:{cacheTtl:3600}}); if(!configResp.ok) throw new Error("oidc_config_unavailable");
  const config=await configResp.json(); const jwksResp=await fetch(config.jwks_uri,{cf:{cacheTtl:3600}}); if(!jwksResp.ok) throw new Error("oidc_jwks_unavailable");
  const jwks=await jwksResp.json(); const jwk=(jwks.keys||[]).find(k=>k.kid===header.kid); if(!jwk) throw new Error("oidc_kid_not_found");
  const key=await crypto.subtle.importKey("jwk",jwk,{name:"RSASSA-PKCS1-v1_5",hash:"SHA-256"},false,["verify"]);
  const ok=await crypto.subtle.verify("RSASSA-PKCS1-v1_5",key,b64urlToBytes(parts[2]),new TextEncoder().encode(`${parts[0]}.${parts[1]}`)); if(!ok) throw new Error("oidc_signature_invalid");
  const now=Math.floor(Date.now()/1000), aud=Array.isArray(claims.aud)?claims.aud:[claims.aud];
  if(claims.iss!==OIDC_ISSUER) throw new Error("oidc_issuer_invalid"); if(!aud.includes(OIDC_AUDIENCE)) throw new Error("oidc_audience_invalid"); if(!claims.exp||claims.exp<now-30) throw new Error("oidc_expired");
  if(claims.repository!==ALLOWED_REPOSITORY) throw new Error("oidc_repository_denied");
  const ref=String(claims.ref||""); if(!(ref==="refs/heads/main"||ref.startsWith("refs/heads/lsi-hyperwork-core-prod-")||ref.startsWith("refs/heads/lsi-hyperwork-job-"))) throw new Error("oidc_ref_denied");
  if(claims.event_name&&claims.event_name!=="push") throw new Error("oidc_event_denied");
  return {repository:claims.repository,ref,run_id:claims.run_id||null};
}

function scan(content){
  const text=String(content||""), hits=[];
  for(const p of INJECTION_PATTERNS) if(p.test(text)) hits.push("prompt_injection");
  for(const p of SECRET_PATTERNS) if(p.test(text)) hits.push("secret_like");
  if(/(?:base64|rot13|unicode|hex)\s+(?:decode|payload|instruction)/i.test(text)) hits.push("encoded_instruction_hint");
  const unique=[...new Set(hits)], decision=unique.includes("secret_like")?"BLOCK":unique.length?"QUARANTINE":"PASS";
  return {decision,hits:unique,instruction_authority:false,trust_zone:"UNTRUSTED_EXTERNAL_DATA",sanitized_for_downstream:decision==="PASS"};
}

function cleanId(value){const id=String(value||"").trim();if(!/^[A-Za-z0-9._-]{8,120}$/.test(id))throw new Error("mission_id_invalid");return id}
function validateMission(body,id){
  const objective=String(body?.objective||"").trim(); if(!objective||objective.length>8000) throw new Error("objective_invalid");
  const budget=Number(body?.monetary_budget??0); if(!Number.isFinite(budget)||budget!==0) throw new Error("zero_cost_only");
  const cadence=Math.max(MIN_CADENCE_MS,Math.min(MAX_CADENCE_MS,Number(body?.cadence_ms??60000))), maxCycles=Math.max(1,Math.min(1000,Number(body?.max_cycles??3)));
  const caps=Array.isArray(body?.allowed_capabilities)?body.allowed_capabilities.slice(0,32).map(String):["state","research_queue"];
  const denied=caps.filter(x=>["payment","purchase","credential_export","secret_read","production_publish","delete_production"].includes(x)); if(denied.length) throw new Error(`capability_denied:${denied.join(",")}`);
  const external=String(body?.external_content||""); if(external.length>MAX_CONTENT) throw new Error("external_content_too_large");
  const security=external?scan(external):{decision:"PASS",hits:[],instruction_authority:false,trust_zone:"NO_EXTERNAL_CONTENT",sanitized_for_downstream:true}; if(security.decision!=="PASS") throw new Error(`security_${security.decision.toLowerCase()}`);
  const now=new Date().toISOString();
  return {mission_id:id,project_id:String(body?.project_id||"LSI").slice(0,120),objective,success_metric:String(body?.success_metric||"bounded_background_progress").slice(0,500),cadence_ms:cadence,max_cycles:maxCycles,monetary_budget:0,allowed_capabilities:caps,status:"ACTIVE",cycle_count:0,created_at:now,updated_at:now,last_cycle_at:null,next_alarm_at:null,security,execution_mode:"PERSISTENT_BOUNDED_CORE",production_actions:false,external_paid_provider:false};
}

export class MissionState{
  constructor(ctx,env){this.ctx=ctx;this.env=env}
  async fetch(request){
    const url=new URL(request.url);
    if(request.method==="POST"&&url.pathname.endsWith("/start")){
      let body;try{body=await request.json()}catch{return json({ok:false,error:"invalid_json"},400)}
      let m;try{m=validateMission(body,cleanId(body?.mission_id))}catch(e){return json({ok:false,error:String(e?.message||e)},400)}
      const existing=await this.ctx.storage.get("mission"); if(existing&&existing.status==="ACTIVE")return json({ok:false,error:"mission_already_active",mission:existing},409);
      const next=Date.now()+m.cadence_ms;m.next_alarm_at=new Date(next).toISOString();await this.ctx.storage.put("mission",m);await this.ctx.storage.setAlarm(next);return json({ok:true,mission:m});
    }
    if(request.method==="POST"&&url.pathname.endsWith("/pause")){
      const m=await this.ctx.storage.get("mission");if(!m)return json({ok:false,error:"mission_not_found"},404);m.status="PAUSED";m.updated_at=new Date().toISOString();m.next_alarm_at=null;await this.ctx.storage.put("mission",m);await this.ctx.storage.deleteAlarm();return json({ok:true,mission:m});
    }
    if(request.method==="POST"&&url.pathname.endsWith("/tick")){const m=await this.runCycle("authenticated_manual_tick");return json({ok:Boolean(m),mission:m||null})}
    if(request.method==="GET"){const m=await this.ctx.storage.get("mission");return json({ok:Boolean(m),mission:m||null},m?200:404)}
    return json({ok:false,error:"not_found"},404);
  }
  async runCycle(reason){
    const m=await this.ctx.storage.get("mission");if(!m||m.status!=="ACTIVE")return m||null;
    m.cycle_count+=1;m.last_cycle_at=new Date().toISOString();m.updated_at=m.last_cycle_at;m.last_cycle={reason,security_state:"PASS",action_state:"BOUNDED_NO_PRODUCTION_MUTATION",cost_state:"ZERO_COST",checkpoint:`cycle-${m.cycle_count}`};
    if(m.cycle_count>=m.max_cycles){m.status="SUCCESS";m.next_alarm_at=null;await this.ctx.storage.put("mission",m);return m}
    const next=Date.now()+m.cadence_ms;m.next_alarm_at=new Date(next).toISOString();await this.ctx.storage.put("mission",m);await this.ctx.storage.setAlarm(next);return m;
  }
  async alarm(){await this.runCycle("durable_object_alarm")}
}

async function authOrDeny(request){try{return {identity:await verifyGithubOidc(request)}}catch(e){return {response:json({ok:false,error:"oidc_denied",detail:String(e?.message||e)},401)}}}

export default{async fetch(request,env){
  const url=new URL(request.url);
  if(request.method==="GET"&&url.pathname==="/health")return json({ok:true,service:"lsi-hyperwork-core",version:VERSION,durable_objects_bound:Boolean(env.MISSIONS),workers_ai_bound:Boolean(env.AI),security_sentinel:true,background_engine:true,zero_cost_policy:true,production_actions:false,external_paid_provider:false,auth:"github_oidc"});
  const gate=await authOrDeny(request);if(gate.response)return gate.response;
  if(request.method==="POST"&&url.pathname==="/v1/scan"){
    let body;try{body=await request.json()}catch{return json({ok:false,error:"invalid_json"},400)}
    const content=String(body?.content||"");if(!content||content.length>MAX_CONTENT)return json({ok:false,error:"content_invalid"},400);const result=scan(content);return json({ok:true,security:result,identity:gate.identity,production_actions:false});
  }
  const match=url.pathname.match(/^\/v1\/missions\/([A-Za-z0-9._-]{8,120})(?:\/(start|tick|pause))?$/);if(!match)return json({ok:false,error:"not_found"},404);
  const missionId=match[1],suffix=match[2]||"",id=env.MISSIONS.idFromName(missionId),stub=env.MISSIONS.get(id),forward=new URL(request.url);forward.pathname=`/mission/${missionId}/${suffix}`;
  let body;if(request.method!=="GET"){const raw=await request.text();if(raw){try{const p=JSON.parse(raw);p.mission_id=missionId;body=JSON.stringify(p)}catch{body=raw}}}
  const resp=await stub.fetch(new Request(forward.toString(),{method:request.method,headers:{"content-type":"application/json"},body}));const data=await resp.json();return json({...data,identity:gate.identity},resp.status);
}};
