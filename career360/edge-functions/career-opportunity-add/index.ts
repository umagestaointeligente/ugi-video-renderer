import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const MAX_TEXT = 6000;

function json(status: number, body: Record<string, unknown>) {
  return new Response(JSON.stringify(body), { status, headers: { ...corsHeaders, "Content-Type": "application/json", "Cache-Control": "no-store" } });
}
function clean(value: unknown, max = 180): string | null {
  if (typeof value !== "string") return null;
  const out = value.replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim();
  return out ? out.slice(0, max) : null;
}
function list(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  const seen = new Set<string>(); const out: string[] = [];
  for (const raw of value.slice(0, 60)) {
    const item = clean(raw, 120); if (!item) continue;
    const key = item.toLocaleLowerCase("pt-BR"); if (!seen.has(key)) { seen.add(key); out.push(item); }
  }
  return out;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return json(405, { error: "METHOD_NOT_ALLOWED" });
  const authHeader = req.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) return json(401, { error: "AUTH_REQUIRED" });

  const url = Deno.env.get("SUPABASE_URL"); const anon = Deno.env.get("SUPABASE_ANON_KEY"); const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !anon || !serviceKey) return json(500, { error: "SERVER_CONFIG_ERROR" });
  const userClient = createClient(url, anon, { global: { headers: { Authorization: authHeader } }, auth: { persistSession: false, autoRefreshToken: false } });
  const { data: userData, error: userError } = await userClient.auth.getUser();
  const user = userData.user; if (userError || !user) return json(401, { error: "INVALID_SESSION" });

  let p: any; try { p = await req.json(); } catch { return json(400, { error: "INVALID_JSON" }); }
  const employer = clean(p?.employer_name, 180); const title = clean(p?.title, 180);
  if (!employer || !title) return json(400, { error: "EMPLOYER_AND_TITLE_REQUIRED" });
  const description = clean(p?.description_text, MAX_TEXT);
  const sector = clean(p?.sector, 120); const city = clean(p?.city, 100); const stateRaw = clean(p?.state_code, 2); const stateCode = stateRaw?.toUpperCase() ?? null;
  const workModel = ["remote","hybrid","onsite","unknown"].includes(p?.work_model) ? p.work_model : "unknown";
  const evidenceClass = ["explicit","estimated","hidden","unknown"].includes(p?.salary_evidence_class) ? p.salary_evidence_class : "unknown";
  const salaryMin = Number.isFinite(Number(p?.salary_min)) ? Math.max(0, Number(p.salary_min)) : null;
  const salaryMax = Number.isFinite(Number(p?.salary_max)) ? Math.max(0, Number(p.salary_max)) : null;
  const requiredSkills = list(p?.required_skills); const preferredSkills = list(p?.preferred_skills);
  const sourceUrl = clean(p?.source_url, 1200);

  const service: any = createClient(url, serviceKey, { auth: { persistSession: false, autoRefreshToken: false } });
  const { data: roleRow } = await service.from("career_user_roles").select("role").eq("user_id", user.id).maybeSingle();
  const sourceName = roleRow?.role === "master" ? "master_manual" : "user_manual";
  const { data: opp, error: insertError } = await service.from("career_opportunities").insert({
    source_name: sourceName,
    source_url: sourceUrl,
    employer_name: employer,
    title,
    description_text: description,
    sector,
    city,
    state_code: stateCode,
    work_model: workModel,
    salary_min: salaryMin,
    salary_max: salaryMax,
    salary_currency: "BRL",
    salary_evidence_class: evidenceClass,
    required_skills: requiredSkills,
    preferred_skills: preferredSkills,
    evidence_safe: { entered_by_user: true, source_url_present: Boolean(sourceUrl) },
    status: "active",
  }).select("id").single();
  if (insertError || !opp) return json(503, { error: "OPPORTUNITY_WRITE_FAILED" });

  const { data: scoreRows, error: scoreError } = await service.rpc("career_score_opportunity", { p_user_id: user.id, p_opportunity_id: opp.id, p_persist: true });
  if (scoreError) return json(503, { error: "MATCH_SCORE_FAILED", opportunity_id: opp.id });
  const match = Array.isArray(scoreRows) ? scoreRows[0] : scoreRows;

  await service.from("career_audit_events").insert({
    user_id: user.id, event_type: "opportunity_manual_add", entity_type: "career_opportunity", entity_id: opp.id,
    outcome: match?.classification ?? "created", reason_code: "USER_SUPPLIED_OPPORTUNITY",
    metadata_safe: { work_model: workModel, salary_evidence_class: evidenceClass, required_skills_count: requiredSkills.length },
  });

  return json(201, { opportunity_id: opp.id, match: match ?? null, privacy_hidden: match?.classification === "BLOCKED_PRIVACY" });
});
