import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
function json(status: number, body: Record<string, unknown>) {
  return new Response(JSON.stringify(body), { status, headers: { ...corsHeaders, "Content-Type": "application/json", "Cache-Control": "no-store" } });
}
function clean(value: unknown, max = 500) {
  if (typeof value !== "string") return "";
  return value.replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, max);
}
function norm(v: string) { return v.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR"); }

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return json(405, { error: "METHOD_NOT_ALLOWED" });
  const authHeader = req.headers.get("Authorization"); if (!authHeader?.startsWith("Bearer ")) return json(401, { error: "AUTH_REQUIRED" });
  const url = Deno.env.get("SUPABASE_URL"); const anon = Deno.env.get("SUPABASE_ANON_KEY"); const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !anon || !serviceKey) return json(500, { error: "SERVER_CONFIG_ERROR" });
  const userClient = createClient(url, anon, { global: { headers: { Authorization: authHeader } }, auth: { persistSession: false, autoRefreshToken: false } });
  const { data: userData, error: userError } = await userClient.auth.getUser(); const user = userData.user;
  if (userError || !user) return json(401, { error: "INVALID_SESSION" });
  let p: any; try { p = await req.json(); } catch { return json(400, { error: "INVALID_JSON" }); }
  const description = clean(p?.description); if (!description) return json(400, { error: "DESCRIPTION_REQUIRED" });
  const q = norm(description);
  const service: any = createClient(url, serviceKey, { auth: { persistSession: false, autoRefreshToken: false } });

  let category = "other"; let reason = "NEEDS_DIAGNOSIS"; let status = "needs_user"; let resolution = "Preciso de mais uma ação sua: confira a orientação e tente novamente.";
  if (/curriculo|cv|pdf|docx|arquivo/.test(q)) {
    category = "document";
    const { data: doc } = await service.from("career_documents").select("file_status,rejection_code").eq("user_id", user.id).order("created_at", { ascending: false }).limit(1).maybeSingle();
    if (!doc) { reason = "NO_DOCUMENT"; resolution = "Nenhum currículo foi encontrado. Envie um PDF textual ou DOCX pela área Minha Carreira."; status = "resolved"; }
    else if (doc.file_status === "rejected") { reason = doc.rejection_code || "DOCUMENT_REJECTED"; resolution = "O arquivo foi recusado pela validação de segurança. Envie outro PDF textual ou DOCX. O bruto rejeitado entra no fluxo automático de exclusão."; status = "resolved"; }
    else { reason = `DOCUMENT_${String(doc.file_status).toUpperCase()}`; resolution = `Seu currículo está com status ${doc.file_status}. Se a tela não avançar, saia e entre novamente; o processamento é idempotente e retoma sem duplicar o rascunho.`; status = "resolved"; }
  } else if (/vaga|oportun|match|aderencia/.test(q)) {
    category = "matching"; reason = "MATCHING_GUIDANCE"; resolution = "Confira se ao menos um cargo-alvo está definido. Salário oculto nunca é tratado como incompatível; empresa bloqueada some do radar por privacidade."; status = "resolved";
  } else if (/empresa|privacidade|bloque|empregador/.test(q)) {
    category = "privacy"; reason = "PRIVACY_GUIDANCE"; resolution = "Abra Minha Carreira > Proteção de Carreira. Empresa bloqueada recebe bloqueio silencioso; empresa não resolvida não recebe sua identidade."; status = "resolved";
  } else if (/fora do ar|indispon|terceiro|extern/.test(q)) {
    category = "external"; reason = "EXTERNAL_DEPENDENCY"; resolution = "Identifiquei possível bloqueio externo. Seu estado fica preservado; tente novamente mais tarde. Não vou repetir chamadas caras enquanto o terceiro estiver indisponível."; status = "external_block";
  } else if (/login|senha|entrar|conta/.test(q)) {
    category = "auth"; reason = "AUTH_SESSION_GUIDANCE"; resolution = "Saia e entre novamente. Se o e-mail ainda não estiver confirmado, conclua a verificação enviada pelo provedor de autenticação. Não compartilhe sua senha no chat ou no suporte."; status = "resolved";
  }

  const { data: incident, error: insertError } = await service.from("career_incidents").insert({
    user_id: user.id, category, status, reason_code: reason,
    summary_safe: description.slice(0, 240), resolution_safe: resolution,
    resolved_at: status === "resolved" ? new Date().toISOString() : null,
  }).select("id,correlation_id,status").single();
  if (insertError || !incident) return json(503, { error: "INCIDENT_WRITE_FAILED" });

  await service.from("career_audit_events").insert({ user_id: user.id, event_type: "support_triage", entity_type: "career_incident", entity_id: incident.id, outcome: status, reason_code: reason, metadata_safe: { category } });
  return json(200, { incident_id: incident.id, correlation_id: incident.correlation_id, status, category, resolution });
});
