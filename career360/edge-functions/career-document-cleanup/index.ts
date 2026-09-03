import { createClient } from "jsr:@supabase/supabase-js@2";

const BUCKET = "career-resumes-quarantine";
const SECRET_NAME = "career_raw_cleanup_cron";
const BATCH_SIZE = 100;

function json(status: number, body: Record<string, unknown>) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return json(405, { error: "METHOD_NOT_ALLOWED" });

  const suppliedSecret = req.headers.get("x-lsi-cron-secret")?.trim();
  if (!suppliedSecret) return json(401, { error: "INTERNAL_AUTH_REQUIRED" });

  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!supabaseUrl || !serviceKey) return json(500, { error: "SERVER_CONFIG_ERROR" });

  const serviceClient = createClient(supabaseUrl, serviceKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  });

  const { data: secretOk, error: secretError } = await serviceClient.rpc(
    "career_validate_internal_secret",
    { p_name: SECRET_NAME, p_candidate: suppliedSecret },
  );
  if (secretError) return json(503, { error: "INTERNAL_AUTH_CHECK_FAILED" });
  if (secretOk !== true) return json(401, { error: "INTERNAL_AUTH_INVALID" });

  const now = new Date().toISOString();
  const { data: rows, error: rowsError } = await serviceClient
    .from("career_documents")
    .select("id,user_id,storage_object_path,file_status")
    .is("deleted_at", null)
    .not("storage_object_path", "is", null)
    .lte("raw_file_retention_until", now)
    .limit(BATCH_SIZE);

  if (rowsError) return json(503, { error: "EXPIRED_DOCUMENT_LOOKUP_FAILED" });
  if (!rows?.length) return json(200, { scanned: 0, deleted: 0, status: "NO_EXPIRED_FILES" });

  const paths = rows.map((r) => r.storage_object_path).filter((p): p is string => Boolean(p));
  const { error: removeError } = await serviceClient.storage.from(BUCKET).remove(paths);
  if (removeError) return json(503, { error: "RAW_FILE_BATCH_DELETE_FAILED", scanned: rows.length });

  const ids = rows.map((r) => r.id);
  const { error: updateError } = await serviceClient
    .from("career_documents")
    .update({
      file_status: "deleted",
      deleted_at: now,
      storage_object_path: null,
      raw_file_retention_until: now,
    })
    .in("id", ids)
    .is("deleted_at", null);

  if (updateError) return json(503, { error: "RAW_FILE_TOMBSTONE_FAILED", scanned: rows.length });

  const auditRows = rows.map((r) => ({
    user_id: r.user_id,
    event_type: "raw_file_cleanup",
    entity_type: "career_document",
    entity_id: r.id,
    outcome: "deleted",
    reason_code: "RETENTION_EXPIRED",
    metadata_safe: { previous_status: r.file_status },
  }));

  const { error: auditError } = await serviceClient.from("career_audit_events").insert(auditRows);
  if (auditError) {
    // Cleanup já ocorreu; não reverter exclusão apenas por falha de auditoria.
    return json(200, {
      scanned: rows.length,
      deleted: rows.length,
      status: "DELETED_AUDIT_DEGRADED",
    });
  }

  return json(200, { scanned: rows.length, deleted: rows.length, status: "DELETED" });
});
