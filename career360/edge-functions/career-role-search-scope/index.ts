import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const cors={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type","Access-Control-Allow-Methods":"POST, OPTIONS"};
function json(status:number,body:any){return new Response(JSON.stringify(body),{status,headers:{...cors,"Content-Type":"application/json","Cache-Control":"no-store"}})}

Deno.serve(async(req)=>{
  if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
  if(req.method!=="POST")return json(405,{error:"METHOD_NOT_ALLOWED"});
  const h=req.headers.get("Authorization");if(!h?.startsWith("Bearer "))return json(401,{error:"AUTH_REQUIRED"});
  const url=Deno.env.get("SUPABASE_URL"),anon=Deno.env.get("SUPABASE_ANON_KEY"),sk=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!url||!anon||!sk)return json(500,{error:"SERVER_CONFIG_ERROR"});
  const uc=createClient(url,anon,{global:{headers:{Authorization:h}},auth:{persistSession:false,autoRefreshToken:false}});
  const{data:u,error:ue}=await uc.auth.getUser();if(ue||!u.user)return json(401,{error:"INVALID_SESSION"});
  const service:any=createClient(url,sk,{auth:{persistSession:false,autoRefreshToken:false}});
  let body:any={};try{body=await req.json()}catch{}
  const action=String(body?.action||"get");
  if(action==="set_mode"){
    const mode=String(body?.mode||"");if(!["strict","balanced","broad"].includes(mode))return json(400,{error:"INVALID_MODE"});
    const {error}=await service.from("career_role_expansion_preferences").upsert({user_id:u.user.id,expansion_mode:mode,updated_at:new Date().toISOString()},{onConflict:"user_id"});if(error)return json(503,{error:"PREFERENCE_UPDATE_FAILED"});
  }
  const [{data:plan,error:pe},{data:matchingCtl,error:ce}]=await Promise.all([
    service.rpc("career_build_role_search_plan",{p_user_id:u.user.id,p_persist:true}),
    service.from("career_engine_control").select("champion_version,rollback_version,status").eq("component","matching").maybeSingle()
  ]);
  if(pe)return json(503,{error:"ROLE_PLAN_FAILED"});
  if(ce)return json(503,{error:"MATCHING_CONTROL_READ_FAILED"});
  const titles=Array.isArray(plan?.search_titles)?plan.search_titles:[];
  const groups:any={direct:[],current:[],equivalent:[],progression:[],correlated:[]};
  for(const x of titles){const item={title:x.title,language:x.language,weight:x.weight,role_key:x.role_key,scope_fit:x.scope_fit,seniority_rank:x.seniority_rank};if(x.tier==="core")groups.direct.push(item);else if(x.tier==="current")groups.current.push(item);else if(x.tier==="equivalent")groups.equivalent.push(item);else if(x.tier==="progression")groups.progression.push(item);else groups.correlated.push(item)}
  const uniq=(xs:any[])=>{const seen=new Set();return xs.filter(x=>{const k=String(x.title||"").toLowerCase();if(seen.has(k))return false;seen.add(k);return true}).slice(0,20)};
  Object.keys(groups).forEach(k=>groups[k]=uniq(groups[k]));
  return json(200,{
    status:"ROLE_SEARCH_SCOPE_READY",
    version:plan?.version||"role-search-v2",
    mode:plan?.policy?.expansion_mode||"balanced",
    groups,
    policy:plan?.policy||{},
    matching_engine:matchingCtl?.status==="active"?matchingCtl?.champion_version:null,
    rollback_engine:matchingCtl?.rollback_version||null,
    principle:"EXPAND_BY_ROLE_GRAPH_SCOPE_AND_SENIORITY"
  });
});
