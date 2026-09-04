import { createClient } from "jsr:@supabase/supabase-js@2.114.0";
const cors={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type","Access-Control-Allow-Methods":"POST, OPTIONS"};
const ENGINE="v2.0";
function json(status:number,body:Record<string,unknown>){return new Response(JSON.stringify(body),{status,headers:{...cors,"Content-Type":"application/json","Cache-Control":"no-store"}})}
const priority:Record<string,number>={QUALIFIED:0,QUALIFIED_SALARY_CONFIRM:1};
Deno.serve(async(req)=>{
  if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
  if(req.method!=="POST")return json(405,{error:"METHOD_NOT_ALLOWED"});
  const h=req.headers.get("Authorization"); if(!h?.startsWith("Bearer "))return json(401,{error:"AUTH_REQUIRED"});
  const url=Deno.env.get("SUPABASE_URL"),anon=Deno.env.get("SUPABASE_ANON_KEY"),serviceKey=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!url||!anon||!serviceKey)return json(500,{error:"SERVER_CONFIG_ERROR"});
  const uc=createClient(url,anon,{global:{headers:{Authorization:h}},auth:{persistSession:false,autoRefreshToken:false}});
  const {data:u,error:ue}=await uc.auth.getUser(); if(ue||!u.user)return json(401,{error:"INVALID_SESSION"});
  let limit=50; try{const p=await req.json();limit=Math.max(1,Math.min(100,Number(p?.limit)||50))}catch{}
  const service:any=createClient(url,serviceKey,{auth:{persistSession:false,autoRefreshToken:false}});
  const {data:ctl}=await service.from("career_engine_control").select("champion_version").eq("component","matching").maybeSingle(); const engine=ctl?.champion_version||ENGINE;
  const {data:all,error}=await service.from("career_matches").select("id,opportunity_id,engine_version,score,classification,privacy_decision,salary_state,breakdown,explanation_safe,created_at,updated_at,career_opportunities(id,employer_name,title,sector,city,state_code,work_model,salary_min,salary_max,salary_evidence_class,required_skills,source_url,published_at,status)").eq("user_id",u.user.id).eq("engine_version",engine).order("updated_at",{ascending:false}).limit(1000);
  if(error)return json(503,{error:"OPPORTUNITY_FEED_FAILED"});
  const rows=all||[]; const counts:Record<string,number>={}; for(const r of rows)counts[r.classification]=(counts[r.classification]||0)+1;
  const visible=rows.filter((r:any)=>["QUALIFIED","QUALIFIED_SALARY_CONFIRM"].includes(r.classification)&&r.career_opportunities?.status==="active").map((r:any)=>({match_id:r.id,opportunity_id:r.opportunity_id,engine_version:r.engine_version,score:r.score,classification:r.classification,privacy_decision:r.privacy_decision,salary_state:r.salary_state,breakdown:r.breakdown,explanation:r.explanation_safe,opportunity:r.career_opportunities,updated_at:r.updated_at})).sort((a:any,b:any)=>{const pa=priority[a.classification]??99,pb=priority[b.classification]??99;if(pa!==pb)return pa-pb;return Number(b.score??-1)-Number(a.score??-1)}).slice(0,limit);
  const analyzed=rows.filter((r:any)=>r.classification!=="EXPIRED").length; const qualified=visible.length; const discarded=(counts.BELOW_FIT||0)+(counts.BLOCKED_REQUIREMENT||0); const privacyProtected=counts.BLOCKED_PRIVACY||0;
  return json(200,{items:visible,counts,total_visible:qualified,engine_version:engine,work_summary:{analyzed_total:analyzed,qualified_total:qualified,discarded_total:discarded,privacy_protected_total:privacyProtected,pending_data_total:(counts.PENDING_DATA||0)+(counts.PENDING_EVIDENCE||0)},principle:"AGENT_FILTERS_BEFORE_USER_SEES"});
});