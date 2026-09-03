import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
function json(status: number, body: Record<string, unknown>) {
  return new Response(JSON.stringify(body), { status, headers: { ...corsHeaders, "Content-Type": "application/json", "Cache-Control": "no-store" } });
}
function clean(value: unknown, max = 1200) {
  if (typeof value !== "string") return "";
  return value.replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, max);
}
function norm(value: string) {
  return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR");
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return json(405, { error: "METHOD_NOT_ALLOWED" });
  const authHeader = req.headers.get("Authorization"); if (!authHeader?.startsWith("Bearer ")) return json(401, { error: "AUTH_REQUIRED" });
  const url = Deno.env.get("SUPABASE_URL"); const anon = Deno.env.get("SUPABASE_ANON_KEY"); const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !anon || !serviceKey) return json(500, { error: "SERVER_CONFIG_ERROR" });
  const userClient = createClient(url, anon, { global: { headers: { Authorization: authHeader } }, auth: { persistSession: false, autoRefreshToken: false } });
  const { data: userData, error: userError } = await userClient.auth.getUser(); const user = userData.user;
  if (userError || !user) return json(401, { error: "INVALID_SESSION" });
  let body: any; try { body = await req.json(); } catch { return json(400, { error: "INVALID_JSON" }); }
  const message = clean(body?.message); if (!message) return json(400, { error: "MESSAGE_REQUIRED" });
  const q = norm(message);
  const service: any = createClient(url, serviceKey, { auth: { persistSession: false, autoRefreshToken: false } });

  const [{ data: profile }, { data: prefs }, { data: role }, { data: docs }, { data: matches }, { data: blocks }, { data: incidents }] = await Promise.all([
    service.from("career_profiles").select("display_name,current_role_title,current_employer,onboarding_status,city,state_code").eq("user_id", user.id).maybeSingle(),
    service.from("career_preferences").select("target_roles,preferred_locations,work_models,salary_floor_brl,preferred_sectors,autonomy_level").eq("user_id", user.id).maybeSingle(),
    service.from("career_user_roles").select("role").eq("user_id", user.id).maybeSingle(),
    service.from("career_documents").select("id,file_status,rejection_code,created_at").eq("user_id", user.id).order("created_at", { ascending: false }).limit(5),
    service.from("career_matches").select("score,classification,privacy_decision,salary_state,opportunity_id,career_opportunities(title,employer_name,work_model,city,state_code)").eq("user_id", user.id).neq("classification", "BLOCKED_PRIVACY").order("score", { ascending: false, nullsFirst: false }).limit(10),
    service.from("career_employer_blocks").select("employer_name,block_reason").eq("user_id", user.id).eq("active", true).limit(50),
    service.from("career_incidents").select("id,status,category,reason_code,summary_safe,created_at").eq("user_id", user.id).neq("status", "resolved").order("created_at", { ascending: false }).limit(10),
  ]);

  const display = profile?.display_name?.split(/\s+/)[0] || "você";
  const visibleMatches = matches ?? [];
  const qualified = visibleMatches.filter((m: any) => ["QUALIFIED","QUALIFIED_SALARY_CONFIRM"].includes(m.classification));
  const pendingUser = (incidents ?? []).filter((i: any) => i.status === "needs_user");
  const lastDoc = (docs ?? [])[0];
  let intent = "general";
  if (/oportun|vaga|match|aderencia/.test(q)) intent = "opportunities";
  else if (/curriculo|cv|document/.test(q)) intent = "resume";
  else if (/privacidade|empresa|bloque|empregador/.test(q)) intent = "privacy";
  else if (/precisa.*mim|penden|acao|fazer agora/.test(q)) intent = "needs_user";
  else if (/status|como esta|resumo/.test(q)) intent = "status";
  else if (/ajuda|erro|problema|trav|falh/.test(q)) intent = "support";
  else if (/config|prefer|salario|cargo|local/.test(q)) intent = "settings";
  else if (/mestre|master|painel/.test(q)) intent = "master";

  let answer = ""; const actions: Array<Record<string,string>> = [];
  if (intent === "opportunities") {
    if (!visibleMatches.length) {
      answer = `${display}, ainda não há oportunidades avaliadas no seu radar. Você pode adicionar uma oportunidade para eu analisar agora.`;
      actions.push({ label: "Adicionar oportunidade", action: "open_opportunity_add" });
    } else {
      const top = visibleMatches.slice(0, 3).map((m: any) => `${m.career_opportunities?.title ?? "Vaga"} — ${m.career_opportunities?.employer_name ?? "empresa"} (${m.score ?? "—"}% / ${m.classification})`).join("\n");
      answer = `Encontrei ${visibleMatches.length} oportunidade(s) visível(is) e ${qualified.length} qualificada(s). As melhores agora:\n${top}`;
      actions.push({ label: "Ver oportunidades", action: "open_opportunities" });
    }
  } else if (intent === "resume") {
    if (!lastDoc) {
      answer = "Ainda não há currículo processado. Envie um PDF textual ou DOCX; eu vou extrair um rascunho e você confirma antes de qualquer dado virar fato.";
      actions.push({ label: "Enviar currículo", action: "open_resume" });
    } else if (lastDoc.file_status === "rejected") {
      answer = `O último currículo foi rejeitado com segurança (${lastDoc.rejection_code ?? "arquivo não aceito"}). O arquivo bruto entra no fluxo de exclusão e você pode enviar outro PDF/DOCX.`;
      actions.push({ label: "Enviar outro currículo", action: "open_resume" });
    } else {
      answer = `Seu último currículo está com status ${lastDoc.file_status}. Dados extraídos só são usados depois da sua confirmação.`;
      actions.push({ label: "Revisar minha carreira", action: "open_career" });
    }
  } else if (intent === "privacy") {
    answer = `Sua Proteção de Carreira tem ${(blocks ?? []).length} empresa(s) bloqueada(s). Uma empresa bloqueada recebe SILENT_BLOCK; empregador não resolvido permanece NO_DISCLOSURE.`;
    actions.push({ label: "Ver proteção", action: "open_privacy" });
  } else if (intent === "needs_user") {
    answer = pendingUser.length ? `Há ${pendingUser.length} item(ns) aguardando uma ação sua. O mais recente: ${pendingUser[0].summary_safe}` : "Neste momento não encontrei nenhuma pendência marcada como “Preciso de Você”.";
    actions.push({ label: "Ver jornada", action: "open_journey" });
  } else if (intent === "support") {
    answer = "Posso verificar currículo, oportunidades, privacidade, configuração e pendências. Se o problema não for resolvido pelo diagnóstico automático, eu registro um incidente seguro sem colocar seu currículo ou dados sensíveis no log.";
    actions.push({ label: "Resolver um problema", action: "open_support" });
  } else if (intent === "settings") {
    const roles = Array.isArray(prefs?.target_roles) ? prefs.target_roles.join(", ") : "não definidos";
    answer = `Hoje seus cargos-alvo são: ${roles || "não definidos"}. Modelo de autonomia: ${prefs?.autonomy_level ?? "1 ação sua"}. Você pode ajustar isso em Minha Carreira.`;
    actions.push({ label: "Abrir configurações", action: "open_career" });
  } else if (intent === "master") {
    answer = role?.role === "master" ? "Seu acesso mestre está ativo. O painel mostra apenas indicadores agregados e saúde do piloto — nunca expõe currículos ou dados pessoais de outros usuários." : "Este acesso é de candidato. O painel mestre não está disponível para esta conta.";
    if (role?.role === "master") actions.push({ label: "Painel mestre", action: "open_master" });
  } else if (intent === "status") {
    answer = `${display}, seu Career está em “${profile?.onboarding_status ?? "início"}”. Tenho ${visibleMatches.length} oportunidade(s) visível(is), ${qualified.length} qualificada(s), ${(blocks ?? []).length} proteção(ões) de empresa e ${(incidents ?? []).length} incidente(s) aberto(s).`;
    actions.push({ label: "Ver início", action: "open_home" });
  } else {
    answer = `Posso trabalhar com você em oportunidades, currículo, Proteção de Carreira, configurações e pendências. Para começar, diga por exemplo “quais são minhas melhores oportunidades?” ou “o que precisa de mim?”.`;
    actions.push({ label: "Ver oportunidades", action: "open_opportunities" }, { label: "Minha carreira", action: "open_career" });
  }

  await service.from("career_audit_events").insert({ user_id: user.id, event_type: "agent_request", entity_type: "career_agent", outcome: "resolved", reason_code: intent.toUpperCase(), metadata_safe: { mode: "deterministic_zero_cash_v1" } });
  return json(200, { answer, intent, actions, mode: "LSI_ZERO_CASH_V1" });
});
