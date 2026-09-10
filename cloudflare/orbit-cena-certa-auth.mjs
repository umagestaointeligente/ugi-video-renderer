const EXPECTED_CHANNEL_ID = 'UCq1h6RSnev5-JJQ8k4T98tg';
const REDIRECT_URI = 'https://orbit-cena-certa-auth.umagestaointeligente.workers.dev/oauth/callback';
const SCOPE = 'https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly';

function b64url(bytes) {
  let s=''; for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
}
function randomString(n=32){ const a=new Uint8Array(n); crypto.getRandomValues(a); return b64url(a); }
async function sha256(s){ return new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s))); }
function html(body, status=200){ return new Response(`<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cena Certa OAuth</title><body style="font-family:system-ui;max-width:720px;margin:48px auto;padding:20px">${body}</body>`,{status,headers:{'content-type':'text/html; charset=utf-8','cache-control':'no-store'}}); }
function json(x,status=200){ return Response.json(x,{status,headers:{'cache-control':'no-store'}}); }
function safeEq(a,b){
  if(typeof a!=='string'||typeof b!=='string'||a.length!==b.length) return false;
  let d=0; for(let i=0;i<a.length;i++) d|=a.charCodeAt(i)^b.charCodeAt(i); return d===0;
}

export class AuthState {
  constructor(state, env){ this.state=state; this.env=env; }
  async fetch(req){
    const u=new URL(req.url);
    if(u.pathname==='/put' && req.method==='POST'){
      const x=await req.json();
      if(x.state) await this.state.storage.put('state:'+x.state,{verifier:x.verifier,expires:Date.now()+10*60*1000});
      if(x.refresh_token) await this.state.storage.put('youtube_refresh_token',x.refresh_token);
      if(x.channel_id) await this.state.storage.put('channel_id',x.channel_id);
      if(x.channel_title) await this.state.storage.put('channel_title',x.channel_title);
      return json({ok:true});
    }
    if(u.pathname==='/get'){
      const key=u.searchParams.get('key'); const v=await this.state.storage.get(key);
      return json({value:v??null});
    }
    if(u.pathname==='/consume' && req.method==='POST'){
      const {state}=await req.json(); const key='state:'+state; const v=await this.state.storage.get(key); await this.state.storage.delete(key);
      return json({value:v??null});
    }
    if(u.pathname==='/status'){
      const channel_id=await this.state.storage.get('channel_id'); const channel_title=await this.state.storage.get('channel_title'); const has_refresh_token=!!(await this.state.storage.get('youtube_refresh_token'));
      return json({ok:true,authorized:has_refresh_token && channel_id===EXPECTED_CHANNEL_ID,channel_id:channel_id||null,channel_title:channel_title||null,has_refresh_token});
    }
    return new Response('not found',{status:404});
  }
}

function stub(env){ return env.AUTH_STATE.get(env.AUTH_STATE.idFromName('cena-certa')); }
async function doGet(env,key){ return (await (await stub(env).fetch('https://do/get?key='+encodeURIComponent(key))).json()).value; }
async function accessToken(env){
  const refresh=await doGet(env,'youtube_refresh_token');
  const channel=await doGet(env,'channel_id');
  if(!refresh||channel!==EXPECTED_CHANNEL_ID) throw new Error('AUTH_NOT_READY');
  const body=new URLSearchParams({client_id:env.YOUTUBE_CLIENT_ID,client_secret:env.YOUTUBE_CLIENT_SECRET,refresh_token:refresh,grant_type:'refresh_token'});
  const r=await fetch('https://oauth2.googleapis.com/token',{method:'POST',headers:{'content-type':'application/x-www-form-urlencoded'},body});
  const d=await r.json(); if(!r.ok||!d.access_token) throw new Error('TOKEN_REFRESH_FAILED_'+r.status);
  return d.access_token;
}
async function channelPreflight(token){
  const r=await fetch('https://www.googleapis.com/youtube/v3/channels?part=id,snippet,contentDetails&mine=true',{headers:{authorization:'Bearer '+token}});
  const d=await r.json(); if(!r.ok) throw new Error('CHANNEL_PREFLIGHT_'+r.status);
  const items=d.items||[]; if(items.length!==1||items[0].id!==EXPECTED_CHANNEL_ID) throw new Error('CHANNEL_IDENTITY_MISMATCH');
  return items[0];
}
async function findExisting(token, uploadsId, title){
  let page='';
  for(let n=0;n<4;n++){
    const q=new URLSearchParams({part:'snippet,status',playlistId:uploadsId,maxResults:'50'}); if(page) q.set('pageToken',page);
    const r=await fetch('https://www.googleapis.com/youtube/v3/playlistItems?'+q,{headers:{authorization:'Bearer '+token}});
    const d=await r.json(); if(!r.ok) throw new Error('DUPLICATE_PREFLIGHT_'+r.status);
    for(const it of (d.items||[])) if((it.snippet?.title||'')===title) return {videoId:it.snippet?.resourceId?.videoId||null,title};
    page=d.nextPageToken||''; if(!page) break;
  }
  return null;
}
async function scheduleVideo(env,p){
  const required=['item_key','title','description','media_url','publish_at'];
  for(const k of required) if(!p[k]||typeof p[k]!=='string') throw new Error('INVALID_'+k.toUpperCase());
  const publishMs=Date.parse(p.publish_at); if(!Number.isFinite(publishMs)||publishMs<=Date.now()+5*60*1000) throw new Error('PUBLISH_AT_NOT_FUTURE_ENOUGH');
  if(!/^https:\/\//.test(p.media_url)) throw new Error('MEDIA_URL_NOT_HTTPS');
  if(p.title.length>100) throw new Error('TITLE_TOO_LONG');

  const token=await accessToken(env);
  const ch=await channelPreflight(token);
  const uploadsId=ch.contentDetails?.relatedPlaylists?.uploads; if(!uploadsId) throw new Error('UPLOADS_PLAYLIST_MISSING');
  const existing=await findExisting(token,uploadsId,p.title);
  if(existing) return {ok:true,result:'ALREADY_EXISTS',item_key:p.item_key,channel_id:EXPECTED_CHANNEL_ID,video_id:existing.videoId,title:p.title,publish_at:p.publish_at,mutation_performed:false};

  const src=await fetch(p.media_url,{redirect:'follow'});
  if(!src.ok||!src.body) throw new Error('MEDIA_FETCH_'+src.status);
  const ctype=src.headers.get('content-type')||'video/mp4';
  if(!ctype.toLowerCase().includes('video')) throw new Error('MEDIA_NOT_VIDEO');
  const len=src.headers.get('content-length');
  const metadata={snippet:{title:p.title,description:p.description,categoryId:'24'},status:{privacyStatus:'private',publishAt:new Date(publishMs).toISOString(),selfDeclaredMadeForKids:false,containsSyntheticMedia:false}};
  const initHeaders={'authorization':'Bearer '+token,'content-type':'application/json; charset=UTF-8','x-upload-content-type':ctype}; if(len) initHeaders['x-upload-content-length']=len;
  const init=await fetch('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',{method:'POST',headers:initHeaders,body:JSON.stringify(metadata)});
  if(!init.ok){ const t=(await init.text()).slice(0,800); throw new Error('UPLOAD_INIT_'+init.status+'_'+t); }
  const loc=init.headers.get('location'); if(!loc) throw new Error('UPLOAD_LOCATION_MISSING');
  const upHeaders={'authorization':'Bearer '+token,'content-type':ctype}; if(len) upHeaders['content-length']=len;
  const up=await fetch(loc,{method:'PUT',headers:upHeaders,body:src.body});
  const vd=await up.json(); if(!up.ok||!vd.id) throw new Error('UPLOAD_FINAL_'+up.status+'_'+JSON.stringify(vd).slice(0,800));
  if(vd.snippet?.channelId!==EXPECTED_CHANNEL_ID) throw new Error('POST_UPLOAD_CHANNEL_MISMATCH');
  const verify=await fetch('https://www.googleapis.com/youtube/v3/videos?part=id,snippet,status&id='+encodeURIComponent(vd.id),{headers:{authorization:'Bearer '+token}});
  const vj=await verify.json(); const v=(vj.items||[])[0]; if(!verify.ok||!v) throw new Error('VERIFY_FAILED_'+verify.status);
  if(v.snippet?.channelId!==EXPECTED_CHANNEL_ID||v.status?.privacyStatus!=='private') throw new Error('VERIFY_STATE_MISMATCH');
  return {ok:true,result:'SCHEDULED',item_key:p.item_key,channel_id:EXPECTED_CHANNEL_ID,video_id:v.id,title:v.snippet?.title||p.title,privacy_status:v.status?.privacyStatus,publish_at:v.status?.publishAt||p.publish_at,mutation_performed:true};
}

export default {
  async fetch(req, env){
    const u=new URL(req.url);
    if(u.pathname==='/health') return json({ok:true,service:'orbit-cena-certa-auth',expected_channel_id:EXPECTED_CHANNEL_ID,mutation_mode:'guarded'});
    if(u.pathname==='/status') return stub(env).fetch('https://do/status');
    if(u.pathname==='/start'){
      if(!env.YOUTUBE_CLIENT_ID) return html('<h2>AUTH_GATE</h2><p>YOUTUBE_CLIENT_ID ausente.</p>',503);
      const state=randomString(24), verifier=randomString(64), challenge=b64url(await sha256(verifier));
      await stub(env).fetch('https://do/put',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({state,verifier})});
      const q=new URLSearchParams({client_id:env.YOUTUBE_CLIENT_ID,redirect_uri:REDIRECT_URI,response_type:'code',scope:SCOPE,access_type:'offline',prompt:'consent',include_granted_scopes:'true',code_challenge:challenge,code_challenge_method:'S256',state});
      return Response.redirect('https://accounts.google.com/o/oauth2/v2/auth?'+q.toString(),302);
    }
    if(u.pathname==='/oauth/callback'){
      const err=u.searchParams.get('error'); if(err) return html(`<h2>Autorização não concluída</h2><p>${err}</p>`,400);
      const code=u.searchParams.get('code'), state=u.searchParams.get('state'); if(!code||!state) return html('<h2>Callback inválido</h2>',400);
      const consumed=await (await stub(env).fetch('https://do/consume',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({state})})).json();
      const saved=consumed.value; if(!saved||saved.expires<Date.now()) return html('<h2>AUTH_GATE</h2><p>Estado OAuth inválido ou expirado.</p>',400);
      const body=new URLSearchParams({client_id:env.YOUTUBE_CLIENT_ID,client_secret:env.YOUTUBE_CLIENT_SECRET,code,code_verifier:saved.verifier,redirect_uri:REDIRECT_URI,grant_type:'authorization_code'});
      const tr=await fetch('https://oauth2.googleapis.com/token',{method:'POST',headers:{'content-type':'application/x-www-form-urlencoded'},body});
      const tok=await tr.json(); if(!tr.ok||!tok.access_token) return html(`<h2>AUTH_GATE</h2><p>Falha na troca do código OAuth (${tr.status}).</p>`,502);
      const cr=await fetch('https://www.googleapis.com/youtube/v3/channels?part=id,snippet&mine=true',{headers:{authorization:'Bearer '+tok.access_token}}); const cd=await cr.json();
      const items=cd.items||[]; if(items.length!==1) return html('<h2>IDENTITY_GATE</h2><p>Conta sem identidade única de canal.</p>',409);
      const ch=items[0], cid=ch.id||'', title=ch.snippet?.title||'';
      if(cid!==EXPECTED_CHANNEL_ID) return html(`<h2>IDENTITY_GATE</h2><p>Canal autorizado não é o Cena Certa esperado.</p><p>Recebido: ${cid}</p>`,409);
      if(!tok.refresh_token) return html('<h2>AUTH_GATE</h2><p>Google não retornou refresh token. Revogue o consentimento anterior e tente novamente.</p>',409);
      await stub(env).fetch('https://do/put',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({refresh_token:tok.refresh_token,channel_id:cid,channel_title:title})});
      return html(`<h2>✅ Cena Certa autorizado</h2><p>Canal: <strong>${title}</strong></p><p>ID: ${cid}</p><p>O token foi armazenado internamente. Você pode voltar ao ChatGPT.</p>`);
    }
    if(u.pathname==='/schedule' && req.method==='POST'){
      const auth=req.headers.get('authorization')||''; const given=auth.startsWith('Bearer ')?auth.slice(7):'';
      if(!env.COMMAND_TOKEN||!safeEq(given,env.COMMAND_TOKEN)) return json({ok:false,error:'COMMAND_GATE'},403);
      try { return json(await scheduleVideo(env,await req.json())); }
      catch(e){ return json({ok:false,error:String(e?.message||e),mutation_performed:false},409); }
    }
    return new Response('not found',{status:404});
  }
};
