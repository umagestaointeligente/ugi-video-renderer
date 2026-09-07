import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const cors={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type","Access-Control-Allow-Methods":"POST, OPTIONS"};
function json(status:number,body:Record<string,unknown>){return new Response(JSON.stringify(body),{status,headers:{...cors,"Content-Type":"application/json","Cache-Control":"no-store"}})}

Deno.serve(async(req)=>{
  if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
  if(req.method!=="POST")return json(405,{error:"METHOD_NOT_ALLOWED"});

  const h=req.headers.get("Authorization");
  if(!h?.startsWith("Bearer "))return json(401,{error:"AUTH_REQUIRED"});

  const url=Deno.env.get("SUPABASE_URL"),anon=Deno.env.get("SUPABASE_ANON_KEY"),serviceKey=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!url||!anon||!serviceKey)return json(500,{error:"SERVER_CONFIG_ERROR"});

  const uc=createClient(url,anon,{global:{headers:{Authorization:h}},auth:{persistSession:false,autoRefreshToken:false}});
  const{data:u,error:ue}=await uc.auth.getUser();
  if(ue||!u.user)return json(401,{error:"INVALID_SESSION"});

  const service:any=createClient(url,serviceKey,{auth:{persistSession:false,autoRefreshToken:false}});
  let body:any={};
  try{body=await req.json()}catch{}

  if(body?.action==="mark_read"&&body?.notification_id){
    const{error}=await service.from("career_notifications").update({status:"read",read_at:new Date().toISOString()}).eq("id",String(body.notification_id)).eq("user_id",u.user.id);
    if(error)return json(503,{error:"MARK_READ_FAILED"});
  }

  const uid=u.user.id;
  const[prefR,digestR,notifR,appsR,mailR,permR]=await Promise.all([
    service.from("career_digest_preferences").select("plan_key,cadence_hours,timezone,in_app_enabled,email_enabled,critical_immediate,last_digest_at,next_digest_at").eq("user_id",uid).maybeSingle(),
    service.from("career_digest_runs").select("id,window_start,window_end,cadence_hours,status,summary_json,generated_at,delivered_at").eq("user_id",uid).order("generated_at",{ascending:false}).limit(1).maybeSingle(),
    service.from("career_notifications").select("id,kind,title,body,action_type,action_payload_safe,status,created_at,read_at").eq("user_id",uid).neq("status","dismissed").order("created_at",{ascending:false}).limit(20),
    service.from("career_applications").select("id,opportunity_id,status,submission_confirmed_at,submission_dispatch_state,submission_attempt_count,last_activity_at,career_opportunities(title,employer_name,source_name)").eq("user_id",uid).order("last_activity_at",{ascending:false}).limit(200),
    service.from("career_mail_actions").select("id,direction,message_kind,sender_display,subject_safe,summary_safe,proposed_reply,status,critical,requires_human,sensitive_category,received_at,created_at").eq("user_id",uid).in("status",["detected","draft_ready","awaiting_approval","approved"]).order("created_at",{ascending:false}).limit(20),
    service.from("career_action_permissions").select("allow_application_submit,require_confirmation_for_identity_disclosure").eq("user_id",uid).maybeSingle()
  ]);

  if(prefR.error||digestR.error||notifR.error||appsR.error||mailR.error||permR.error)return json(503,{error:"PROACTIVE_STATUS_READ_FAILED"});

  const apps=appsR.data||[],counts:any={};
  for(const a of apps)counts[a.status]=(counts[a.status]||0)+1;
  const allowSubmit=Boolean(permR.data?.allow_application_submit);
  const confirmable=apps
    .filter((a:any)=>["draft_ready","awaiting_user"].includes(a.status)&&a.submission_dispatch_state==="idle"&&Number(a.submission_attempt_count||0)===0)
    .slice(0,20)
    .map((a:any)=>({
      id:a.id,
      status:a.status,
      submission_confirmed:Boolean(a.submission_confirmed_at),
      submission_dispatch_state:a.submission_dispatch_state,
      title:a.career_opportunities?.title||"Oportunidade",
      employer_name:a.career_opportunities?.employer_name||null,
      source_name:a.career_opportunities?.source_name||null,
      global_submit_permission:allowSubmit,
      dispatch_eligible:Boolean(a.submission_confirmed_at)&&allowSubmit
    }));

  const notifs=notifR.data||[];
  return json(200,{
    status:"PROACTIVE_AGENT_READY",
    preference:prefR.data||null,
    latest_digest:digestR.data||null,
    notifications:notifs,
    unread_count:notifs.filter((x:any)=>x.status==="unread").length,
    application_counts:counts,
    confirmable_applications:confirmable,
    application_permissions:{
      allow_application_submit:allowSubmit,
      require_confirmation_for_identity_disclosure:Boolean(permR.data?.require_confirmation_for_identity_disclosure)
    },
    pending_mail_actions:mailR.data||[],
    critical_count:notifs.filter((x:any)=>x.kind==="critical"&&x.status==="unread").length,
    action_required_count:notifs.filter((x:any)=>x.kind==="action_required"&&x.status==="unread").length
  });
});
