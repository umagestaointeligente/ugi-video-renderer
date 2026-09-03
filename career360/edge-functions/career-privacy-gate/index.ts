import { createClient } from "jsr:@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

function json(status: number, body: Record<string, unknown>) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return json(405, { error: "METHOD_NOT_ALLOWED" });

  const authHeader = req.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) return json(401, { error: "AUTH_REQUIRED" });

  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const anonKey = Deno.env.get("SUPABASE_ANON_KEY");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!supabaseUrl || !anonKey || !serviceKey) return json(500, { error: "SERVER_CONFIG_ERROR" });

  const userClient = createClient(supabaseUrl, anonKey, {
    global: { headers: { Authorization: authHeader } },
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const { data: userData, error: userError } = await userClient.auth.getUser();
  const user = userData.user;
  if (userError || !user) return json(401, { error: "INVALID_SESSION" });

  let payload: { employer_name?: string } = {};
  try { payload = await req.json(); } catch { return json(400, { error: "INVALID_JSON" }); }
  const employerName = payload.employer_name?.trim();
  if (!employerName) return json(400, { error: "EMPLOYER_NAME_REQUIRED" });
  if (employerName.length > 240) return json(400, { error: "EMPLOYER_NAME_TOO_LONG" });

  const serviceClient = createClient(supabaseUrl, serviceKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  });

  const { data, error } = await serviceClient.rpc("career_privacy_gate", {
    p_user_id: user.id,
    p_employer_name: employerName,
  });
  if (error || !data?.length) return json(503, { error: "PRIVACY_GATE_FAILED" });

  const row = data[0];
  return json(200, {
    decision: row.decision,
    reason_code: row.reason_code,
    identity_disclosure_required: row.identity_disclosure_required,
  });
});
