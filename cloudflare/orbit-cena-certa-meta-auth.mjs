const EXPECTED_PAGE_ID = '1314911305035494';
const REDIRECT_URI = 'https://orbit-cena-certa-meta-auth.umagestaointeligente.workers.dev/oauth/callback';
const DEFAULT_GRAPH_VERSION = 'v23.0';
const META_SCOPES = ['pages_show_list','pages_read_engagement','pages_manage_posts'];

function json(x,status=200){ return Response.json(x,{status,headers:{'cache-control':'no-store'}}); }
function html(body,status=200){ return new Response(`<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cena Certa Meta OAuth</title><body style="font-family:system-ui;max-width:760px;margin:48px auto;padding:20px">${body}</body>`,{status,headers:{'content-type':'text/html; charset=utf-8','cache-control':'no-store'}}); }
function randomString(n=32){ const a=new Uint8Array(n); crypto.getRandomValues(a); return Array.from(a,b=>b.toString(16).padStart(2,'0')).join(''); }
function safeEq(a,b){ if(typeof a!=='string'||typeof b!=='string'||a.length!==b.length) return false; let d=0; for(let i=0;i<a.length;i++) d|=a.charCodeAt(i)^b.charCodeAt(i); return d===0; }
async function sha256hex(s){ const b=new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s))); return Array.from(b,x=>x.toString(16).padStart(2,'0')).join(''); }

export class MetaAuthState {
  constructor(state,env){ this.state=state; this.env=env; }
  async fetch(req){
    const u=new URL(req.url);
    if(u.pathname==='/put' && req.method==='POST'){
      const x=await req.json();
      if(x.oauth_state) await this.state.storage.put('oauth:'+x.oauth_state,{expires:Date.now()+10*60*1000});
      if(x.page_access_token) await this.state.storage.put('page_access_token',x.page_access_token);
      if(x.page_id) await this.state.storage.put('page_id',String(x.page_id));
      if(x.page_name) await this.state.storage.put('page_name',String(x.page_name));
      if(x.tasks) await this.state.storage.put('tasks',x.tasks);
      return json({ok:true});
    }
    if(u.pathname==='/consume' && req.method==='POST'){
      const {oauth_state}=await req.json(); const key='oauth:'+oauth_state; const v=await this.state.storage.get(key); await this.state.storage.delete(key); return json({value:v??null});
    }
    if(u.pathname==='/get'){
      const key=u.searchParams.get('key'); return json({value:(await this.state.storage.get(key))??null});
    }
    if(u.pathname==='/status'){
      const page_id=await this.state.storage.get('page_id');
      const page_name=await this.state.storage.get('page_name');
      const has_page_access_token=!!(await this.state.storage.get('page_access_token'));
      const tasks=(await this.state.storage.get('tasks'))||[];
      return json({ok:true,authorized:has_page_access_token&&page_id===EXPECTED_PAGE_ID,page_id:page_id||null,page_name:page_name||null,has_page_access_token,tasks});
    }
    return new Response('not found',{status:404});
  }
}
function stub(env){ return env.META_AUTH_STATE.get(env.META_AUTH_STATE.idFromName('cena-certa')); }
async function doGet(env,key){ return (await (await stub(env).fetch('https://do/get?key='+encodeURIComponent(key))).json()).value; }
function graph(env,path){ const v=(env.GRAPH_VERSION||DEFAULT_GRAPH_VERSION).trim(); if(!/^v\d+\.\d+$/.test(v)) throw new Error('INVALID_GRAPH_VERSION'); return `https://graph.facebook.com/${v}${path}`; }

async function graphGet(env,path,params,token){
  const q=new URLSearchParams(params||{}); q.set('access_token',token);
  const r=await fetch(graph(env,path)+'?'+q.toString(),{headers:{'cache-control':'no-store'}}); const d=await r.json();
  if(!r.ok) throw new Error('META_GET_'+r.status+'_'+JSON.stringify(d).slice(0,1200)); return d;
}
async function graphPost(env,path,params,token){
  const body=new URLSearchParams(params||{}); body.set('access_token',token);
  const r=await fetch(graph(env,path),{method:'POST',headers:{'content-type':'application/x-www-form-urlencoded'},body}); const d=await r.json();
  if(!r.ok) throw new Error('META_POST_'+r.status+'_'+JSON.stringify(d).slice(0,1200)); return d;
}

async function pageToken(env){
  const token=await doGet(env,'page_access_token'); const page=await doGet(env,'page_id');
  if(!token||page!==EXPECTED_PAGE_ID) throw new Error('META_AUTH_NOT_READY');
  const me=await graphGet(env,'/me',{fields:'id,name'},token);
  if(String(me.id)!==EXPECTED_PAGE_ID) throw new Error('META_PAGE_IDENTITY_MISMATCH');
  return token;
}

async function scheduleVideo(env,p){
  for(const k of ['item_key','media_url','publish_at']) if(!p[k]||typeof p[k]!=='string') throw new Error('INVALID_'+k.toUpperCase());
  const publishMs=Date.parse(p.publish_at); if(!Number.isFinite(publishMs)||publishMs<=Date.now()+10*60*1000) throw new Error('PUBLISH_AT_NOT_FUTURE_ENOUGH');
  if(!/^https:\/\//.test(p.media_url)) throw new Error('MEDIA_URL_NOT_HTTPS');
  if((p.format||'video')!=='video') throw new Error('FORMAT_FAIL_CLOSED');
  const token=await pageToken(env);
  const marker='orbit_'+(await sha256hex(p.item_key)).slice(0,24);
  const recent=await graphGet(env,'/'+EXPECTED_PAGE_ID+'/videos',{fields:'id,description,created_time,scheduled_publish_time,published',limit:'100'},token);
  for(const v of (recent.data||[])){
    if((v.description||'').includes(marker)){
      const requested=Math.floor(publishMs/1000), existing=Number(v.scheduled_publish_time||0);
      if(existing&&Math.abs(existing-requested)>2) throw new Error('IDEMPOTENCY_KEY_CONFLICT');
      return {ok:true,result:'ALREADY_EXISTS',page_id:EXPECTED_PAGE_ID,video_id:String(v.id),publish_at:p.publish_at,mutation_performed:false};
    }
  }
  const description=((p.caption||'').trim()+'\n\n'+marker).trim();
  const out=await graphPost(env,'/'+EXPECTED_PAGE_ID+'/videos',{file_url:p.media_url,description,published:'false',scheduled_publish_time:String(Math.floor(publishMs/1000))},token);
  if(!out.id) throw new Error('UNCERTAIN_AFTER_POST_NO_ID');
  const verify=await graphGet(env,'/'+encodeURIComponent(out.id),{fields:'id,description,scheduled_publish_time,published'},token);
  if(String(verify.id)!==String(out.id)||!(verify.description||'').includes(marker)||verify.published===true) throw new Error('UNCERTAIN_AFTER_POST_READBACK_MISMATCH');
  return {ok:true,result:'SCHEDULED',page_id:EXPECTED_PAGE_ID,video_id:String(out.id),publish_at:p.publish_at,scheduled_publish_time:verify.scheduled_publish_time||null,published:verify.published??null,mutation_performed:true};
}

export default {
  async fetch(req,env){
    const u=new URL(req.url);
    if(u.pathname==='/health') return json({ok:true,service:'orbit-cena-certa-meta-auth',expected_page_id:EXPECTED_PAGE_ID,mutation_mode:'guarded',stories:'fail-closed'});
    if(u.pathname==='/status') return stub(env).fetch('https://do/status');
    if(u.pathname==='/start'){
      if(!env.META_APP_ID) return html('<h2>AUTH_GATE</h2><p>META_APP_ID ausente.</p>',503);
      const oauth_state=randomString(24);
      await stub(env).fetch('https://do/put',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({oauth_state})});
      const q=new URLSearchParams({client_id:env.META_APP_ID,redirect_uri:REDIRECT_URI,state:oauth_state,response_type:'code',scope:META_SCOPES.join(',')});
      return Response.redirect('https://www.facebook.com/dialog/oauth?'+q.toString(),302);
    }
    if(u.pathname==='/oauth/callback'){
      const err=u.searchParams.get('error'); if(err) return html(`<h2>Autorização não concluída</h2><p>${err}</p>`,400);
      const code=u.searchParams.get('code'), oauth_state=u.searchParams.get('state'); if(!code||!oauth_state) return html('<h2>Callback inválido</h2>',400);
      const consumed=await (await stub(env).fetch('https://do/consume',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({oauth_state})})).json();
      if(!consumed.value||consumed.value.expires<Date.now()) return html('<h2>AUTH_GATE</h2><p>Estado OAuth inválido ou expirado.</p>',400);
      if(!env.META_APP_ID||!env.META_APP_SECRET) return html('<h2>AUTH_GATE</h2><p>Credenciais do app Meta ausentes no Worker.</p>',503);
      const tq=new URLSearchParams({client_id:env.META_APP_ID,client_secret:env.META_APP_SECRET,redirect_uri:REDIRECT_URI,code});
      const tr=await fetch(graph(env,'/oauth/access_token')+'?'+tq.toString()); const td=await tr.json();
      if(!tr.ok||!td.access_token) return html(`<h2>AUTH_GATE</h2><p>Falha na troca do código OAuth (${tr.status}).</p>`,502);
      const lq=new URLSearchParams({grant_type:'fb_exchange_token',client_id:env.META_APP_ID,client_secret:env.META_APP_SECRET,fb_exchange_token:td.access_token});
      const lr=await fetch(graph(env,'/oauth/access_token')+'?'+lq.toString()); const ld=await lr.json(); const userToken=(lr.ok&&ld.access_token)?ld.access_token:td.access_token;
      let accounts;
      try{ accounts=await graphGet(env,'/me/accounts',{fields:'id,name,access_token,tasks',limit:'100'},userToken); }
      catch(e){ return html('<h2>IDENTITY_GATE</h2><p>Não foi possível listar as páginas autorizadas.</p>',409); }
      const page=(accounts.data||[]).find(x=>String(x.id)===EXPECTED_PAGE_ID);
      if(!page||!page.access_token) return html(`<h2>IDENTITY_GATE</h2><p>A página Cena Certa Ofc (${EXPECTED_PAGE_ID}) não veio na autorização.</p>`,409);
      const me=await graphGet(env,'/me',{fields:'id,name'},page.access_token);
      if(String(me.id)!==EXPECTED_PAGE_ID) return html('<h2>IDENTITY_GATE</h2><p>O token obtido não pertence à página canônica.</p>',409);
      await stub(env).fetch('https://do/put',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({page_access_token:page.access_token,page_id:String(page.id),page_name:page.name||me.name||'Cena Certa Ofc',tasks:page.tasks||[]})});
      return html(`<h2>✅ Cena Certa Facebook autorizado</h2><p>Página: <strong>${page.name||me.name||'Cena Certa Ofc'}</strong></p><p>ID: ${page.id}</p><p>Token armazenado internamente. Você pode voltar ao ChatGPT.</p>`);
    }
    if(u.pathname==='/schedule'&&req.method==='POST'){
      const auth=req.headers.get('authorization')||'', given=auth.startsWith('Bearer ')?auth.slice(7):'';
      if(!env.COMMAND_TOKEN||!safeEq(given,env.COMMAND_TOKEN)) return json({ok:false,error:'COMMAND_GATE'},403);
      try{return json(await scheduleVideo(env,await req.json()));}
      catch(e){const error=String(e?.message||e); const uncertain=error.startsWith('UNCERTAIN_AFTER_POST'); return json({ok:false,error,mutation_performed:uncertain?null:false,mutation_state:uncertain?'unknown_after_post':'none'},409);}
    }
    return new Response('not found',{status:404});
  }
};
