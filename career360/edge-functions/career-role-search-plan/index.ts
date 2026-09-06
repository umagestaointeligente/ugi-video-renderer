import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const cors={
  "Access-Control-Allow-Origin":"*",
  "Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods":"GET, POST, OPTIONS",
};
const json=(status:number,body:Record<string,unknown>)=>new Response(JSON.stringify(body),{status,headers:{...cors,"Content-Type":"application/json","Cache-Control":"no-store"}});

Deno.serve(async(req)=>{
  if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
  if(!["GET","POST"].includes(req.method))return json(405,{error:"METHOD_NOT_ALLOWED"});
  const auth=req.headers.get("Authorization");if(!auth?.startsWith("Bearer "))return json(401,{error:"AUTH_REQUIRED"});
  const url=Deno.env.get("SUPABASE_URL"),anon=Deno.env.get("SUPABASE_ANON_KEY"),serviceKey=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!url||!anon||!serviceKey)return json(500,{error:"SERVER_CONFIG_ERROR"});
  const userClient=createClient(url,anon,{global:{headers:{Authorization:auth}},auth:{persistSession:false,autoRefreshToken:false}});
  const {data:userData,error:userError}=await userClient.auth.getUser();if(userError||!userData.user)return json(401,{error:"INVALID_SESSION"});
  const service:any=createClient(url,serviceKey,{auth:{persistSession:false,autoRefreshToken:false}});
  let refresh=false;if(req.method==="POST"){try{const body=await req.json();refresh=body?.refresh===true}catch{}}
  const rpc=refresh?"career_refresh_role_search_plan":"career_build_role_search_plan";
  const args=refresh?{p_user_id:userData.user.id}:{p_user_id:userData.user.id,p_persist:true};
  const [{data:plan,error},{data:matchingCtl,error:ctlErr}]=await Promise.all([
    service.rpc(rpc,args),
    service.from("career_engine_control").select("champion_version,rollback_version,status").eq("component","matching").maybeSingle()
  ]);
  if(error)return json(503,{error:"ROLE_SEARCH_PLAN_FAILED"});
  if(ctlErr)return json(503,{error:"MATCHING_CONTROL_READ_FAILED"});
  const titles=Array.isArray(plan?.search_titles)?plan.search_titles:[];
  const tiers=titles.reduce((acc:any,item:any)=>{const key=String(item?.tier||"other");acc[key]=(acc[key]||0)+1;return acc;},{});
  return json(200,{
    status:"ROLE_SEARCH_PLAN_READY",
    plan,
    summary:{
      version:plan?.version||"role-search-v2",
      expansion_mode:plan?.policy?.expansion_mode||plan?.expansion_mode||"balanced",
      titles:titles.length,
      scope_terms:Array.isArray(plan?.scope_terms)?plan.scope_terms.length:0,
      tiers,
      matching_champion:matchingCtl?.status==="active"?matchingCtl?.champion_version:null,
      matching_rollback:matchingCtl?.rollback_version||null,
      role_graph_mode:"production_component"
    }
  });
});
