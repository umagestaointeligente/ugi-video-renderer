import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const cors={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type","Access-Control-Allow-Methods":"GET, POST, OPTIONS"};
function json(status:number,body:Record<string,unknown>){return new Response(JSON.stringify(body),{status,headers:{...cors,"Content-Type":"application/json","Cache-Control":"no-store"}})}

Deno.serve(async(req)=>{
  if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
  if(!["GET","POST"].includes(req.method))return json(405,{error:"METHOD_NOT_ALLOWED"});
  const h=req.headers.get("Authorization");if(!h?.startsWith("Bearer "))return json(401,{error:"AUTH_REQUIRED"});
  const url=Deno.env.get("SUPABASE_URL"),anon=Deno.env.get("SUPABASE_ANON_KEY"),serviceKey=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!url||!anon||!serviceKey)return json(500,{error:"SERVER_CONFIG_ERROR"});
  const uc=createClient(url,anon,{global:{headers:{Authorization:h}},auth:{persistSession:false,autoRefreshToken:false}});
  const{data:u,error:ue}=await uc.auth.getUser();if(ue||!u.user)return json(401,{error:"INVALID_SESSION"});
  const service:any=createClient(url,serviceKey,{auth:{persistSession:false,autoRefreshToken:false}});

  const [{data:runtime,error:rtErr},{data:sources,error:se},{data:runs,error:re}]=await Promise.all([
    service.rpc("career_radar_runtime_status"),
    service.from("career_opportunity_sources").select("id,last_checked_at,last_success_at,active").eq("active",true),
    service.from("career_opportunity_research_runs").select("status,finished_at,fetched_count,accepted_count,deduped_count,expired_count,metadata_safe").in("status",["success","partial"]).order("finished_at",{ascending:false}).limit(1)
  ]);
  if(rtErr||se||re)return json(503,{error:"RADAR_STATUS_READ_FAILED"});

  const rt=Array.isArray(runtime)?runtime[0]:runtime;
  if(!rt)return json(503,{error:"RADAR_RUNTIME_NOT_FOUND"});
  const active=sources||[];
  const last=(runs||[])[0]||null;
  const sourceCount=active.length;
  const sourceLimit=Number(rt.source_limit)||null;
  const cycleMinutes=Number(rt.cycle_minutes)||null;
  const cyclesForCoverage=sourceLimit?Math.max(1,Math.ceil(sourceCount/sourceLimit)):null;
  const fullCoverageHours=cyclesForCoverage&&cycleMinutes?Number(((cyclesForCoverage*cycleMinutes)/60).toFixed(2)):null;
  let nextEstimatedAt:string|null=null;
  if(last?.finished_at&&cycleMinutes){const d=new Date(last.finished_at);d.setMinutes(d.getMinutes()+cycleMinutes);nextEstimatedAt=d.toISOString()}

  return json(200,{
    status:rt.cron_active?"RADAR_ACTIVE":"RADAR_PAUSED",
    automation:{
      cron_job_id:rt.cron_job_id||null,
      cron_schedule:rt.cron_schedule||null,
      cron_active:Boolean(rt.cron_active),
      cycle_minutes:cycleMinutes,
      sources_per_cycle:sourceLimit,
      active_sources:sourceCount,
      full_coverage_hours:fullCoverageHours,
      next_estimated_at:nextEstimatedAt
    },
    matching:{
      champion_engine:rt.matching_engine||null,
      rollback_engine:rt.rollback_engine||null,
      role_search_plan:rt.role_search_plan||null
    },
    last_run:last?{
      finished_at:last.finished_at,
      fetched_count:last.fetched_count,
      accepted_count:last.accepted_count,
      deduped_count:last.deduped_count,
      expired_count:last.expired_count,
      matching_engine:last.metadata_safe?.matching_engine||null,
      rollback_engine:last.metadata_safe?.rollback_engine||null
    }:null,
    truth_source:"pg_cron+career_engine_control"
  });
});
