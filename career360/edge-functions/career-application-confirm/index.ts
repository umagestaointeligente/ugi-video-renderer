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

  const { data: app, error: appError } = await service
    .from("career_applications")
    .select("id,user_id,status,submission_confirmed_at,submission_dispatch_state,submission_attempt_count,applied_at,external_application_ref_hash")
    .eq("id", applicationId)
    .eq("user_id", user.id)
    .maybeSingle();

  if (appError) return json(503, { error: "APPLICATION_LOOKUP_FAILED" });
  if (!app) return json(404, { error: "APPLICATION_NOT_FOUND" });

  if (app.applied_at || app.external_application_ref_hash || app.status === "applied" || app.submission_dispatch_state === "receipt_confirmed") {
    return json(409, { error: "APPLICATION_ALREADY_SUBMITTED" });
  }

  if (["claimed", "uncertain", "blocked"].includes(app.submission_dispatch_state)) {
    return json(409, { error: "APPLICATION_SUBMISSION_ATTEMPT_ALREADY_STARTED", dispatch_state: app.submission_dispatch_state });
  }

  if ((app.submission_attempt_count ?? 0) > 0) {
    return json(409, { error: "APPLICATION_SUBMISSION_ATTEMPT_ALREADY_RECORDED" });
  }

  if (!["draft_ready", "awaiting_user"].includes(app.status)) {
    return json(409, { error: "APPLICATION_STATE_NOT_CONFIRMABLE", status: app.status });
  }

  const now = new Date().toISOString();
  const nextStatus = confirmed ? "awaiting_user" : "draft_ready";
  const patch = confirmed
    ? { submission_confirmed_at: now, status: nextStatus, updated_at: now }
    : { submission_confirmed_at: null, status: nextStatus, updated_at: now };

  const { error: writeError } = await service
    .from("career_applications")
    .update(patch)
    .eq("id", applicationId)
    .eq("user_id", user.id)
    .eq("submission_dispatch_state", "idle")
    .eq("submission_attempt_count", 0);

  if (writeError) return json(503, { error: "APPLICATION_CONFIRMATION_WRITE_FAILED" });

  const { data: permissions, error: permissionError } = await service
    .from("career_action_permissions")
    .select("allow_application_submit,require_confirmation_for_identity_disclosure")
    .eq("user_id", user.id)
    .maybeSingle();

  if (permissionError) return json(503, { error: "APPLICATION_PERMISSION_READ_FAILED" });
  const allowSubmit = Boolean(permissions?.allow_application_submit);

  await service.from("career_audit_events").insert({
    user_id: user.id,
    event_type: confirmed ? "application_submission_confirmed" : "application_submission_confirmation_revoked",
    entity_type: "career_applications",
    entity_id: applicationId,
    outcome: confirmed ? "confirmed" : "revoked",
    reason_code: confirmed ? "EXPLICIT_PER_APPLICATION_CONFIRMATION" : "EXPLICIT_CONFIRMATION_REVOKED",
    metadata_safe: {
      source: "career-application-confirm",
      dispatch_state: "idle",
      global_submit_permission: allowSubmit,
      provider_side_effect: false,
    },
  });

  return json(200, {
    status: confirmed ? "APPLICATION_CONFIRMED" : "APPLICATION_CONFIRMATION_REVOKED",
    application_id: applicationId,
    application_status: nextStatus,
    submission_confirmed: confirmed,
    global_submit_permission: allowSubmit,
    dispatch_eligible: confirmed && allowSubmit,
    provider_side_effect: false,
  });
});
