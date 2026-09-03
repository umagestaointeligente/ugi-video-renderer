import { createClient } from "jsr:@supabase/supabase-js@2";

const BUCKET = "career-resumes-quarantine";
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

  let payload: { document_id?: string } = {};
  try { payload = await req.json(); } catch { return json(400, { error: "INVALID_JSON" }); }
  const documentId = payload.document_id?.trim();
  if (!documentId) return json(400, { error: "DOCUMENT_ID_REQUIRED" });

  const serviceClient = createClient(supabaseUrl, serviceKey, { auth: { persistSession: false, autoRefreshToken: false } });
  const { data: row, error: rowError } = await serviceClient
    .from("career_documents")
    .select("id,user_id,storage_object_path,file_status,deleted_at")
    .eq("id", documentId)
    .eq("user_id", user.id)
    .maybeSingle();

  if (rowError) return json(503, { error: "DOCUMENT_LOOKUP_FAILED" });
  if (!row) return json(404, { error: "DOCUMENT_NOT_FOUND" });
  if (row.file_status === "deleted" || row.deleted_at) return json(200, { document_id: row.id, status: "DELETED", idempotent: true });

  if (row.storage_object_path) {
    const { error: removeError } = await serviceClient.storage.from(BUCKET).remove([row.storage_object_path]);
    if (removeError) return json(503, { error: "RAW_FILE_DELETE_FAILED" });
  }

  const now = new Date().toISOString();
  const { error: updateError } = await serviceClient
    .from("career_documents")
    .update({
      file_status: "deleted",
      deleted_at: now,
      storage_object_path: null,
      raw_file_retention_until: now,
    })
    .eq("id", row.id)
    .eq("user_id", user.id);

  if (updateError) return json(503, { error: "DELETE_TOMBSTONE_FAILED" });
  return json(200, { document_id: row.id, status: "DELETED", idempotent: false });
});
