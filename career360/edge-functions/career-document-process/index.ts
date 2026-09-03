import { createClient } from "jsr:@supabase/supabase-js@2.114.0";
import { extractAndDraft, MAX_FILE_BYTES, PARSER_VERSION, ParseError, sha256Hex } from "./core.ts";

const BUCKET = "career-resumes-quarantine";
const REJECTED_RETENTION_HOURS = 24;

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

type DocumentRow = {
  id: string;
  user_id: string;
  original_filename_display: string;
  detected_type: "pdf" | "docx";
  size_bytes: number;
  sha256: string;
  storage_object_path: string | null;
  file_status: string;
  deleted_at: string | null;
};

async function markRejected(serviceClient: any, row: DocumentRow, code: string) {
  const retention = new Date(
    Date.now() + REJECTED_RETENTION_HOURS * 60 * 60 * 1000,
  ).toISOString();

  await serviceClient
    .from("career_documents")
    .update({
      file_status: "rejected",
      rejection_code: code,
      raw_file_retention_until: retention,
    })
    .eq("id", row.id)
    .eq("user_id", row.user_id);

  await serviceClient.from("career_audit_events").insert({
    user_id: row.user_id,
    event_type: "resume_parse",
    entity_type: "career_document",
    entity_id: row.id,
    outcome: "rejected",
    reason_code: code,
    metadata_safe: { parser_version: PARSER_VERSION },
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }
  if (req.method !== "POST") {
    return json(405, { error: "METHOD_NOT_ALLOWED" });
  }

  const authHeader = req.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) {
    return json(401, { error: "AUTH_REQUIRED" });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const anonKey = Deno.env.get("SUPABASE_ANON_KEY");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!supabaseUrl || !anonKey || !serviceKey) {
    return json(500, { error: "SERVER_CONFIG_ERROR" });
  }

  const userClient = createClient(supabaseUrl, anonKey, {
    global: { headers: { Authorization: authHeader } },
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const { data: userData, error: userError } = await userClient.auth.getUser();
  const user = userData.user;
  if (userError || !user) {
    return json(401, { error: "INVALID_SESSION" });
  }

  let payload: { document_id?: string } = {};
  try {
    payload = await req.json();
  } catch {
    return json(400, { error: "INVALID_JSON" });
  }
  const documentId = payload.document_id?.trim();
  if (!documentId) {
    return json(400, { error: "DOCUMENT_ID_REQUIRED" });
  }

  const serviceClient: any = createClient(supabaseUrl, serviceKey, {
    auth: { persistSession: false, autoRefreshToken: false },
  });

  const { data: rawRow, error: rowError } = await serviceClient
    .from("career_documents")
    .select(
      "id,user_id,original_filename_display,detected_type,size_bytes,sha256,storage_object_path,file_status,deleted_at",
    )
    .eq("id", documentId)
    .eq("user_id", user.id)
    .maybeSingle();

  if (rowError) {
    return json(503, { error: "DOCUMENT_LOOKUP_FAILED" });
  }
  if (!rawRow) {
    return json(404, { error: "DOCUMENT_NOT_FOUND" });
  }

  const row = rawRow as DocumentRow;
  if (row.deleted_at || row.file_status === "deleted") {
    return json(404, { error: "DOCUMENT_NOT_FOUND" });
  }

  const { data: existingDraft } = await serviceClient
    .from("career_profile_drafts")
    .select("id,status,draft_json,parser_version")
    .eq("document_id", row.id)
    .eq("parser_version", PARSER_VERSION)
    .maybeSingle();

  if (existingDraft) {
    return json(200, {
      document_id: row.id,
      draft_id: existingDraft.id,
      status: "DRAFT_REQUIRES_CONFIRMATION",
      idempotent: true,
      candidate_profile_draft: existingDraft.draft_json,
    });
  }

  if (row.file_status !== "quarantined" && row.file_status !== "safe_for_parse") {
    return json(409, {
      error: "DOCUMENT_STATE_NOT_PROCESSABLE",
      file_status: row.file_status,
    });
  }
  if (!row.storage_object_path) {
    return json(409, { error: "RAW_FILE_NOT_AVAILABLE" });
  }

  const { data: blob, error: downloadError } = await serviceClient.storage
    .from(BUCKET)
    .download(row.storage_object_path);
  if (downloadError || !blob) {
    return json(503, { error: "QUARANTINE_DOWNLOAD_FAILED" });
  }

  const bytes = new Uint8Array(await blob.arrayBuffer());

  try {
    if (
      bytes.length <= 0 ||
      bytes.length > MAX_FILE_BYTES ||
      bytes.length !== Number(row.size_bytes)
    ) {
      throw new ParseError(
        "FILE_SIZE_MISMATCH",
        "O arquivo não corresponde ao metadado de quarentena.",
      );
    }

    const digest = await sha256Hex(bytes);
    if (digest !== row.sha256) {
      throw new ParseError(
        "FILE_HASH_MISMATCH",
        "O arquivo não corresponde ao hash de quarentena.",
      );
    }

    const parsed = await extractAndDraft(bytes, row.detected_type);

    await serviceClient
      .from("career_documents")
      .update({ file_status: "safe_for_parse", rejection_code: null })
      .eq("id", row.id)
      .eq("user_id", user.id);

    const { data: draftRow, error: draftError } = await serviceClient
      .from("career_profile_drafts")
      .insert({
        user_id: user.id,
        document_id: row.id,
        draft_version: 1,
        draft_json: parsed.draft,
        parser_version: PARSER_VERSION,
        status: "requires_confirmation",
      })
      .select("id")
      .single();

    if (draftError || !draftRow) {
      const { data: racedDraft } = await serviceClient
        .from("career_profile_drafts")
        .select("id,draft_json")
        .eq("document_id", row.id)
        .eq("parser_version", PARSER_VERSION)
        .maybeSingle();

      if (racedDraft) {
        return json(200, {
          document_id: row.id,
          draft_id: racedDraft.id,
          status: "DRAFT_REQUIRES_CONFIRMATION",
          idempotent: true,
          candidate_profile_draft: racedDraft.draft_json,
        });
      }
      return json(503, { error: "DRAFT_WRITE_FAILED" });
    }

    await serviceClient
      .from("career_documents")
      .update({ file_status: "parsed", parser_version: PARSER_VERSION })
      .eq("id", row.id)
      .eq("user_id", user.id);

    await serviceClient.from("career_audit_events").insert({
      user_id: user.id,
      event_type: "resume_parse",
      entity_type: "career_document",
      entity_id: row.id,
      outcome: "parsed",
      reason_code: "DRAFT_REQUIRES_CONFIRMATION",
      metadata_safe: {
        parser_version: PARSER_VERSION,
        detected_type: row.detected_type,
      },
    });

    return json(200, {
      document_id: row.id,
      draft_id: draftRow.id,
      status: "DRAFT_REQUIRES_CONFIRMATION",
      idempotent: false,
      candidate_profile_draft: parsed.draft,
    });
  } catch (err) {
    const parseError = err instanceof ParseError
      ? err
      : new ParseError("PARSER_INTERNAL_ERROR", "Falha controlada no parser.");
    await markRejected(serviceClient, row, parseError.code);
    return json(422, { error: parseError.code, message: parseError.message });
  }
});