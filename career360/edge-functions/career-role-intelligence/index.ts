import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const cors={
  "Access-Control-Allow-Origin":"*",
  "Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods":"POST, OPTIONS",
};
function json(status:number,body:Record<string,unknown>){return new Response(JSON.stringify(body),{status,headers:{...cors,"Content-Type":"application/json","Cache-Control":"no-store"}})}
function clean(v:unknown,max=240){if(typeof v!=="string")return null;const s=v.replace(/[\u0000-\u001f\u007f]/g," ").replace(/\s+/g," ").trim();return s?s.slice(0,max):null}
function norm(v:string){return v.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[^a-z0-9+#&/ -]+/g," ").replace(/\s+/g," ").trim()}
function arr(v:unknown,max=30){if(!Array.isArray(v))return[];return v.map(x=>clean(x,300)).filter(Boolean).slice(0,max) as string[]}
async function auth(req:Request){
  const h=req.headers.get("Authorization");if(!h?.startsWith("Bearer "))return{error:json(401,{error:"AUTH_REQUIRED"})};
  const url=Deno.env.get("SUPABASE_URL"),anon=Deno.env.get("SUPABASE_ANON_KEY"),serviceKey=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!url||!anon||!serviceKey)return{error:json(500,{error:"SERVER_CONFIG_ERROR"})};
  const userClient=createClient(url,anon,{global:{headers:{Authorization:h}},auth:{persistSession:false,autoRefreshToken:false}});
  const {data,error}=await userClient.auth.getUser();if(error||!data.user)return{error:json(401,{error:"INVALID_SESSION"})};
  return{user:data.user,service:createClient(url,serviceKey,{auth:{persistSession:false,autoRefreshToken:false}})};
}
function flattenEmbedded(d:any){
  const out:any[]=[];const e=d?._embedded;
  if(Array.isArray(e))out.push(...e);
  else if(e&&typeof e==="object")for(const v of Object.values(e))if(Array.isArray(v))out.push(...v as any[]);
  if(Array.isArray(d?.results))out.push(...d.results);
  return out;
}
function labelsFrom(x:any,lang:string){
  const al:any=x?.alternativeLabel??x?.alternativeLabels??x?.altLabels??x?.altLabel??{};
  let vals:string[]=[];
  if(Array.isArray(al))vals=al;
  else if(al&&typeof al==="object"){
    const v=(al as any)[lang]??(al as any).en??(al as any).pt;
    if(Array.isArray(v))vals=v; else if(typeof v==="string")vals=[v];
  }
  return [...new Set(vals.map(v=>clean(v,250)).filter(Boolean) as string[])].slice(0,30);
}
function preferred(x:any,lang:string){return clean(x?.preferredLabel?.[lang]??x?.title??x?._links?.self?.title??x?.label,250)}
function uriOf(x:any){return clean(x?.uri??x?._links?.self?.uri??x?._links?.self?.href,500)}
async function escoSearch(q:string,lang:string){
  const ctrl=new AbortController();const timer=setTimeout(()=>ctrl.abort(),8000);
  try{
    const u=new URL("https://ec.europa.eu/esco/api/search");
    u.searchParams.set("text",q);u.searchParams.append("type","occupation");u.searchParams.set("language",lang);u.searchParams.set("limit","8");u.searchParams.set("full","true");u.searchParams.set("selectedVersion","latest");u.searchParams.set("viewObsolete","false");
    const r=await fetch(u.toString(),{headers:{Accept:"application/json","Accept-Language":lang},signal:ctrl.signal});
    if(!r.ok)throw new Error(`ESCO_${r.status}`);const d=await r.json();
    return flattenEmbedded(d).slice(0,8).map((x:any)=>({uri:uriOf(x),preferred_label:preferred(x,lang),alternative_labels:labelsFrom(x,lang),description:clean(x?.description?.[lang]??x?.description??x?.scopeNote?.[lang],1200),code:clean(x?.code??x?._links?.self?.code,120),raw_title:clean(x?.title,250)})).filter((x:any)=>x.preferred_label);
  } finally {clearTimeout(timer)}
}
function allowed(relation:string,p:any,weight:number){
  if(relation==="exact_alias"||relation==="market_equivalent")return true;
  if(relation==="scope_overlap")return !!p.allow_scope_overlap&&weight>=Number(p.min_relation_weight??0.65);
  if(relation==="career_adjacent")return !!p.allow_career_adjacent&&weight>=Number(p.min_relation_weight??0.65);
  if(relation==="progression_up")return !!p.allow_progression_up&&weight>=Number(p.min_relation_weight??0.65);
  if(relation==="progression_down")return !!p.allow_progression_down&&weight>=Number(p.min_relation_weight??0.65);
  return false;
}

Deno.serve(async(req)=>{
  if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
  if(req.method!=="POST")return json(405,{error:"METHOD_NOT_ALLOWED"});
  const ctx:any=await auth(req);if(ctx.error)return ctx.error;const user=ctx.user,service:any=ctx.service;
  let body:any={};try{body=await req.json()}catch{}
  const action=clean(body?.action,40)||"profile";
  const {data:prefRow}=await service.from("career_role_expansion_preferences").select("*").eq("user_id",user.id).maybeSingle();
  let pref=prefRow;
  if(!pref){const {data}=await service.from("career_role_expansion_preferences").upsert({user_id:user.id},{onConflict:"user_id"}).select("*").single();pref=data}

  if(action==="set_policy"){
    const patch:any={user_id:user.id,updated_at:new Date().toISOString()};
    if(["strict","balanced","broad"].includes(body?.expansion_mode))patch.expansion_mode=body.expansion_mode;
    for(const k of["allow_scope_overlap","allow_career_adjacent","allow_progression_up","allow_progression_down","use_scope_match"])if(typeof body?.[k]==="boolean")patch[k]=body[k];
    if(Number.isFinite(Number(body?.min_relation_weight)))patch.min_relation_weight=Math.max(0,Math.min(1,Number(body.min_relation_weight)));
    const {data,error}=await service.from("career_role_expansion_preferences").upsert(patch,{onConflict:"user_id"}).select("*").single();
    if(error)return json(503,{error:"POLICY_UPDATE_FAILED"});return json(200,{status:"ROLE_POLICY_UPDATED",preference:data});
  }

  if(action==="discover_esco"){
    const q=clean(body?.query,180);if(!q)return json(400,{error:"QUERY_REQUIRED"});
    const langs=arr(body?.languages,2).filter(x=>["pt","en"].includes(x));if(!langs.length)langs.push("pt","en");
    const all:any[]=[];const errors:any[]=[];
    for(const lang of langs){try{const rs=await escoSearch(q,lang);for(const x of rs){all.push({...x,language:lang});await service.from("career_role_external_candidates").upsert({query_text:q,normalized_query:norm(q),source_system:"esco",external_uri:x.uri,external_code:x.code,preferred_label:x.preferred_label,language:lang,alternative_labels:x.alternative_labels,description_safe:x.description,status:"suggested",evidence_safe:{source_version:"latest",retrieved_via:"esco_web_api"},fetched_at:new Date().toISOString()},{onConflict:"source_system,normalized_query,preferred_label,language"})}}catch(e){errors.push({language:lang,error:String((e as any)?.message||e).slice(0,120)})}}
    if(all.length)await service.from("career_role_taxonomy_sources").update({last_synced_at:new Date().toISOString(),integration_status:"live_api",updated_at:new Date().toISOString()}).eq("source_key","esco");
    return json(200,{status:"ESCO_DISCOVERY_COMPLETE",query:q,results:all.slice(0,16),errors});
  }

  const expandOne=async(title:string)=>{
    const {data,error}=await service.rpc("career_role_expand",{p_title:title,p_min_weight:Number(pref?.min_relation_weight??0.65)});if(error)return{title,error:"LOCAL_EXPANSION_FAILED",results:[]};
    const results=(data||[]).filter((x:any)=>allowed(String(x.relation_type||""),pref,Number(x.weight||0))).slice(0,60);
    return{title,results};
  };

  if(action==="expand"){
    const title=clean(body?.title,180);if(!title)return json(400,{error:"TITLE_REQUIRED"});
    const local=await expandOne(title);
    return json(200,{status:"ROLE_EXPANSION_READY",preference:pref,expansion:local});
  }

  if(action==="diagnostic"){
    const opportunityTitle=clean(body?.opportunity_title,180),targetTitle=clean(body?.target_title,180),description=clean(body?.description,8000)||"";
    if(!opportunityTitle||!targetTitle)return json(400,{error:"OPPORTUNITY_AND_TARGET_REQUIRED"});
    const {data,error}=await service.rpc("career_role_pair_diagnostic_v3",{p_opportunity_title:opportunityTitle,p_target_title:targetTitle,p_description:description});
    if(error)return json(503,{error:"ROLE_DIAGNOSTIC_FAILED"});
    return json(200,{status:"ROLE_DIAGNOSTIC_READY",diagnostic_engine:"v3",diagnostic:data?.[0]??null});
  }

  if(action!=="profile")return json(400,{error:"UNKNOWN_ACTION"});
  const [{data:p},{data:base},{data:taxonomy},{data:matchingCtl}]=await Promise.all([
    service.from("career_preferences").select("target_roles").eq("user_id",user.id).maybeSingle(),
    service.from("career_profiles").select("current_role_title").eq("user_id",user.id).maybeSingle(),
    service.from("career_role_taxonomy_sources").select("source_key,integration_status,source_version,last_synced_at,notes_safe").order("source_key"),
    service.from("career_engine_control").select("champion_version,rollback_version,status").eq("component","matching").maybeSingle()
  ]);
  const targets=arr(p?.target_roles,10);const current=clean(base?.current_role_title,180);const titles=[...new Set([...(current?[current]:[]),...targets])];
  const expansions=[];for(const t of titles)expansions.push(await expandOne(t));
  const sources=Object.fromEntries((taxonomy||[]).map((x:any)=>[x.source_key,{status:x.integration_status,version:x.source_version||null,last_synced_at:x.last_synced_at||null,notes_safe:x.notes_safe||{}}]));
  return json(200,{status:"ROLE_PROFILE_READY",preference:pref,current_role:current,target_roles:targets,expansions,matching:{champion:matchingCtl?.champion_version||null,rollback:matchingCtl?.rollback_version||null,status:matchingCtl?.status||null},sources});
});
