import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

function json(status: number, body: Record<string, unknown>) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      ...corsHeaders,
      "Content-Type": "application/json",
      "Cache-Control": "no-store",
    },
  });
}

function cleanUuid(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const v = value.trim().toLowerCase();
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(v) ? v : null;
}

function rpcStatus(message: string): number {
  if (message.includes("APPLICATION_NOT_FOUND")) return 404;
  if (
    message.includes("APPLICATION_ALREADY_SUBMITTED") ||
    message.includes("APPLICATION_SUBMISSION_ATTEMPT_ALREADY_STARTED") ||
    message.includes("APPLICATION_STATE_NOT_CONFIRMABLE")
  ) return 409;
  if (message.includes("APPLICATION_CONFIRMATION_REQUIRED_FIELDS_MISSING")) return 400;
  return 503;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return json(405, { error: "METHOD_NOT_ALLOWED" });

  const authHeader = req.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) return json(401, { error: "AUTH_REQUIRED" });

  const url = Deno.env.get("SUPABASE_URL");
  const anon = Deno.env.get("SUPABASE_ANON_KEY");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !anon || !serviceKey) return json(500, { error: "SERVER_CONFIG_ERROR" });

  const userClient = createClient(url, anon, {
    global: { headers: { Authorization: authHeader } },
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const { data: userData, error: userError } = await userClient.auth.getUser();
  const user = userData.user;
  if (userError || !user) return json(401, { error: "INVALID_SESSION" });

  let payload: any;
  try {
    payload = await req.json();
  } catch {
    return json(400, { error: "INVALID_JSON" });
  }

  const applicationId = cleanUuid(payload?.application_id);
  const confirmed = payload?.confirmed;
  if (!applicationId || typeof confirmed !== "boolean") {
    return json(400, { error: "APPLICATION_CONFIRMATION_REQUIRED_FIELDS_MISSING" });
  }

  const service: any = createClient(url, serviceKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  });

  const { data, error } = await service.rpc("career_set_application_submission_confirmation", {
    p_user_id: user.id,
    p_application_id: applicationId,
    p_confirmed: confirmed,
  });

  if (error) {
    const message = String(error.message ?? "APPLICATION_CONFIRMATION_FAILED");
    const known = [
      "APPLICATION_NOT_FOUND",
      "APPLICATION_ALREADY_SUBMITTED",
      "APPLICATION_SUBMISSION_ATTEMPT_ALREADY_STARTED",
      "APPLICATION_STATE_NOT_CONFIRMABLE",
      "APPLICATION_CONFIRMATION_REQUIRED_FIELDS_MISSING",
    ].find((code) => message.includes(code));
    return json(rpcStatus(message), { error: known ?? "APPLICATION_CONFIRMATION_FAILED" });
  }

  const result = Array.isArray(data) ? data[0] : data;
  if (!result) return json(503, { error: "APPLICATION_CONFIRMATION_EMPTY_RESULT" });

  return json(200, {
    status: confirmed ? "APPLICATION_CONFIRMED" : "APPLICATION_CONFIRMATION_REVOKED",
    application_id: result.application_id,
    application_status: result.application_status,
    submission_confirmed: result.submission_confirmed,
    global_submit_permission: result.global_submit_permission,
    dispatch_eligible: result.dispatch_eligible,
    provider_side_effect: false,
  });
});
