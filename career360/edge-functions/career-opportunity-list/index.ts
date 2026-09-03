import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
function json(status: number, body: Record<string, unknown>) {
  return new Response(JSON.stringify(body), { status, headers: { ...corsHeaders, "Content-Type": "application/json", "Cache-Control": "no-store" } });
}

const priority: Record<string, number> = {
  QUALIFIED: 0, QUALIFIED_SALARY_CONFIRM: 1, PENDING_DATA: 2, BELOW_FIT: 3, BLOCKED_REQUIREMENT: 4, EXPIRED: 5,
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return json(405, { error: "METHOD_NOT_ALLOWED" });
  const authHeader = req.headers.get("Authorization"); if (!authHeader?.startsWith("Bearer ")) return json(401, { error: "AUTH_REQUIRED" });
  const url = Deno.env.get("SUPABASE_URL"); const anon = Deno.env.get("SUPABASE_ANON_KEY"); const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !anon || !serviceKey) return json(500, { error: "SERVER_CONFIG_ERROR" });
  const userClient = createClient(url, anon, { global: { headers: { Authorization: authHeader } }, auth: { persistSession: false, autoRefreshToken: false } });
  const { data: userData, error: userError } = await userClient.auth.getUser(); const user = userData.user;
  if (userError || !user) return json(401, { error: "INVALID_SESSION" });
  let limit = 50; try { const p = await req.json(); limit = Math.max(1, Math.min(100, Number(p?.limit) || 50)); } catch { /* optional body */ }

  const service: any = createClient(url, serviceKey, { auth: { persistSession: false, autoRefreshToken: false } });
  const { data: rows, error } = await service.from("career_matches")
    .select("id,opportunity_id,score,classification,privacy_decision,salary_state,breakdown,explanation_safe,created_at,updated_at,career_opportunities(id,employer_name,title,sector,city,state_code,work_model,salary_min,salary_max,salary_evidence_class,required_skills,source_url,published_at,status)")
    .eq("user_id", user.id)
    .neq("classification", "BLOCKED_PRIVACY")
    .limit(limit);
  if (error) return json(503, { error: "OPPORTUNITY_FEED_FAILED" });

  const items = (rows ?? []).map((row: any) => ({
    match_id: row.id,
    opportunity_id: row.opportunity_id,
    score: row.score,
    classification: row.classification,
    privacy_decision: row.privacy_decision,
    salary_state: row.salary_state,
    breakdown: row.breakdown,
    explanation: row.explanation_safe,
    opportunity: row.career_opportunities,
    updated_at: row.updated_at,
  })).sort((a: any, b: any) => {
    const pa = priority[a.classification] ?? 99; const pb = priority[b.classification] ?? 99;
    if (pa !== pb) return pa - pb;
    return Number(b.score ?? -1) - Number(a.score ?? -1);
  });

  const counts: Record<string, number> = {};
  for (const item of items) counts[item.classification] = (counts[item.classification] ?? 0) + 1;
  return json(200, { items, counts, total_visible: items.length });
});
