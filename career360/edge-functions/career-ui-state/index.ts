import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const cors={
  "Access-Control-Allow-Origin":"*",
  "Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods":"GET, POST, OPTIONS"
};
const json=(status:number,body:Record<string,unknown>)=>new Response(JSON.stringify(body),{status,headers:{...cors,"Content-Type":"application/json","Cache-Control":"no-store"}});

Deno.serve(async(req:Request)=>{
  if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
  if(!["GET","POST"].includes(req.method))return json(405,{error:"METHOD_NOT_ALLOWED"});
  const h=req.headers.get("Authorization");
  if(!h?.startsWith("Bearer "))return json(401,{error:"AUTH_REQUIRED"});
  const url=Deno.env.get("SUPABASE_URL"),anon=Deno.env.get("SUPABASE_ANON_KEY"),serviceKey=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!url||!anon||!serviceKey)return json(500,{error:"SERVER_CONFIG_ERROR"});
  const userClient=createClient(url,anon,{global:{headers:{Authorization:h}},auth:{persistSession:false,autoRefreshToken:false}});
  const {data:u,error:ue}=await userClient.auth.getUser();
  if(ue||!u.user)return json(401,{error:"INVALID_SESSION"});
  const service:any=createClient(url,serviceKey,{auth:{persistSession:false,autoRefreshToken:false}});
  const uid=u.user.id;

  const [profileR,professionalR,mediaR,photoSetR,photoVariantsR,digestPrefR,digestR,notifR,radarRunR,sourceR,engineR]=await Promise.all([
    service.from("career_profiles").select("display_name,current_role_title,city,state_code,onboarding_status,updated_at").eq("user_id",uid).maybeSingle(),
    service.from("career_professional_profile_versions").select("id,version,status,created_at,accepted_at").eq("user_id",uid).order("version",{ascending:false}).limit(1).maybeSingle(),
    service.from("career_profile_media").select("id,updated_at").eq("user_id",uid).eq("media_type","profile_photo").maybeSingle(),
    service.from("career_profile_photo_settings").select("selected_kind,selected_variant_id,preferred_style_key,ai_opt_in,updated_at").eq("user_id",uid).maybeSingle(),
    service.from("career_profile_photo_variants").select("id,status,provider,style_key,created_at,decided_at").eq("user_id",uid).neq("status","rejected").order("created_at",{ascending:false}).limit(8),
    service.from("career_digest_preferences").select("plan_key,cadence_hours,in_app_enabled,email_enabled,critical_immediate,last_digest_at,next_digest_at").eq("user_id",uid).maybeSingle(),
    service.from("career_digest_runs").select("id,status,summary_json,generated_at").eq("user_id",uid).order("generated_at",{ascending:false}).limit(1).maybeSingle(),
    service.from("career_notifications").select("id,kind,status,created_at").eq("user_id",uid).neq("status","dismissed").order("created_at",{ascending:false}).limit(50),
    service.from("career_opportunity_research_runs").select("status,finished_at,fetched_count,accepted_count,deduped_count,expired_count").in("status",["success","partial"]).order("finished_at",{ascending:false}).limit(1).maybeSingle(),
    service.from("career_opportunity_sources").select("id").eq("active",true),
    service.from("career_engine_control").select("champion_engine,rollback_engine,updated_at").eq("id",1).maybeSingle()
  ]);

  const criticalErrors=[profileR,professionalR,mediaR,photoSetR,photoVariantsR,digestPrefR,digestR,notifR,radarRunR,sourceR,engineR].filter((x:any)=>x?.error);
  if(criticalErrors.length)return json(503,{error:"UI_STATE_READ_FAILED"});

  const variants=photoVariantsR.data||[];
  const notifs=notifR.data||[];
  const sourceCount=(sourceR.data||[]).length;
  const selectedKind=photoSetR.data?.selected_kind||"original";
  const hasAcceptedVariant=variants.some((v:any)=>v.status==="accepted");
  const latestDigest=digestR.data||null;
  const radarRun=radarRunR.data||null;

  return json(200,{
    status:"CAREER_UI_READY",
    ui:{
      shell_version:"v15",
      proactive_version:"v12",
      visual_profile_version:"v13",
      photo_studio_version:"v14",
      density_mode:"responsive-fluid",
      scale_breakpoints:[360,412,768,1180]
    },
    capabilities:{
      visual_profile:true,
      proactive_agent:true,
      proactive_digest:true,
      smart_cv:true,
      photo_studio_local:true,
      photo_studio_external_ai:false,
      photo_studio_provider:"local-studio-v1",
      radar_manual_refresh:true,
      mail_decision:true,
      mail_delivery:false
    },
    profile:{
      onboarding_status:profileR.data?.onboarding_status||null,
      has_professional_profile:Boolean(professionalR.data),
      professional_profile_version:professionalR.data?.version||null,
      professional_profile_status:professionalR.data?.status||null,
      has_photo:Boolean(mediaR.data),
      photo_selected_kind:selectedKind,
      has_professional_photo:hasAcceptedVariant,
      preferred_photo_style:photoSetR.data?.preferred_style_key||null
    },
    proactive:{
      cadence_hours:digestPrefR.data?.cadence_hours||null,
      next_digest_at:digestPrefR.data?.next_digest_at||null,
      last_digest_at:digestPrefR.data?.last_digest_at||latestDigest?.generated_at||null,
      unread_count:notifs.filter((x:any)=>x.status==="unread").length,
      critical_unread:notifs.filter((x:any)=>x.status==="unread"&&x.kind==="critical").length,
      action_required_unread:notifs.filter((x:any)=>x.status==="unread"&&x.kind==="action_required").length,
      latest_digest_summary:latestDigest?.summary_json||null
    },
    radar:{
      active_sources:sourceCount,
      last_finished_at:radarRun?.finished_at||null,
      fetched_count:radarRun?.fetched_count||0,
      accepted_count:radarRun?.accepted_count||0,
      deduped_count:radarRun?.deduped_count||0,
      expired_count:radarRun?.expired_count||0,
      champion_engine:engineR.data?.champion_engine||"v2.0",
      rollback_engine:engineR.data?.rollback_engine||"v1.0"
    },
    incomplete:{external_photo_ai:true,mail_delivery:true}
  });
});
