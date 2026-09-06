import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const cors={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type","Access-Control-Allow-Methods":"POST, OPTIONS"};
function json(status:number,body:Record<string,unknown>){return new Response(JSON.stringify(body),{status,headers:{...cors,"Content-Type":"application/json","Cache-Control":"no-store"}})}
const sleep=(ms:number)=>new Promise(r=>setTimeout(r,ms));

Deno.serve(async(req)=>{
  if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
  if(req.method!=="POST")return json(405,{error:"METHOD_NOT_ALLOWED"});
  const h=req.headers.get("Authorization");if(!h?.startsWith("Bearer "))return json(401,{error:"AUTH_REQUIRED"});
  const url=Deno.env.get("SUPABASE_URL"),anon=Deno.env.get("SUPABASE_ANON_KEY"),serviceKey=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!url||!anon||!serviceKey)return json(500,{error:"SERVER_CONFIG_ERROR"});
  const uc=createClient(url,anon,{global:{headers:{Authorization:h}},auth:{persistSession:false,autoRefreshToken:false}});
  const{data:u,error:ue}=await uc.auth.getUser();if(ue||!u.user)return json(401,{error:"INVALID_SESSION"});
  const service:any=createClient(url,serviceKey,{auth:{persistSession:false,autoRefreshToken:false}});

  let limit=5;
  try{const b=await req.json();limit=Math.max(1,Math.min(5,Number(b?.source_limit)||5))}catch{}

  const{data:requestId,error:startError}=await service.rpc("career_request_research_now",{p_user_id:u.user.id,p_source_limit:limit});
  if(startError){
    if(String(startError.message||"").includes("RESEARCH_COOLDOWN"))return json(429,{error:"RESEARCH_COOLDOWN",message:"Uma pesquisa já foi iniciada há poucos instantes. Aguarde a atualização do radar."});
    return json(503,{error:"RESEARCH_START_FAILED"});
  }

  let status:any=null;
  for(let i=0;i<28;i++){
    await sleep(700);
    const{data}=await service.rpc("career_research_request_status",{p_request_id:requestId});
    if(data?.status_code||data?.timed_out||data?.error_msg){status=data;break}
  }

  if(!status)return json(202,{status:"RESEARCH_RUNNING",request_id:requestId,source_limit:limit,message:"A pesquisa continua em execução e o radar será atualizado automaticamente."});
  if(status.timed_out||status.error_msg)return json(503,{error:"RESEARCH_EXECUTION_FAILED",request_id:requestId});

  let details:any=null;
  try{details=typeof status.content==="string"?JSON.parse(status.content):status.content}catch{}
  if(Number(status.status_code)!==200)return json(503,{error:"RESEARCH_EXECUTION_FAILED",request_id:requestId,status_code:status.status_code});

  const sources=Array.isArray(details?.sources)?details.sources:[];
  const totals=sources.reduce((a:any,s:any)=>{
    a.sources++;
    a.fetched+=Number(s.fetched||0);
    a.accepted+=Number(s.accepted||0);
    a.deduped+=Number(s.deduped||0);
    a.expired+=Number(s.expired||0);
    a.champion_match_operations+=Number(s.champion_match_operations||0);
    if(s.error)a.errors++;
    return a;
  },{sources:0,fetched:0,accepted:0,deduped:0,expired:0,champion_match_operations:0,errors:0});

  return json(200,{
    status:"RESEARCH_COMPLETE",
    request_id:requestId,
    source_limit:limit,
    matching_engine:details?.matching_engine||null,
    rollback_engine:details?.rollback_engine||null,
    role_search_plan:details?.role_search_plan||null,
    totals,
    sources,
    message:`Pesquisa concluída em ${totals.sources} fonte(s): ${totals.fetched} vagas lidas, ${totals.accepted} nova(s) e ${totals.deduped} já conhecidas.`
  });
});
