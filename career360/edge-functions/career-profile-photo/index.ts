import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const BUCKET='career-profile-private';
const MAX=5*1024*1024;
const cors={
  'Access-Control-Allow-Origin':'*',
  'Access-Control-Allow-Headers':'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods':'GET, POST, DELETE, OPTIONS'
};
const json=(status:number,body:any)=>new Response(JSON.stringify(body),{status,headers:{...cors,'Content-Type':'application/json','Cache-Control':'no-store'}});
const hex=(a:ArrayBuffer)=>[...new Uint8Array(a)].map(b=>b.toString(16).padStart(2,'0')).join('');
function detect(b:Uint8Array){
  if(b.length>=3&&b[0]===0xff&&b[1]===0xd8&&b[2]===0xff)return{mime:'image/jpeg',ext:'jpg'};
  if(b.length>=8&&b[0]===0x89&&b[1]===0x50&&b[2]===0x4e&&b[3]===0x47&&b[4]===0x0d&&b[5]===0x0a&&b[6]===0x1a&&b[7]===0x0a)return{mime:'image/png',ext:'png'};
  if(b.length>=12&&String.fromCharCode(...b.slice(0,4))==='RIFF'&&String.fromCharCode(...b.slice(8,12))==='WEBP')return{mime:'image/webp',ext:'webp'};
  return null;
}
async function auth(req:Request){
  const h=req.headers.get('Authorization');
  if(!h?.startsWith('Bearer '))return{error:json(401,{error:'AUTH_REQUIRED'})};
  const url=Deno.env.get('SUPABASE_URL'),anon=Deno.env.get('SUPABASE_ANON_KEY'),key=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if(!url||!anon||!key)return{error:json(500,{error:'SERVER_CONFIG_ERROR'})};
  const uc=createClient(url,anon,{global:{headers:{Authorization:h}},auth:{persistSession:false,autoRefreshToken:false}});
  const {data,error}=await uc.auth.getUser();
  if(error||!data.user)return{error:json(401,{error:'INVALID_SESSION'})};
  return{user:data.user,service:createClient(url,key,{auth:{persistSession:false,autoRefreshToken:false}})};
}
async function ensureBucket(s:any){
  const {data}=await s.storage.getBucket(BUCKET);
  if(data)return true;
  const {error}=await s.storage.createBucket(BUCKET,{public:false,fileSizeLimit:8*1024*1024,allowedMimeTypes:['image/jpeg','image/png','image/webp']});
  return !error;
}
async function sign(s:any,path:string|null){
  if(!path)return null;
  const {data,error}=await s.storage.from(BUCKET).createSignedUrl(path,3600);
  return error?null:data?.signedUrl||null;
}
async function audit(s:any,uid:string,outcome:string,reason:string,id:string|null,meta:any={}){
  await s.from('career_audit_events').insert({user_id:uid,event_type:'profile_photo',entity_type:'career_profile_media',entity_id:id,outcome,reason_code:reason,metadata_safe:meta});
}
Deno.serve(async(req:Request)=>{
  if(req.method==='OPTIONS')return new Response('ok',{headers:cors});
  const c:any=await auth(req); if(c.error)return c.error;
  const uid=c.user.id,s=c.service;

  if(req.method==='GET'){
    const {data:media,error}=await s.from('career_profile_media').select('id,storage_object_path,mime_type,size_bytes,sha256,created_at,updated_at').eq('user_id',uid).eq('media_type','profile_photo').maybeSingle();
    if(error)return json(503,{error:'PHOTO_LOOKUP_FAILED'});
    if(!media)return json(200,{status:'NO_PHOTO',photo:null,original:null});
    const {data:pref}=await s.from('career_profile_photo_settings').select('selected_kind,selected_variant_id').eq('user_id',uid).maybeSingle();
    let active:any=null,kind='original';
    if(pref?.selected_kind==='variant'&&pref?.selected_variant_id){
      const {data:v}=await s.from('career_profile_photo_variants').select('id,source_media_id,storage_object_path,mime_type,size_bytes,sha256,style_key,provider,created_at,decided_at,status').eq('id',pref.selected_variant_id).eq('user_id',uid).eq('status','accepted').maybeSingle();
      if(v&&v.source_media_id===media.id&&v.storage_object_path){active=v;kind='professional';}
    }
    const originalUrl=await sign(s,media.storage_object_path);
    const activeUrl=active?await sign(s,active.storage_object_path):originalUrl;
    if(!activeUrl)return json(503,{error:'PHOTO_SIGN_FAILED'});
    return json(200,{
      status:'PHOTO_READY',
      photo:{url:activeUrl,mime_type:active?.mime_type||media.mime_type,size_bytes:active?.size_bytes||media.size_bytes,updated_at:active?.decided_at||media.updated_at,kind,variant_id:active?.id||null,style_key:active?.style_key||null},
      original:{url:originalUrl,mime_type:media.mime_type,size_bytes:media.size_bytes,updated_at:media.updated_at},
      matching_usage:false,identity_disclosure:false
    });
  }

  if(req.method==='DELETE'){
    const {data:media}=await s.from('career_profile_media').select('id,storage_object_path').eq('user_id',uid).eq('media_type','profile_photo').maybeSingle();
    if(!media)return json(200,{status:'NO_PHOTO'});
    const {data:variants}=await s.from('career_profile_photo_variants').select('storage_object_path').eq('user_id',uid).eq('source_media_id',media.id);
    const paths=[media.storage_object_path,...(variants||[]).map((x:any)=>x.storage_object_path)].filter(Boolean);
    await s.from('career_profile_photo_settings').delete().eq('user_id',uid);
    await s.from('career_profile_photo_variants').delete().eq('user_id',uid).eq('source_media_id',media.id);
    const {error}=await s.from('career_profile_media').delete().eq('id',media.id).eq('user_id',uid);
    if(error)return json(503,{error:'PHOTO_DELETE_FAILED'});
    if(paths.length)await s.storage.from(BUCKET).remove(paths);
    await audit(s,uid,'deleted','USER_REQUESTED',media.id,{});
    return json(200,{status:'PHOTO_DELETED'});
  }

  if(req.method!=='POST')return json(405,{error:'METHOD_NOT_ALLOWED'});
  const length=Number(req.headers.get('content-length')||'0');
  if(length&&length>MAX+512000)return json(413,{error:'PHOTO_TOO_LARGE'});
  let form:FormData; try{form=await req.formData();}catch{return json(400,{error:'INVALID_MULTIPART'});}
  const f=form.get('file');
  if(!(f instanceof File))return json(400,{error:'PHOTO_REQUIRED'});
  if(f.size<=0||f.size>MAX)return json(413,{error:'PHOTO_TOO_LARGE',max_bytes:MAX});
  const bytes=new Uint8Array(await f.arrayBuffer()),kind=detect(bytes);
  if(!kind)return json(415,{error:'PHOTO_TYPE_NOT_ALLOWED'});
  if(!(await ensureBucket(s)))return json(503,{error:'PHOTO_BUCKET_UNAVAILABLE'});
  const sha=hex(await crypto.subtle.digest('SHA-256',bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength) as ArrayBuffer));
  const path=`${uid}/${crypto.randomUUID()}.${kind.ext}`;
  const {error:up}=await s.storage.from(BUCKET).upload(path,bytes,{contentType:kind.mime,cacheControl:'0',upsert:false});
  if(up)return json(503,{error:'PHOTO_UPLOAD_FAILED'});
  const {data:old}=await s.from('career_profile_media').select('id,storage_object_path').eq('user_id',uid).eq('media_type','profile_photo').maybeSingle();
  const now=new Date().toISOString();
  const {data:row,error:write}=await s.from('career_profile_media').upsert({user_id:uid,media_type:'profile_photo',storage_object_path:path,mime_type:kind.mime,size_bytes:f.size,sha256:sha,updated_at:now},{onConflict:'user_id,media_type'}).select('id,updated_at').single();
  if(write||!row){await s.storage.from(BUCKET).remove([path]);return json(503,{error:'PHOTO_METADATA_WRITE_FAILED'});}

  const sourceId=row.id;
  await s.from('career_profile_photo_settings').upsert({user_id:uid,selected_kind:'original',selected_variant_id:null,updated_at:now},{onConflict:'user_id'});
  const {data:variants}=await s.from('career_profile_photo_variants').select('storage_object_path').eq('user_id',uid).eq('source_media_id',sourceId);
  const variantPaths=(variants||[]).map((x:any)=>x.storage_object_path).filter(Boolean);
  await s.from('career_profile_photo_variants').delete().eq('user_id',uid).eq('source_media_id',sourceId);
  if(variantPaths.length)await s.storage.from(BUCKET).remove(variantPaths);
  if(old?.storage_object_path&&old.storage_object_path!==path)await s.storage.from(BUCKET).remove([old.storage_object_path]);

  await audit(s,uid,'uploaded','USER_CONFIRMED',row.id,{mime_type:kind.mime,size_bytes:f.size,professional_variants_reset:true});
  const url=await sign(s,path);
  return json(201,{status:'PHOTO_READY',photo:{url,mime_type:kind.mime,size_bytes:f.size,updated_at:row.updated_at,kind:'original',variant_id:null},matching_usage:false,identity_disclosure:false});
});