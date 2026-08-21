from __future__ import annotations
import json, os, re, secrets, time
from pathlib import Path
import requests
import scripts.r44_5_18_repair_v2 as base

STATUS=Path('cloudflare/status/r44-5-19-final.txt')
WORKER='lola-operacional-ugi'
ORIGIN='https://lola-operacional-ugi.umagestaointeligente.workers.dev'
OLD='lola-v8-r44-5-18-permanent-publication-link-policy-2026-08-21'
NEW='lola-v8-r44-5-19-commerce-hub-visual-caption-2026-08-21'
HUB=ORIGIN+'/materiais'
POSTS={'instagram':'6a87d61b1b38003a90c37507','tiktok':'6a87d61f1b38003a90c3752d','youtube':'6a87d6231b38003a90c3755b'}
CAPTION='''🎯 Priorizar tudo é não priorizar nada.\n\nQuando tudo vira urgente, a equipe perde clareza, energia e velocidade.\n\n⚠️ Mais tarefas abertas\n🔄 Mais retrabalho\n⏳ Mais tempo desperdiçado\n📉 Menos foco no que realmente importa\n\n💡 Priorizar é decidir o que entra — e também o que sai do foco.\n\n📋 Kit UGI — Priorização Inteligente\n💰 R$ 14,99\n\n🛍️ Acesse nossos materiais pelo link na Bio.\n\n#UmaGestaoInteligente #Gestao #Lideranca #Produtividade #Priorizacao'''

def write(lines): STATUS.parent.mkdir(parents=True,exist_ok=True); STATUS.write_text('\n'.join(lines)+'\n',encoding='utf-8')
def fetch_live(api,h):
 r=requests.get(api+'/content/v2',headers=h,timeout=30); r.raise_for_status(); return base.extract_source(r)
def bindings(api,h):
 r=requests.get(api+f'/versions/{base.STABLE_VERSION_ID}',headers=h,timeout=30); r.raise_for_status(); return base.restored_bindings(r.json())
def deploy(api,h,src,b,tag):
 v=base.create_version(api,h,src,b,tag); d=base.deploy(api,h,v,tag); return v,d
def wait(ver):
 last={}
 for _ in range(20):
  try:
   r=requests.get(ORIGIN+'/api/health',timeout=12)
   if r.status_code==200:
    last=r.json(); bd=last.get('bindings') or {}
    if last.get('ok') is True and last.get('version')==ver and bd.get('MEDIA_R2') is True and bd.get('BUFFER_API_KEY') is True and bd.get('ASAAS_API_KEY') is True:return last
  except Exception: pass
  time.sleep(3)
 raise RuntimeError('health timeout '+json.dumps(last,ensure_ascii=False)[:800])

def patch(src):
 t=base.strip_temp_routes(src)
 t=re.sub(r'\n\s*// BEGIN_R44_5_19_.*?// END_R44_5_19_.*?\s*\n','\n',t,flags=re.S)
 old=f'var VERSION = "{OLD}";'
 if old in t:t=t.replace(old,f'var VERSION = "{NEW}";',1)
 elif f'var VERSION = "{NEW}";' not in t:raise RuntimeError('version anchor mismatch')
 pat=r'function permanentCommercePublicationText\(draft = \{\}\) \{.*?\n\}\n__name\(permanentCommercePublicationText, "permanentCommercePublicationText"\);'
 repl=r'''function permanentCommercePublicationText(draft = {}) {
  const commerce=draft?.commerce||{}; const commercial=draft?.commercialOffer===true||commerce?.required===true;
  const topic=String(draft?.topic||draft?.title||draft?.theme||"").toLowerCase(); let original=String(draft?.text||"").trim();
  original=original.replace(/https:\/\/(?:www\.)?asaas\.com\/checkoutSession\/show(?:\/[A-Za-z0-9_-]+|\?id=[^\s]+)/gi,"").replace(/https:\/\/lola-operacional-ugi\.umagestaointeligente\.workers\.dev\/priorizacao/gi,"").replace(/\n{3,}/g,"\n\n").trim();
  const emoji=topic.includes("prior")?"🎯":topic.includes("delega")?"🤝":topic.includes("process")?"⚙️":topic.includes("planej")?"🧭":topic.includes("lider")?"👥":topic.includes("reuni")?"🗓️":topic.includes("ia")?"🤖":"💡";
  if(original&&!/^[\p{Extended_Pictographic}]/u.test(original)) original=emoji+" "+original;
  if(!original.includes("\n\n")){const s=original.split(/(?<=[.!?])\s+/).filter(Boolean);if(s.length>=3){const g=[];for(let i=0;i<s.length;i+=2)g.push(s.slice(i,i+2).join(" "));original=g.join("\n\n");}}
  if(commercial){const pt=String(draft?.productTitle||commerce?.productTitle||"Material UGI");const p=Number(draft?.price||commerce?.price||0);const pl=Number.isFinite(p)&&p>0?"\n💰 R$ "+p.toFixed(2).replace(".",","):"";original+="\n\n📋 "+pt+pl+"\n\n🛍️ Acesse nossos materiais pelo link na Bio.";}
  return original.replace(/\n{3,}/g,"\n\n").trim();
}
__name(permanentCommercePublicationText, "permanentCommercePublicationText");'''
 t,n=re.subn(pat,repl,t,count=1,flags=re.S)
 if n!=1:raise RuntimeError('caption helper replacement failed')
 anchor='      if (request.method === "GET" && path === "/priorizacao") {'
 if t.count(anchor)!=1:raise RuntimeError('priorizacao anchor mismatch')
 route=r'''      if (request.method === "GET" && path === "/materiais") {
        const product=await getJsonR2(env, `${PRODUCT_PREFIX}UGI-MATERIAL-PRIORIDADES-001.json`);
        const material=await getJsonR2(env, `${MATERIAL_PREFIX}UGI-KIT-PRIORIZACAO-001.json`);
        const ok=product&&material&&product.status==="active"&&material.assetReady===true&&material.qualityStatus==="PASS"&&material.deliveryEnabled===true;
        const card=ok?`<article class="card"><div class="tag">MATERIAL UGI</div><h2>${escapeCommerceHtml(product.title||material.title||"Kit UGI")}</h2><p>${escapeCommerceHtml(product.description||material.description||"")}</p><div class="price">R$ ${Number(product.price||0).toFixed(2).replace(".",",")}</div><a class="buy" href="${url.origin}/priorizacao">Ver material</a></article>`:`<p>Nenhum material disponível neste momento.</p>`;
        const page=`<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Materiais UGI</title><style>body{margin:0;background:#061A2B;color:#fff;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif}.wrap{max-width:900px;margin:auto;padding:30px 18px 60px}.brand{color:#E7A72C;font-weight:900}h1{font-size:36px;line-height:1.05}.lead{color:#cbd5e1;line-height:1.6}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;margin-top:28px}.card{background:#fff;color:#172232;border-radius:22px;padding:24px}.tag{font-size:12px;font-weight:900;color:#9a6a00}.card p{color:#52606f;line-height:1.5}.price{font-size:28px;font-weight:900;margin:18px 0}.buy{display:block;text-align:center;text-decoration:none;background:#E7A72C;color:#061A2B;padding:15px;border-radius:13px;font-weight:900}</style></head><body><main class="wrap"><div class="brand">UGI · UMA GESTÃO INTELIGENTE</div><h1>Materiais práticos para uma gestão melhor.</h1><p class="lead">Escolha o material que resolve seu problema agora.</p><section class="grid">${card}</section></main></body></html>`;
        return new Response(page,{status:200,headers:{"Content-Type":"text/html; charset=utf-8","Cache-Control":"no-store"}});
      }

'''
 t=t.replace(anchor,route+anchor,1)
 hanchor='            permanentCommerceEntrypoint: true,\n'
 if t.count(hanchor)!=1:raise RuntimeError('health anchor mismatch')
 t=t.replace(hanchor,hanchor+'            commerceHubEntrypoint: true,\n            commerceHubUrl: "/materiais",\n            visualCaptionBlocks: true,\n            visualCaptionEmojiPolicy: "semantic_light",\n            commercialCaptionCta: "link_na_bio",\n',1)
 return t

def add_repair(src,path,token):
 anchor='      if (request.method === "GET" && path === "/materiais") {'
 ids=json.dumps(POSTS); cap=json.dumps(CAPTION,ensure_ascii=False)
 route=r'''      // BEGIN_R44_5_19_SLOT02_REPAIR
      if(request.method==="POST"&&path===__PATH__&&url.searchParams.get("token")===__TOKEN__){const ids=__IDS__,caption=__CAPTION__,results=[];for(const [platform,id] of Object.entries(ids)){const bq=`query { post(input:{id:${JSON.stringify(id)}}) { id text status dueAt sentAt assets { id type mimeType source ... on VideoAsset { video { thumbnailOffset title } } } } }`;const bw=await bufferGraphQL(bq,env),before=bw?.data?.post||{};if(!before.id||before.sentAt||String(before.status||"").toLowerCase()==="sent"){results.push({platform,id,ok:false,error:"post_not_mutable"});continue;}const videos=(before.assets||[]).filter(a=>String(a.type||"").toLowerCase()==="video");if(videos.length!==1||!videos[0].source){results.push({platform,id,ok:false,error:"video_missing"});continue;}const v=videos[0],vm=v.video||{},dueAt=before.dueAt||null;let dq=null;if(platform==="instagram")dq=`query { post(input:{id:${JSON.stringify(id)}}) { metadata { ... on InstagramPostMetadata { type shouldShareToFeed isAiGenerated } } } }`;if(platform==="tiktok")dq=`query { post(input:{id:${JSON.stringify(id)}}) { metadata { ... on TiktokPostMetadata { type isAiGenerated title } } } }`;if(platform==="youtube")dq=`query { post(input:{id:${JSON.stringify(id)}}) { metadata { ... on YoutubePostMetadata { type title category { categoryId title } } } } }`;const dw=await bufferGraphQL(dq,env),meta=dw?.data?.post?.metadata||{};const asset=`assets:[{video:{url:${JSON.stringify(v.source)},metadata:{thumbnailOffset:${Number(vm.thumbnailOffset||0)}${vm.title?`,title:${JSON.stringify(vm.title)}`:""}}}}]`;let md="";if(platform==="instagram")md=`metadata:{instagram:{type:${String(meta.type||"reel")},shouldShareToFeed:${meta.shouldShareToFeed!==false},isAiGenerated:${meta.isAiGenerated===true}}}`;if(platform==="tiktok")md=`metadata:{tiktok:{isAiGenerated:${meta.isAiGenerated===true}}}`;if(platform==="youtube"){const title=meta.title||vm.title,cat=meta.category?.categoryId;if(!title||!cat){results.push({platform,id,ok:false,error:"youtube_metadata_missing"});continue;}md=`metadata:{youtube:{title:${JSON.stringify(title)},categoryId:${JSON.stringify(cat)}}}`;}const mq=`mutation { editPost(input:{id:${JSON.stringify(id)},text:${JSON.stringify(caption)},aiAssisted:true,${asset},${md}}) { __typename ... on PostActionSuccess { post { id text status dueAt sentAt assets { id type source } } } ... on MutationError { message } } }`;const ew=await bufferGraphQL(mq,env),payload=ew?.data?.editPost;if(!payload?.post?.id){results.push({platform,id,ok:false,error:payload?.message||"edit_failed"});continue;}const aw=await bufferGraphQL(bq,env),after=aw?.data?.post||{},av=(after.assets||[]).filter(a=>String(a.type||"").toLowerCase()==="video");const ok=after.text===caption&&(after.dueAt||null)===dueAt&&av.length===1&&av[0].source===v.source&&!/asaas\.com\/checkoutSession\/show/i.test(after.text||"");results.push({platform,id,ok,status:after.status||null,dueAt:after.dueAt||null,schedulePreserved:(after.dueAt||null)===dueAt,videoPreserved:av.length===1&&av[0].source===v.source,visualCaptionApplied:after.text===caption,tempCheckoutAbsent:!/asaas\.com\/checkoutSession\/show/i.test(after.text||"")});}return json({ok:results.length===3&&results.every(x=>x.ok),version:VERSION,results});}
      // END_R44_5_19_SLOT02_REPAIR

'''.replace('__PATH__',json.dumps(path)).replace('__TOKEN__',json.dumps(token)).replace('__IDS__',ids).replace('__CAPTION__',cap)
 return src.replace(anchor,route+anchor,1)

def strip_repair(s):return re.sub(r'\n\s*// BEGIN_R44_5_19_SLOT02_REPAIR.*?// END_R44_5_19_SLOT02_REPAIR\s*\n','\n',s,flags=re.S)

def main():
 lines=['R44.5.19_STAGE=COMMERCE_HUB_VISUAL_CAPTION'];write(lines+['OK=false','STATE=STARTED'])
 tok=os.environ['CF_API_TOKEN'];acct=os.environ['CF_ACCOUNT_ID'];h={'Authorization':f'Bearer {tok}'};api=f'https://api.cloudflare.com/client/v4/accounts/{acct}/workers/scripts/{WORKER}'
 live=fetch_live(api,h);final=patch(live);b=bindings(api,h);lines += [f'BASE_SOURCE_BYTES={len(live.encode())}','BINDINGS_PRESERVED=19']
 p='/__ugi_slot02_caption_'+secrets.token_hex(10);t=secrets.token_urlsafe(24);temp=add_repair(final,p,t);deploy(api,h,temp,b,'UGI R44.5.19 temp Slot02 caption');wait(NEW)
 rr=None
 for _ in range(20):
  rr=requests.post(ORIGIN+p,params={'token':t},timeout=45)
  try:
   dat=rr.json()
   if isinstance(dat,dict) and isinstance(dat.get('results'),list):break
  except Exception:pass
  time.sleep(3)
 if rr is None or rr.status_code!=200:raise RuntimeError('repair http failure')
 dat=rr.json()
 if not dat.get('ok'):raise RuntimeError('repair failed '+json.dumps(dat,ensure_ascii=False)[:2200])
 lines.append('SLOT02_VISUAL_CAPTION_REPAIR_PASS=true')
 for row in dat['results']:lines.append('BUFFER_POST='+row['id']+' PLATFORM='+row['platform']+' STATUS='+str(row.get('status'))+' DUE_AT='+str(row.get('dueAt'))+' SCHEDULE_PRESERVED=true VIDEO_PRESERVED=true VISUAL_CAPTION_APPLIED=true TEMP_CHECKOUT_ABSENT=true')
 final=strip_repair(final);fv,fd=deploy(api,h,final,b,'UGI R44.5.19 commerce hub + visual captions');wait(NEW)
 page=requests.get(HUB,timeout=20)
 if page.status_code!=200 or 'Materiais práticos' not in page.text or 'Priorização' not in page.text or 'R$ 14,99' not in page.text:raise RuntimeError('hub validation failed')
 lines += ['FINAL_VERSION_ID='+fv,'FINAL_DEPLOYMENT_ID='+fd,'TEMP_REPAIR_ENDPOINT_REMOVED=true','COMMERCE_HUB_HTTP=200','COMMERCE_HUB_URL='+HUB,'VISUAL_CAPTION_BLOCKS=true','VISUAL_CAPTION_EMOJI_POLICY=semantic_light','COMMERCIAL_CTA_POLICY=link_na_bio','OK=true'];write(lines)

if __name__=='__main__':
 try:main()
 except BaseException as e:
  try:x=STATUS.read_text(encoding='utf-8').splitlines() if STATUS.exists() else []
  except Exception:x=[]
  x += ['ERROR_TYPE='+type(e).__name__,'ERROR='+str(e).replace('\n',' ')[:5000],'OK=false'];write(x);raise
