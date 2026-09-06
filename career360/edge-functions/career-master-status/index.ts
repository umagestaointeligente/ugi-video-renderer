import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const H={
  "Access-Control-Allow-Origin":"*",
  "Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods":"POST, OPTIONS"
};
const out=(status:number,body:unknown)=>new Response(JSON.stringify(body),{status,headers:{...H,"Content-Type":"application/json","Cache-Control":"no-store"}});

Deno.serve(async(req)=>{
  if(req.method==="OPTIONS")return new Response("ok",{headers:H});
  if(req.method!=="POST")return out(405,{error:"METHOD_NOT_ALLOWED"});
  const auth=req.headers.get("Authorization");
  if(!auth?.startsWith("Bearer "))return out(401,{error:"AUTH_REQUIRED"});

  const url=Deno.env.get("SUPABASE_URL");
  const anon=Deno.env.get("SUPABASE_ANON_KEY");
  const serviceKey=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!url||!anon||!serviceKey)return out(500,{error:"SERVER_CONFIG_ERROR"});

  const client=createClient(url,anon,{global:{headers:{Authorization:auth}},auth:{persistSession:false,autoRefreshToken:false}});
  const {data:userData,error:userError}=await client.auth.getUser();
  if(userError||!userData.user)return out(401,{error:"INVALID_SESSION"});

  const {data:metric,error}=await client
    .from("career_master_metrics")
    .select("users,masters,documents,quarantined,rejected,drafts,matches,qualified,privacy_blocks,incidents_open,incidents_external,updated_at")
    .eq("id",1)
    .maybeSingle();

  if(error)return out(503,{error:"MASTER_STATUS_FAILED"});
  if(!metric)return out(403,{error:"MASTER_REQUIRED"});

  const service:any=createClient(url,serviceKey,{auth:{persistSession:false,autoRefreshToken:false}});
  const [matchingR,followupR,mailR]=await Promise.all([
    service.from("career_engine_control").select("champion_version,rollback_version,status,updated_at").eq("component","matching").maybeSingle(),
    service.from("career_engine_control").select("champion_version,status,updated_at").eq("component","followup_scheduler").maybeSingle(),
    service.from("career_engine_control").select("champion_version,status,updated_at,notes_safe").eq("component","mail_delivery").maybeSingle()
  ]);
  if(matchingR.error||followupR.error||mailR.error)return out(503,{error:"MASTER_CONTROL_PLANE_READ_FAILED"});

  const matching=matchingR.data||null;
  const followup=followupR.data||null;
  const mail=mailR.data||null;
  const mailDeliveryActive=mail?.status==="active"&&Boolean(mail?.champion_version)&&mail?.champion_version!=="none";

  return out(200,{
    product:"LSI Career 360",
    release:"Master Pilot 1.0",
    role:"master",
    privacy_notice:"Painel agregado: não retorna currículo, nome, e-mail ou histórico de outro usuário.",
    aggregates:{...metric,matching_engine:matching?.champion_version||null},
    control_plane:{
      matching:{champion:matching?.champion_version||null,rollback:matching?.rollback_version||null,status:matching?.status||null},
      followup_scheduler:{version:followup?.champion_version||null,status:followup?.status||null},
      mail_delivery:{version:mail?.champion_version||null,status:mail?.status||null,active:mailDeliveryActive,reason:mail?.notes_safe?.reason||null}
    },
    gates:{
      dedicated_project:"PASS",
      database_rls:"PASS_READ_ONLY_AUDIT_2026_09_06",
      security_advisor:"KNOWN_WARN_LEAKED_PASSWORD_PROTECTION_PLAN_LIMITATION",
      private_storage:"PASS_PRIVATE_BUCKETS",
      raw_retention:"PASS_CRON_ACTIVE",
      deep_parser:"PARSER_1_0_3_LIVE",
      privacy_gate:"PASS_MASTER_PILOT_SCOPE",
      matching:matching?.status==="active"?`CHAMPION_${matching.champion_version}`:"MATCHING_CONTROL_NOT_ACTIVE",
      matching_rollback:matching?.rollback_version||null,
      auth_real_session:"PASS_E2E",
      master_role_bootstrap:"PASS_E2E",
      resume_full_flow:"PASS_E2E",
      raw_file_delete_after_confirmation:"PASS_E2E",
      agent:"CHAMPION_ALIGNED_V3_LIVE",
      followup_scheduler:followup?.status==="active"?`LIVE_${followup.champion_version}`:"NOT_ACTIVE",
      mail_delivery:mailDeliveryActive?`LIVE_${mail?.champion_version}`:"NOT_LIVE",
      frontend_production:"V14_STABLE_V15_V16_NOT_PROMOTED",
      public_beta:"NOT_OPENED_PRODUCT_DECISION"
    },
    operations:{
      cleanup_schedule:"17 * * * *",
      master_metrics_refresh:"*/5 * * * *",
      metrics_match_scope:"ACTIVE_CHAMPION_ONLY",
      cost_mode:"ZERO_CASH",
      customer_data_in_logs:false
    }
  });
});