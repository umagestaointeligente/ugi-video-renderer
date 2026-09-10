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
      return Response.json({ok:true});
    }
    if(u.pathname==='/get'){
      const key=u.searchParams.get('key'); const v=await this.state.storage.get(key);
      return Response.json({value:v??null});
    }
    if(u.pathname==='/consume' && req.method==='POST'){
      const {state}=await req.json(); const key='state:'+state; const v=await this.state.storage.get(key); await this.state.storage.delete(key);
      return Response.json({value:v??null});
    }
    if(u.pathname==='/status'){
      const channel_id=await this.state.storage.get('channel_id'); const channel_title=await this.state.storage.get('channel_title'); const has_refresh_token=!!(await this.state.storage.get('youtube_refresh_token'));
      return Response.json({ok:true,authorized:has_refresh_token && channel_id===EXPECTED_CHANNEL_ID,channel_id:channel_id||null,channel_title:channel_title||null,has_refresh_token});
    }
    return new Response('not found',{status:404});
  }
}

function stub(env){ return env.AUTH_STATE.get(env.AUTH_STATE.idFromName('cena-certa')); }

export default {
  async fetch(req, env){
    const u=new URL(req.url);
    if(u.pathname==='/health') return Response.json({ok:true,service:'orbit-cena-certa-auth',expected_channel_id:EXPECTED_CHANNEL_ID,mutation_enabled:false});
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
    return new Response('not found',{status:404});
  }
};
