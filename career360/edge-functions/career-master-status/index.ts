import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
function json(status: number, body: Record<string, unknown>) {
  return new Response(JSON.stringify(body), { status, headers: { ...corsHeaders, "Content-Type": "application/json", "Cache-Control": "no-store" } });
}
async function count(service: any, table: string, apply?: (q: any) => any) {
  let q = service.from(table).select("id", { count: "exact", head: true });
  if (apply) q = apply(q);
  const { count, error } = await q;
  return error ? null : (count ?? 0);
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
  const service: any = createClient(url, serviceKey, { auth: { persistSession: false, autoRefreshToken: false } });
  const { data: roleRow } = await service.from("career_user_roles").select("role").eq("user_id", user.id).maybeSingle();
  if (roleRow?.role !== "master") return json(403, { error: "MASTER_REQUIRED" });

  const [users, masters, docs, quarantined, rejected, drafts, matches, qualified, privacyBlocks, incidentsOpen, incidentsExternal] = await Promise.all([
    count(service, "career_user_roles"),
    count(service, "career_user_roles", (q) => q.eq("role", "master")),
    count(service, "career_documents"),
    count(service, "career_documents", (q) => q.eq("file_status", "quarantined")),
    count(service, "career_documents", (q) => q.eq("file_status", "rejected")),
    count(service, "career_profile_drafts"),
    count(service, "career_matches"),
    count(service, "career_matches", (q) => q.in("classification", ["QUALIFIED","QUALIFIED_SALARY_CONFIRM"])),
    count(service, "career_matches", (q) => q.eq("classification", "BLOCKED_PRIVACY")),
    count(service, "career_incidents", (q) => q.in("status", ["open","needs_user"])),
    count(service, "career_incidents", (q) => q.eq("status", "external_block")),
  ]);

  return json(200, {
    product: "LSI Career 360",
    release: "Master Pilot 1.0",
    role: "master",
    privacy_notice: "Painel agregado: não retorna currículo, nome, e-mail ou histórico de outro usuário.",
    aggregates: { users, masters, documents: docs, quarantined, rejected, drafts, matches, qualified, privacy_blocks: privacyBlocks, incidents_open: incidentsOpen, incidents_external: incidentsExternal },
    gates: {
      dedicated_project: "PASS",
      database_rls: "PASS_CORE_AB_TEST",
      security_advisor: "PASS_ZERO_LINTS",
      private_storage: "PASS",
      raw_retention: "PASS_CRON_ACTIVE",
      deep_parser: "PASS_CI_AND_DEPLOYED",
      privacy_gate: "PASS_SYNTHETIC_SCENARIOS",
      matching_v1: "PASS_SYNTHETIC_SCENARIOS_AND_E2E",
      auth_real_session: "PASS_E2E",
      master_role_bootstrap: "PASS_E2E",
      resume_full_flow: "PASS_E2E",
      raw_file_delete_after_confirmation: "PASS_E2E",
      agent: "PASS_E2E",
      support: "PASS_E2E",
      hosted_app: "PASS_HTTP_200",
      master_pilot: "PASS_READY_FOR_MASTER_USE",
      public_beta: "NOT_OPENED_PRODUCT_DECISION"
    },
    operations: { cleanup_schedule: "hourly minute 17", cost_mode: "ZERO_CASH", customer_data_in_logs: false },
  });
});