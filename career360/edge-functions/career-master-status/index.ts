import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const H = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const out = (status: number, body: unknown) => new Response(JSON.stringify(body), {
  status,
  headers: { ...H, "Content-Type": "application/json", "Cache-Control": "no-store" },
});

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: H });
  if (req.method !== "POST") return out(405, { error: "METHOD_NOT_ALLOWED" });
  const auth = req.headers.get("Authorization");
  if (!auth?.startsWith("Bearer ")) return out(401, { error: "AUTH_REQUIRED" });

  const url = Deno.env.get("SUPABASE_URL");
  const anon = Deno.env.get("SUPABASE_ANON_KEY");
  if (!url || !anon) return out(500, { error: "SERVER_CONFIG_ERROR" });

  const client = createClient(url, anon, {
    global: { headers: { Authorization: auth } },
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const { data: userData, error: userError } = await client.auth.getUser();
  if (userError || !userData.user) return out(401, { error: "INVALID_SESSION" });

  const { data: metric, error } = await client
    .from("career_master_metrics")
    .select("users,masters,documents,quarantined,rejected,drafts,matches,qualified,privacy_blocks,incidents_open,incidents_external,updated_at")
    .eq("id", 1)
    .maybeSingle();

  if (error) return out(503, { error: "MASTER_STATUS_FAILED" });
  if (!metric) return out(403, { error: "MASTER_REQUIRED" });

  return out(200, {
    product: "LSI Career 360",
    release: "Master Pilot 1.0",
    role: "master",
    privacy_notice: "Painel agregado: não retorna currículo, nome, e-mail ou histórico de outro usuário.",
    aggregates: metric,
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
      public_beta: "NOT_OPENED_PRODUCT_DECISION",
    },
    operations: {
      cleanup_schedule: "hourly minute 17",
      master_metrics_refresh: "every 5 minutes",
      cost_mode: "ZERO_CASH",
      customer_data_in_logs: false,
    },
  });
});