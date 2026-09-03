import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const BUCKET = "career-resumes-quarantine";
const MAX_LIST_ITEMS = 50;
const MAX_TEXT = 180;

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

function clean(value: unknown, max = MAX_TEXT): string | null {
  if (typeof value !== "string") return null;
  const out = value.replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim();
  return out ? out.slice(0, max) : null;
}

function list(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  const seen = new Set<string>();
  const out: string[] = [];
  for (const raw of value.slice(0, MAX_LIST_ITEMS)) {
    const item = clean(raw, 120);
    if (!item) continue;
    const key = item.toLocaleLowerCase("pt-BR");
    if (!seen.has(key)) { seen.add(key); out.push(item); }
  }
  return out;
}

function normalizeEmployer(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR")
    .replace(/[^a-z0-9]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
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

  let payload: any;
  try { payload = await req.json(); } catch { return json(400, { error: "INVALID_JSON" }); }
  const draftId = clean(payload?.draft_id, 80);
  if (!draftId) return json(400, { error: "DRAFT_ID_REQUIRED" });

  const service: any = createClient(supabaseUrl, serviceKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  });

  const { data: draft, error: draftError } = await service
    .from("career_profile_drafts")
    .select("id,user_id,document_id,status")
    .eq("id", draftId)
    .eq("user_id", user.id)
    .maybeSingle();
  if (draftError) return json(503, { error: "DRAFT_LOOKUP_FAILED" });
  if (!draft) return json(404, { error: "DRAFT_NOT_FOUND" });
  if (draft.status === "confirmed") return json(200, { status: "ALREADY_CONFIRMED", draft_id: draft.id });
  if (!['requires_confirmation','partially_confirmed'].includes(draft.status)) {
    return json(409, { error: "DRAFT_STATE_NOT_CONFIRMABLE" });
  }

  const profile = payload?.profile ?? {};
  const prefs = payload?.preferences ?? {};
  const targetRoles = list(prefs.target_roles);
  const preferredLocations = list(prefs.preferred_locations);
  const workModels = list(prefs.work_models).filter((x) => ['remote','hybrid','onsite'].includes(x));
  const preferredSectors = list(prefs.preferred_sectors);
  const skills = list(payload?.skills);
  const autonomy = ['autopilot','one_action','human_first'].includes(prefs.autonomy_level) ? prefs.autonomy_level : 'one_action';
  const salaryFloor = Number.isFinite(Number(prefs.salary_floor_brl)) ? Math.max(0, Number(prefs.salary_floor_brl)) : null;
  const salaryTarget = Number.isFinite(Number(prefs.salary_target_brl)) ? Math.max(0, Number(prefs.salary_target_brl)) : null;

  const displayName = clean(profile.display_name);
  const currentRoleTitle = clean(profile.current_role_title);
  const currentEmployer = clean(profile.current_employer);
  const city = clean(profile.city, 100);
  const stateCodeRaw = clean(profile.state_code, 2);
  const stateCode = stateCodeRaw ? stateCodeRaw.toUpperCase() : null;
  const currentEmploymentConfirmed = Boolean(profile.current_employment_confirmed);
  const protectCurrentEmployer = payload?.protect_current_employer !== false;

  const agentReady = targetRoles.length > 0;
  const onboardingStatus = agentReady ? 'agent_ready' : 'privacy_ready';

  const { error: profileError } = await service.from("career_profiles").upsert({
    user_id: user.id,
    display_name: displayName,
    current_role_title: currentRoleTitle,
    current_employer: currentEmployer,
    current_employment_confirmed: currentEmploymentConfirmed,
    city,
    state_code: stateCode,
    onboarding_status: onboardingStatus,
    updated_at: new Date().toISOString(),
  }, { onConflict: 'user_id' });
  if (profileError) return json(503, { error: "PROFILE_WRITE_FAILED" });

  const { error: prefsError } = await service.from("career_preferences").upsert({
    user_id: user.id,
    target_roles: targetRoles,
    preferred_locations: preferredLocations,
    work_models: workModels,
    salary_floor_brl: salaryFloor,
    salary_target_brl: salaryTarget,
    preferred_sectors: preferredSectors,
    autonomy_level: autonomy,
    updated_at: new Date().toISOString(),
  }, { onConflict: 'user_id' });
  if (prefsError) return json(503, { error: "PREFERENCES_WRITE_FAILED" });

  const now = new Date().toISOString();
  await service.from("career_confirmed_facts")
    .update({ superseded_at: now })
    .eq("user_id", user.id)
    .eq("fact_type", "skill")
    .is("superseded_at", null);

  if (skills.length) {
    const facts = skills.map((name) => ({
      user_id: user.id,
      draft_id: draft.id,
      fact_type: 'skill',
      fact_value: { name },
      source_document_id: draft.document_id,
      confirmation_method: 'explicit_ui',
    }));
    const { error: factsError } = await service.from("career_confirmed_facts").insert(facts);
    if (factsError) return json(503, { error: "CONFIRMED_FACTS_WRITE_FAILED" });
  }

  const blocks = Array.isArray(payload?.employer_blocks) ? payload.employer_blocks.slice(0, 50) : [];
  const normalizedBlocks: any[] = [];
  if (protectCurrentEmployer && currentEmploymentConfirmed && currentEmployer) {
    normalizedBlocks.push({
      employer_name: currentEmployer,
      block_reason: 'current_employer',
      source: 'user_confirmed',
      user_confirmed: true,
    });
  }
  for (const raw of blocks) {
    const employerName = clean(raw?.employer_name);
    if (!employerName) continue;
    const reason = ['current_employer','former_employer','user_requested','group_related','other'].includes(raw?.block_reason)
      ? raw.block_reason : 'user_requested';
    normalizedBlocks.push({ employer_name: employerName, block_reason: reason, source: 'user_confirmed', user_confirmed: true });
  }
  for (const block of normalizedBlocks) {
    await service.from("career_employer_blocks").upsert({
      user_id: user.id,
      employer_name: block.employer_name,
      normalized_name: normalizeEmployer(block.employer_name),
      block_reason: block.block_reason,
      source: block.source,
      user_confirmed: true,
      active: true,
    }, { onConflict: 'user_id,employer_name' });
  }

  const { error: confirmError } = await service.from("career_profile_drafts")
    .update({ status: 'confirmed', confirmed_at: now })
    .eq("id", draft.id)
    .eq("user_id", user.id);
  if (confirmError) return json(503, { error: "DRAFT_CONFIRM_FAILED" });

  let rawDeleted = false;
  if (draft.document_id) {
    const { data: doc } = await service.from("career_documents")
      .select("id,storage_object_path")
      .eq("id", draft.document_id)
      .eq("user_id", user.id)
      .maybeSingle();
    if (doc?.storage_object_path) {
      const { error: removeError } = await service.storage.from(BUCKET).remove([doc.storage_object_path]);
      if (!removeError) {
        rawDeleted = true;
        await service.from("career_documents").update({
          storage_object_path: null,
          raw_file_retention_until: now,
        }).eq("id", doc.id).eq("user_id", user.id);
      }
    }
  }

  await service.from("career_audit_events").insert({
    user_id: user.id,
    event_type: 'profile_confirmation',
    entity_type: 'career_profile_draft',
    entity_id: draft.id,
    outcome: 'confirmed',
    reason_code: agentReady ? 'AGENT_READY' : 'PRIVACY_READY',
    metadata_safe: { raw_deleted: rawDeleted, target_roles_count: targetRoles.length, skills_count: skills.length },
  });

  return json(200, {
    status: agentReady ? 'AGENT_READY' : 'PRIVACY_READY',
    draft_id: draft.id,
    raw_file_deleted: rawDeleted,
    counts: { target_roles: targetRoles.length, skills: skills.length, employer_blocks: normalizedBlocks.length },
  });
});
