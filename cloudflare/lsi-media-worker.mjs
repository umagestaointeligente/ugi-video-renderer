const VERSION = 'lsi-media-worker-r1-2026-08-29';
const IMAGE_MODEL = '@cf/black-forest-labs/flux-1-schnell';
const TRANSCRIBE_MODEL = '@cf/openai/whisper-large-v3-turbo';
const OIDC_ISSUER = 'https://token.actions.githubusercontent.com';
const OIDC_AUDIENCE = 'lsi-media-worker';
const ALLOWED_REPOSITORY = 'umagestaointeligente/ugi-video-renderer';
const ALLOWED_REF_PREFIXES = ['refs/heads/lsi-media-job-', 'refs/heads/lsi-media-worker-pilot-'];
const MAX_IMAGE_PROMPT_CHARS = 2048;
const MAX_AUDIO_BYTES = 5 * 1024 * 1024;

function json(data, status=200) {
  return new Response(JSON.stringify(data), {status, headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
}
function b64urlToBytes(value) {
  const base64=value.replace(/-/g,'+').replace(/_/g,'/')+'='.repeat((4-(value.length%4))%4);
  const raw=atob(base64); const out=new Uint8Array(raw.length);
  for(let i=0;i<raw.length;i++) out[i]=raw.charCodeAt(i);
  return out;
}
function decodeJwtPart(part){ return JSON.parse(new TextDecoder().decode(b64urlToBytes(part))); }
async function verifyGithubOidc(request){
  const auth=request.headers.get('authorization')||'';
  if(!auth.startsWith('Bearer ')) throw new Error('missing_bearer');
  const token=auth.slice(7).trim(); const parts=token.split('.');
  if(parts.length!==3) throw new Error('invalid_jwt');
  const header=decodeJwtPart(parts[0]); const claims=decodeJwtPart(parts[1]);
  if(header.alg!=='RS256'||!header.kid) throw new Error('unsupported_jwt_header');
  const configResp=await fetch(`${OIDC_ISSUER}/.well-known/openid-configuration`,{cf:{cacheTtl:3600}});
  if(!configResp.ok) throw new Error('oidc_config_unavailable');
  const config=await configResp.json();
  const jwksResp=await fetch(config.jwks_uri,{cf:{cacheTtl:3600}});
  if(!jwksResp.ok) throw new Error('oidc_jwks_unavailable');
  const jwks=await jwksResp.json(); const jwk=(jwks.keys||[]).find(k=>k.kid===header.kid);
  if(!jwk) throw new Error('oidc_kid_not_found');
  const key=await crypto.subtle.importKey('jwk',jwk,{name:'RSASSA-PKCS1-v1_5',hash:'SHA-256'},false,['verify']);
  const verified=await crypto.subtle.verify('RSASSA-PKCS1-v1_5',key,b64urlToBytes(parts[2]),new TextEncoder().encode(`${parts[0]}.${parts[1]}`));
  if(!verified) throw new Error('oidc_signature_invalid');
  const now=Math.floor(Date.now()/1000);
  if(claims.iss!==OIDC_ISSUER) throw new Error('oidc_issuer_invalid');
  const aud=Array.isArray(claims.aud)?claims.aud:[claims.aud];
  if(!aud.includes(OIDC_AUDIENCE)) throw new Error('oidc_audience_invalid');
  if(!claims.exp||claims.exp<now-30) throw new Error('oidc_expired');
  if(claims.repository!==ALLOWED_REPOSITORY) throw new Error('oidc_repository_denied');
  if(!ALLOWED_REF_PREFIXES.some(p=>String(claims.ref||'').startsWith(p))) throw new Error('oidc_ref_denied');
  if(claims.event_name&&claims.event_name!=='push') throw new Error('oidc_event_denied');
  return {repository:claims.repository,ref:claims.ref,run_id:claims.run_id||null};
}
function bytesToBase64(bytes){
  let raw=''; const chunk=0x8000;
  for(let i=0;i<bytes.length;i+=chunk) raw+=String.fromCharCode(...bytes.subarray(i,Math.min(i+chunk,bytes.length)));
  return btoa(raw);
}
async function sha256Hex(text){
  const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text));
  return [...new Uint8Array(digest)].map(b=>b.toString(16).padStart(2,'0')).join('');
}
async function handleImage(request,env,identity){
  let body; try{body=await request.json();}catch{return json({ok:false,error:'invalid_json'},400);}
  const prompt=String(body?.prompt||'').trim();
  if(!prompt||prompt.length>MAX_IMAGE_PROMPT_CHARS) return json({ok:false,error:'prompt_invalid'},400);
  const started=Date.now();
  try{
    const result=await env.AI.run(IMAGE_MODEL,{prompt,steps:4});
    const image=String(result?.image??result?.result?.image??'');
    if(image.length<1000) throw new Error('image_empty');
    const bytes=Uint8Array.from(atob(image),c=>c.charCodeAt(0));
    return new Response(bytes,{status:200,headers:{
      'content-type':'image/jpeg','cache-control':'no-store','x-lsi-model':IMAGE_MODEL,'x-lsi-zero-cost-route':'true',
      'x-lsi-external-paid-provider':'false','x-lsi-elapsed-ms':String(Date.now()-started),
      'x-lsi-prompt-sha256':await sha256Hex(prompt),'x-lsi-run-id':String(identity.run_id||'')
    }});
  }catch(e){ return json({ok:false,error:'image_generation_failed',detail:String(e?.message??e).slice(0,300),external_paid_provider:false},503); }
}
async function handleTranscribe(request,env,identity,url){
  const contentLength=Number(request.headers.get('content-length')||0);
  if(contentLength>MAX_AUDIO_BYTES) return json({ok:false,error:'audio_too_large'},413);
  const audioBuffer=await request.arrayBuffer();
  if(audioBuffer.byteLength<100||audioBuffer.byteLength>MAX_AUDIO_BYTES) return json({ok:false,error:'audio_size_invalid'},400);
  const language=String(url.searchParams.get('language')||'').trim().toLowerCase();
  if(language&&!['pt','en','es'].includes(language)) return json({ok:false,error:'language_not_allowed'},400);
  const base64=bytesToBase64(new Uint8Array(audioBuffer));
  const started=Date.now();
  try{
    const input={audio:base64,task:'transcribe',vad_filter:true,condition_on_previous_text:false};
    if(language) input.language=language;
    const result=await env.AI.run(TRANSCRIBE_MODEL,input);
    const text=String(result?.text??result?.result?.text??'').trim();
    if(!text) throw new Error('transcript_empty');
    return json({ok:true,provider:'cloudflare_workers_ai',model:TRANSCRIBE_MODEL,text,word_count:Number(result?.word_count??0),vtt:String(result?.vtt??''),elapsed_ms:Date.now()-started,zero_cost_route:true,external_paid_provider:false,identity:{repository:identity.repository,ref:identity.ref,run_id:identity.run_id}});
  }catch(e){ return json({ok:false,error:'transcription_failed',detail:String(e?.message??e).slice(0,300),external_paid_provider:false},503); }
}
export default {
  async fetch(request,env){
    const url=new URL(request.url);
    if(request.method==='GET'&&url.pathname==='/health') return json({ok:true,service:'lsi-media-worker',version:VERSION,workers_ai_bound:Boolean(env.AI),image_model:IMAGE_MODEL,transcribe_model:TRANSCRIBE_MODEL,image_steps:4,max_audio_bytes:MAX_AUDIO_BYTES,production_publication:false,external_paid_provider:false});
    if(!env.AI) return json({ok:false,error:'workers_ai_binding_missing'},503);
    let identity; try{identity=await verifyGithubOidc(request);}catch(e){return json({ok:false,error:'oidc_denied',detail:String(e?.message??e)},401);}
    if(request.method==='POST'&&url.pathname==='/v1/image') return handleImage(request,env,identity);
    if(request.method==='POST'&&url.pathname==='/v1/transcribe') return handleTranscribe(request,env,identity,url);
    return json({ok:false,error:'not_found'},404);
  }
};
