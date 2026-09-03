import { createClient } from "jsr:@supabase/supabase-js@2";

const MAX_FILE_BYTES = 10 * 1024 * 1024;
const MAX_REQUEST_BYTES = 12 * 1024 * 1024;
const MAX_ACTIVE_DOCUMENTS = 3;
const RETENTION_DAYS = 7;
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

function safeDisplayName(name: string) {
  return name.replace(/[\u0000-\u001f\u007f]/g, "").slice(0, 180) || "curriculo";
}

function extensionOf(name: string) {
  const match = name.toLowerCase().match(/\.([a-z0-9]+)$/);
  return match?.[1] ?? "";
}

function detectType(bytes: Uint8Array): "pdf" | "docx" | null {
  if (bytes.length >= 5 && bytes[0] === 0x25 && bytes[1] === 0x50 && bytes[2] === 0x44 && bytes[3] === 0x46 && bytes[4] === 0x2d) return "pdf";
  if (bytes.length >= 4 && bytes[0] === 0x50 && bytes[1] === 0x4b && bytes[2] === 0x03 && bytes[3] === 0x04) return "docx";
  return null;
}

function hex(buffer: ArrayBuffer) {
  return [...new Uint8Array(buffer)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (req.method !== "POST") return json(405, { error: "METHOD_NOT_ALLOWED" });

  const contentLength = Number(req.headers.get("content-length") || "0");
  if (Number.isFinite(contentLength) && contentLength > MAX_REQUEST_BYTES) return json(413, { error: "REQUEST_TOO_LARGE" });

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

  const serviceClient = createClient(supabaseUrl, serviceKey, { auth: { persistSession: false, autoRefreshToken: false } });
  const { count, error: countError } = await serviceClient
    .from("career_documents")
    .select("id", { count: "exact", head: true })
    .eq("user_id", user.id)
    .is("deleted_at", null)
    .in("file_status", ["quarantined", "safe_for_parse", "parsed"]);

  if (countError) return json(503, { error: "DOCUMENT_LIMIT_CHECK_FAILED" });
  if ((count ?? 0) >= MAX_ACTIVE_DOCUMENTS) return json(429, { error: "ONBOARDING_FILE_LIMIT_REACHED", limit: MAX_ACTIVE_DOCUMENTS });

  let form: FormData;
  try { form = await req.formData(); } catch { return json(400, { error: "INVALID_MULTIPART" }); }

  const candidate = form.get("file");
  if (!(candidate instanceof File)) return json(400, { error: "FILE_REQUIRED" });
  if (candidate.size <= 0) return json(400, { error: "EMPTY_FILE" });
  if (candidate.size > MAX_FILE_BYTES) return json(413, { error: "FILE_TOO_LARGE", max_bytes: MAX_FILE_BYTES });

  const ext = extensionOf(candidate.name);
  if (ext !== "pdf" && ext !== "docx") return json(415, { error: "EXTENSION_NOT_ALLOWED" });

  const bytes = new Uint8Array(await candidate.arrayBuffer());
  const detectedType = detectType(bytes);
  if (!detectedType) return json(415, { error: "UNSUPPORTED_SIGNATURE" });
  if (detectedType !== ext) return json(415, { error: "EXTENSION_SIGNATURE_MISMATCH" });

  const sha256 = hex(await crypto.subtle.digest("SHA-256", bytes));
  const objectPath = `${user.id}/${crypto.randomUUID()}.${detectedType}`;
  const contentType = detectedType === "pdf" ? "application/pdf" : "application/vnd.openxmlformats-officedocument.wordprocessingml.document";

  const { error: uploadError } = await serviceClient.storage.from(BUCKET).upload(objectPath, bytes, { contentType, upsert: false, cacheControl: "0" });
  if (uploadError) return json(503, { error: "QUARANTINE_UPLOAD_FAILED" });

  const retentionUntil = new Date(Date.now() + RETENTION_DAYS * 24 * 60 * 60 * 1000).toISOString();
  const { data: documentRow, error: insertError } = await serviceClient
    .from("career_documents")
    .insert({
      user_id: user.id,
      original_filename_display: safeDisplayName(candidate.name),
      detected_type: detectedType,
      size_bytes: candidate.size,
      sha256,
      storage_object_path: objectPath,
      file_status: "quarantined",
      raw_file_retention_until: retentionUntil,
    })
    .select("id,file_status,detected_type,size_bytes,raw_file_retention_until")
    .single();

  if (insertError || !documentRow) {
    await serviceClient.storage.from(BUCKET).remove([objectPath]);
    return json(503, { error: "DOCUMENT_METADATA_WRITE_FAILED" });
  }

  return json(201, {
    document_id: documentRow.id,
    status: "QUARANTINED",
    detected_type: documentRow.detected_type,
    size_bytes: documentRow.size_bytes,
    raw_file_retention_until: documentRow.raw_file_retention_until,
  });
});
