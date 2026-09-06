import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const cors={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type","Access-Control-Allow-Methods":"POST, OPTIONS"};
function json(status:number,body:Record<string,unknown>){return new Response(JSON.stringify(body),{status,headers:{...cors,"Content-Type":"application/json","Cache-Control":"no-store"}})}
function clean(v:unknown,max=1200){if(typeof v!=="string")return"";return v.replace(/[\u0000-\u001f\u007f]/g," ").replace(/\s+/g," ").trim().slice(0,max)}
function norm(v:string){return v.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase()}
const val=(v:any)=>v&&typeof v==="object"&&"value" in v?v.value:v;
const n=(v:any)=>Array.isArray(v)?v.length:0;

Deno.serve(async(req)=>{
  if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
  if(req.method!=="POST")return json(405,{error:"METHOD_NOT_ALLOWED"});
  const h=req.headers.get("Authorization");if(!h?.startsWith("Bearer "))return json(401,{error:"AUTH_REQUIRED"});
  const url=Deno.env.get("SUPABASE_URL"),anon=Deno.env.get("SUPABASE_ANON_KEY"),serviceKey=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!url||!anon||!serviceKey)return json(500,{error:"SERVER_CONFIG_ERROR"});
  const uc=createClient(url,anon,{global:{headers:{Authorization:h}},auth:{persistSession:false,autoRefreshToken:false}});
  const{data:u,error:ue}=await uc.auth.getUser();if(ue||!u.user)return json(401,{error:"INVALID_SESSION"});
  let b:any={};try{b=await req.json()}catch{return json(400,{error:"INVALID_JSON"})}
  const message=clean(b?.message);if(!message)return json(400,{error:"MESSAGE_REQUIRED"});
  const q=norm(message),service:any=createClient(url,serviceKey,{auth:{persistSession:false,autoRefreshToken:false}});

  const{data:ctl,error:ctlErr}=await service.from("career_engine_control").select("champion_version,rollback_version,status").eq("component","matching").maybeSingle();
  if(ctlErr)return json(503,{error:"MATCHING_ENGINE_READ_FAILED"});
  const engine=ctl?.status==="active"&&ctl?.champion_version?String(ctl.champion_version):"v2.0";

  const [profileR,prefsR,roleR,docsR,matchesR,blocksR,incR,draftR,profR]=await Promise.all([
    service.from("career_profiles").select("display_name,current_role_title,current_employer,onboarding_status,city,state_code").eq("user_id",u.user.id).maybeSingle(),
    service.from("career_preferences").select("target_roles,preferred_locations,work_models,salary_floor_brl,preferred_sectors,autonomy_level").eq("user_id",u.user.id).maybeSingle(),
    service.from("career_user_roles").select("role").eq("user_id",u.user.id).maybeSingle(),
    service.from("career_documents").select("id,original_filename_display,file_status,rejection_code,parser_version,created_at,deleted_at").eq("user_id",u.user.id).order("created_at",{ascending:false}).limit(5),
    service.from("career_matches").select("engine_version,score,classification,privacy_decision,salary_state,opportunity_id,career_opportunities(title,employer_name,work_model,city,state_code,status)").eq("user_id",u.user.id).eq("engine_version",engine).order("score",{ascending:false,nullsFirst:false}).limit(500),
    service.from("career_employer_blocks").select("employer_name,block_reason").eq("user_id",u.user.id).eq("active",true).limit(50),
    service.from("career_incidents").select("id,status,category,reason_code,summary_safe,created_at").eq("user_id",u.user.id).neq("status","resolved").order("created_at",{ascending:false}).limit(10),
    service.from("career_profile_drafts").select("id,status,draft_json,parser_version,created_at,confirmed_at").eq("user_id",u.user.id).order("created_at",{ascending:false}).limit(1).maybeSingle(),
    service.from("career_professional_profile_versions").select("version,status,profile_json,created_at").eq("user_id",u.user.id).order("version",{ascending:false}).limit(1).maybeSingle()
  ]);
  if(matchesR.error)return json(503,{error:"CHAMPION_MATCH_READ_FAILED",engine_version:engine});

  const profile=profileR.data,prefs=prefsR.data,role=roleR.data,docs=docsR.data||[],matches=matchesR.data||[],blocks=blocksR.data||[],inc=incR.data||[],draft:any=draftR.data,prof:any=profR.data?.profile_json||null;
  const display=profile?.display_name?.split(/\s+/)[0]||"você";
  const activeMatches=matches.filter((m:any)=>m.career_opportunities?.status==="active"&&m.classification!=="EXPIRED");
  const qualified=activeMatches.filter((m:any)=>["QUALIFIED","QUALIFIED_SALARY_CONFIRM"].includes(m.classification));
  const analyzed=activeMatches.length;
  const discarded=activeMatches.filter((m:any)=>["BELOW_FIT","BLOCKED_REQUIREMENT"].includes(m.classification)).length;
  const pending=inc.filter((i:any)=>i.status==="needs_user");

  let intent="general";
  if(/oportun|vaga|match|aderencia|radar|pesquis/.test(q))intent="opportunities";
  else if(/curriculo|cv|document|experien|formacao|educacao/.test(q))intent="resume";
  else if(/privacidade|empresa|bloque|empregador/.test(q))intent="privacy";
  else if(/precisa.*mim|penden|acao|fazer agora/.test(q))intent="needs_user";
  else if(/status|como esta|resumo/.test(q))intent="status";
  else if(/ajuda|erro|problema|trav|falh/.test(q))intent="support";
  else if(/config|prefer|salario|cargo|local/.test(q))intent="settings";
  else if(/mestre|master|painel/.test(q))intent="master";

  let answer="";const actions:any[]=[];
  if(intent==="opportunities"){
    if(!qualified.length){answer=`${display}, seu radar no motor atual analisou ${analyzed} oportunidade(s) ativa(s) e descartou ${discarded} por baixa aderência ou conflito com suas regras. Nenhuma atingiu o corte de qualificação até agora.`;actions.push({label:"Pesquisar oportunidades agora",action:"run_opportunity_research"})}
    else{const top=qualified.slice(0,3).map((m:any)=>`${m.career_opportunities?.title||"Vaga"} — ${m.career_opportunities?.employer_name||"empresa"} (${Math.round(Number(m.score||0))}% / ${m.classification})`).join("\n");answer=`Encontrei ${qualified.length} oportunidade(s) qualificada(s) entre ${analyzed} ativas analisadas pelo motor atual. As melhores agora:\n${top}`;actions.push({label:"Ver oportunidades",action:"open_opportunities"})}
  }else if(intent==="resume"){
    const d=docs[0],dr=draft?.draft_json||{};const counts={experiencia:n(dr.experience_evidence),formacao:n(dr.education_evidence),competencias:n(dr.skills_evidence),idiomas:n(dr.languages_evidence),certificacoes:n(dr.certifications_evidence)};const meaningful=Object.values(counts).reduce((a:any,x:any)=>a+Number(x>0),0)+(val(dr.summary)?1:0);
    if(!d){answer="Ainda não há currículo enviado. Você pode incluir um PDF textual ou DOCX em Minha Carreira.";actions.push({label:"Enviar currículo",action:"open_resume"})}
    else if(d.file_status==="rejected"){answer=`O último currículo não pôde ser usado (${d.rejection_code||"arquivo não aceito"}). Envie outro PDF textual ou DOCX.`;actions.push({label:"Enviar outro currículo",action:"open_resume"})}
    else if(!meaningful){answer="Recebi seu currículo, mas a extração ainda não estruturou informação suficiente com qualidade. Isso não aparece como currículo entendido; você pode reprocessar e confirmar os dados antes de qualquer uso.";actions.push({label:"Reprocessar currículo",action:"open_resume"})}
    else{const parts=[];if(val(dr.summary))parts.push("resumo profissional");if(counts.experiencia)parts.push(`${counts.experiencia} linha(s) de experiência`);if(counts.formacao)parts.push(`${counts.formacao} de formação`);if(counts.competencias)parts.push(`${counts.competencias} competência(s)`);if(counts.idiomas)parts.push(`${counts.idiomas} idioma(s)`);if(counts.certificacoes)parts.push(`${counts.certificacoes} curso(s)/certificação(ões)`);answer=`Seu currículo foi estruturado em: ${parts.join(", ")}. ${draft?.status==="confirmed"?"Esses dados estão confirmados e podem compor seu Perfil Profissional.":"Esses dados ainda aguardam sua confirmação antes de virarem fatos do perfil."}`;if(prof?.professional_summary)answer+=" Seu Perfil Profissional atual também possui um resumo preparado a partir dos dados confirmados.";actions.push({label:"Revisar dados extraídos",action:"open_career"})}
  }else if(intent==="privacy"){answer=`Sua Proteção de Carreira tem ${blocks.length} empresa(s) bloqueada(s). Uma empresa bloqueada recebe SILENT_BLOCK; empregador não resolvido permanece sem divulgação da sua identidade.`;actions.push({label:"Ver proteção",action:"open_privacy"})}
  else if(intent==="needs_user"){answer=pending.length?`Há ${pending.length} item(ns) aguardando uma ação sua. O mais recente: ${pending[0].summary_safe}`:"Neste momento não encontrei nenhuma pendência marcada como “Preciso de Você”."}
  else if(intent==="settings"){const roles=Array.isArray(prefs?.target_roles)?prefs.target_roles.join(", "):"não definidos";answer=`Seus cargos-alvo são: ${roles||"não definidos"}. Você pode revisar cargos, local, salário e autonomia em Minha Carreira.`}
  else if(intent==="master"){answer=role?.role==="master"?"Seu acesso mestre está ativo. O painel mestre mostra indicadores agregados e saúde do piloto, sem expor currículos de outros usuários.":"Este acesso é de candidato."}
  else if(intent==="status"){answer=`${display}, seu Career está em “${profile?.onboarding_status||"início"}”. O motor ${engine} tem ${analyzed} oportunidade(s) ativa(s) analisada(s), ${qualified.length} qualificada(s), ${blocks.length} proteção(ões) de empresa e ${inc.length} incidente(s) aberto(s).`}
  else if(intent==="support"){answer="Posso verificar currículo, oportunidades, privacidade, configuração e pendências. Se algo falhar, descreva o que ocorreu e eu uso o diagnóstico seguro."}
  else{answer="Posso trabalhar com você em oportunidades, currículo, Proteção de Carreira, configurações e pendências. Pergunte, por exemplo, “quais são minhas melhores oportunidades?” ou “o que precisa de mim?”."}

  await service.from("career_audit_events").insert({user_id:u.user.id,event_type:"agent_request",entity_type:"career_agent",outcome:"resolved",reason_code:intent.toUpperCase(),metadata_safe:{mode:"deterministic_zero_cash_v3",matching_engine:engine}});
  return json(200,{answer,intent,actions,mode:"LSI_ZERO_CASH_V3",matching_engine:engine,rollback_engine:ctl?.rollback_version||null});
});
