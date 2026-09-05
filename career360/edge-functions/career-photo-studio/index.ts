import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const BUCKET = 'career-profile-private';
const MAX = 8 * 1024 * 1024;
const cors = {
  'Access-Control-Allow-Origin':'*',
  'Access-Control-Allow-Headers':'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods':'GET, POST, OPTIONS'
};
const json = (status:number, body:any) => new Response(JSON.stringify(body), {status, headers:{...cors,'Content-Type':'application/json','Cache-Control':'no-store'}});
const clean = (v:any,max=220) => typeof v === 'string' ? v.replace(/[\u0000-\u001f\u007f]/g,' ').replace(/\s+/g,' ').trim().slice(0,max) : '';
const arr = (v:any) => Array.isArray(v) ? v.map(x=>clean(x,180)).filter(Boolean) : [];
const hex = (a:ArrayBuffer) => [...new Uint8Array(a)].map(b=>b.toString(16).padStart(2,'0')).join('');
function detect(b:Uint8Array){
  if(b.length>=3&&b[0]===0xff&&b[1]===0xd8&&b[2]===0xff)return{mime:'image/jpeg',ext:'jpg'};
  if(b.length>=8&&b[0]===0x89&&b[1]===0x50&&b[2]===0x4e&&b[3]===0x47)return{mime:'image/png',ext:'png'};
  if(b.length>=12&&String.fromCharCode(...b.slice(0,4))==='RIFF'&&String.fromCharCode(...b.slice(8,12))==='WEBP')return{mime:'image/webp',ext:'webp'};
  return null;
}
async function auth(req:Request){
  const h=req.headers.get('Authorization');
  if(!h?.startsWith('Bearer '))return{error:json(401,{error:'AUTH_REQUIRED'})};
  const url=Deno.env.get('SUPABASE_URL'), anon=Deno.env.get('SUPABASE_ANON_KEY'), key=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if(!url||!anon||!key)return{error:json(500,{error:'SERVER_CONFIG_ERROR'})};
  const uc=createClient(url,anon,{global:{headers:{Authorization:h}},auth:{persistSession:false,autoRefreshToken:false}});
  const {data,error}=await uc.auth.getUser();
  if(error||!data.user)return{error:json(401,{error:'INVALID_SESSION'})};
  return{user:data.user,service:createClient(url,key,{auth:{persistSession:false,autoRefreshToken:false}})};
}
function styleFrom(role:string,targets:string[]){
  const t=(role+' '+targets.join(' ')).toLowerCase();
  if(/diretor|director|head|vp|vice president|chief|executiv|gerente s[eê]nior|senior manager/.test(t))return'executive';
  if(/comercial|sales|business development|category|compras|procurement|buyer|trade|revenue/.test(t))return'commercial';
  if(/tech|tecnolog|product|produto|data|dados|engineer|software|developer|digital/.test(t))return'modern';
  if(/marketing|design|creative|criativ|brand|conte[uú]do|content/.test(t))return'creative';
  return'professional';
}
function plan(style:string,role:string,targets:string[]){
  const map:any={
    executive:{title:'Executivo contemporâneo',background:'neutro sofisticado, discreto e luminoso',presentation:'enquadramento de liderança, luz equilibrada e acabamento sóbrio'},
    commercial:{title:'Corporativo natural',background:'corporativo claro, acolhedor e limpo',presentation:'presença profissional, acessível e confiante'},
    modern:{title:'Profissional moderno',background:'minimalista moderno, claro e sem distrações',presentation:'visual limpo, atual e objetivo'},
    creative:{title:'Profissional expressivo',background:'editorial leve e elegante, sem excesso visual',presentation:'acabamento contemporâneo com personalidade sutil'},
    professional:{title:'Profissional natural',background:'neutro claro e limpo',presentation:'enquadramento clássico, discreto e atemporal'}
  }[style]||{};
  const career=clean([role,...targets.slice(0,2)].filter(Boolean).join(' / '),180);
  return{style_key:style,title:map.title,career_basis:career,background:map.background,presentation:map.presentation,prompt_version:'career-photo-local-v1'};
}
async function signed(s:any,path:string|null){
  if(!path)return null;
  const {data,error}=await s.storage.from(BUCKET).createSignedUrl(path,3600);
  return error?null:data?.signedUrl||null;
}
async function sources(s:any,uid:string){
  const [m,pref,prof,prefs]=await Promise.all([
    s.from('career_profile_media').select('id,storage_object_path,mime_type,size_bytes,sha256,updated_at').eq('user_id',uid).eq('media_type','profile_photo').maybeSingle(),
    s.from('career_profile_photo_settings').select('*').eq('user_id',uid).maybeSingle(),
    s.from('career_profiles').select('current_role_title').eq('user_id',uid).maybeSingle(),
    s.from('career_preferences').select('target_roles').eq('user_id',uid).maybeSingle()
  ]);
  const role=clean(prof.data?.current_role_title,180), targets=arr(prefs.data?.target_roles);
  const auto=styleFrom(role,targets), style=pref.data?.preferred_style_key||auto;
  return{media:m.data||null,pref:pref.data||null,role,targets,style,plan:plan(style,role,targets)};
}
async function audit(s:any,uid:string,type:string,id:string|null,outcome:string,reason:string,meta:any={}){
  await s.from('career_audit_events').insert({user_id:uid,event_type:type,entity_type:'career_profile_photo_variants',entity_id:id,outcome,reason_code:reason,metadata_safe:meta});
}
async function removeGeneratedCandidates(s:any,uid:string,sourceId:string){
  const {data:old}=await s.from('career_profile_photo_variants').select('id,storage_object_path').eq('user_id',uid).eq('source_media_id',sourceId).eq('status','generated');
  const paths=(old||[]).map((x:any)=>x.storage_object_path).filter(Boolean);
  if(paths.length)await s.storage.from(BUCKET).remove(paths);
  if((old||[]).length)await s.from('career_profile_photo_variants').update({status:'rejected',storage_object_path:null,decided_at:new Date().toISOString()}).eq('user_id',uid).eq('source_media_id',sourceId).eq('status','generated');
}
async function storeVariant(s:any,uid:string,sourceId:string,bytes:Uint8Array,kind:any,style:string,meta:any={}){
  await removeGeneratedCandidates(s,uid,sourceId);
  const path=`${uid}/variants/${crypto.randomUUID()}.${kind.ext}`;
  const {error:up}=await s.storage.from(BUCKET).upload(path,bytes,{contentType:kind.mime,cacheControl:'0',upsert:false});
  if(up)throw new Error('VARIANT_STORAGE_FAILED');
  const sha=hex(await crypto.subtle.digest('SHA-256',bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength) as ArrayBuffer));
  const {data,error}=await s.from('career_profile_photo_variants').insert({
    user_id:uid,source_media_id:sourceId,provider:'local-studio-v1',style_key:style,prompt_version:'career-photo-local-v1',
    storage_object_path:path,mime_type:kind.mime,size_bytes:bytes.byteLength,sha256:sha,status:'generated',metadata_safe:meta
  }).select('id,provider,style_key,status,created_at,storage_object_path,mime_type,size_bytes').single();
  if(error||!data){await s.storage.from(BUCKET).remove([path]);throw new Error('VARIANT_METADATA_FAILED');}
  await audit(s,uid,'professional_photo_variant',data.id,'generated','local-studio-v1',{style_key:style});
  return{...data,url:await signed(s,path)};
}
Deno.serve(async(req:Request)=>{
  if(req.method==='OPTIONS')return new Response('ok',{headers:cors});
  const c:any=await auth(req); if(c.error)return c.error;
  const uid=c.user.id,s=c.service,src=await sources(s,uid);
  if(req.method==='GET'){
    const {data:vs}=await s.from('career_profile_photo_variants').select('id,provider,style_key,status,created_at,storage_object_path,mime_type,size_bytes').eq('user_id',uid).neq('status','rejected').order('created_at',{ascending:false}).limit(6);
    const variants:any[]=[];
    for(const v of vs||[])variants.push({...v,url:await signed(s,v.storage_object_path)});
    const original=src.media?{...src.media,url:await signed(s,src.media.storage_object_path)}:null;
    const selected=src.pref?.selected_kind==='variant'&&src.pref?.selected_variant_id?variants.find((x:any)=>x.id===src.pref.selected_variant_id)||original:original;
    return json(200,{status:'PHOTO_STUDIO_READY',original,selected,variants,style_plan:src.plan,capabilities:{local_studio:true,ai_generation:false,ai_provider:null,ai_opt_in:src.pref?.ai_opt_in!==false},matching_usage:false});
  }
  if(req.method!=='POST')return json(405,{error:'METHOD_NOT_ALLOWED'});
  const ct=req.headers.get('content-type')||'';
  let action='',body:any={},form:FormData|null=null;
  if(ct.includes('multipart/form-data')){form=await req.formData();action=clean(form.get('action'),40);}else{try{body=await req.json()}catch{} action=clean(body?.action,40);}
  if(!src.media)return json(409,{error:'ORIGINAL_PHOTO_REQUIRED'});
  if(action==='save_local_variant'){
    const f=form?.get('file');
    if(!(f instanceof File))return json(400,{error:'VARIANT_FILE_REQUIRED'});
    if(f.size<=0||f.size>MAX)return json(413,{error:'VARIANT_TOO_LARGE'});
    const bytes=new Uint8Array(await f.arrayBuffer()),kind=detect(bytes);
    if(!kind)return json(415,{error:'PHOTO_TYPE_NOT_ALLOWED'});
    try{return json(201,{status:'VARIANT_READY',variant:await storeVariant(s,uid,src.media.id,bytes,kind,src.style,{career_basis:src.plan.career_basis,presentation:src.plan.presentation,identity_preservation:true,generation_mode:'local_mediapipe_canvas_v1'})});}
    catch(e){return json(503,{error:String((e as Error).message||e)});}
  }
  if(action==='generate_ai')return json(503,{error:'AI_PROVIDER_NOT_CONFIGURED',fallback:'local_studio',style_plan:src.plan});
  if(action==='accept'){
    const id=clean(body?.variant_id,80); if(!id)return json(400,{error:'VARIANT_ID_REQUIRED'});
    const {data:v}=await s.from('career_profile_photo_variants').select('id,status,source_media_id').eq('id',id).eq('user_id',uid).maybeSingle();
    if(!v||v.status==='rejected'||v.source_media_id!==src.media.id)return json(404,{error:'VARIANT_NOT_FOUND'});
    await s.from('career_profile_photo_variants').update({status:'superseded'}).eq('user_id',uid).eq('status','accepted').neq('id',id);
    const {error}=await s.from('career_profile_photo_variants').update({status:'accepted',decided_at:new Date().toISOString()}).eq('id',id).eq('user_id',uid);
    if(error)return json(503,{error:'VARIANT_ACCEPT_FAILED'});
    await s.from('career_profile_photo_settings').upsert({user_id:uid,selected_kind:'variant',selected_variant_id:id,preferred_style_key:src.style,ai_opt_in:src.pref?.ai_opt_in!==false,updated_at:new Date().toISOString()},{onConflict:'user_id'});
    await audit(s,uid,'professional_photo_variant',id,'accepted','USER_CONFIRMED',{style_key:src.style});
    return json(200,{status:'VARIANT_ACCEPTED',variant_id:id});
  }
  if(action==='keep_original'){
    await s.from('career_profile_photo_settings').upsert({user_id:uid,selected_kind:'original',selected_variant_id:null,preferred_style_key:src.style,ai_opt_in:src.pref?.ai_opt_in!==false,updated_at:new Date().toISOString()},{onConflict:'user_id'});
    await s.from('career_profile_photo_variants').update({status:'superseded'}).eq('user_id',uid).eq('status','accepted');
    await audit(s,uid,'professional_photo_selection',null,'original_selected','USER_CONFIRMED',{});
    return json(200,{status:'ORIGINAL_SELECTED'});
  }
  if(action==='reject'){
    const id=clean(body?.variant_id,80); if(!id)return json(400,{error:'VARIANT_ID_REQUIRED'});
    const {data:v}=await s.from('career_profile_photo_variants').select('id,storage_object_path,status').eq('id',id).eq('user_id',uid).maybeSingle();
    if(!v||v.status==='accepted')return json(409,{error:'VARIANT_CANNOT_BE_REJECTED'});
    if(v.storage_object_path)await s.storage.from(BUCKET).remove([v.storage_object_path]);
    await s.from('career_profile_photo_variants').update({status:'rejected',storage_object_path:null,decided_at:new Date().toISOString()}).eq('id',id).eq('user_id',uid);
    await audit(s,uid,'professional_photo_variant',id,'rejected','USER_REJECTED',{});
    return json(200,{status:'VARIANT_REJECTED'});
  }
  if(action==='set_style'){
    const style=clean(body?.style_key,30);
    if(!['executive','commercial','modern','creative','professional'].includes(style))return json(400,{error:'INVALID_STYLE'});
    await s.from('career_profile_photo_settings').upsert({user_id:uid,selected_kind:src.pref?.selected_kind||'original',selected_variant_id:src.pref?.selected_variant_id||null,preferred_style_key:style,ai_opt_in:src.pref?.ai_opt_in!==false,updated_at:new Date().toISOString()},{onConflict:'user_id'});
    return json(200,{status:'STYLE_UPDATED',style_key:style});
  }
  if(action==='set_ai_opt_in'){
    const enabled=Boolean(body?.enabled);
    await s.from('career_profile_photo_settings').upsert({user_id:uid,selected_kind:src.pref?.selected_kind||'original',selected_variant_id:src.pref?.selected_variant_id||null,preferred_style_key:src.style,ai_opt_in:enabled,updated_at:new Date().toISOString()},{onConflict:'user_id'});
    return json(200,{status:'AI_OPT_IN_UPDATED',enabled});
  }
  return json(400,{error:'UNKNOWN_ACTION'});
});