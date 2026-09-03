import { createClient } from "jsr:@supabase/supabase-js@2";
import JSZip from "npm:jszip@3.10.1";
import { extractText, getDocumentProxy } from "npm:unpdf@1.8.1";

const BUCKET = "career-resumes-quarantine";
const PARSER_VERSION = "career360-edge-parser/1.0.0";
const MAX_FILE_BYTES = 10 * 1024 * 1024;
const MAX_DOCX_ENTRIES = 500;
const MAX_DOCX_UNCOMPRESSED_BYTES = 40 * 1024 * 1024;
const MAX_DOCX_COMPRESSION_RATIO = 120;
const MAX_TEXT_CHARS = 250_000;
const MAX_PDF_PAGES = 30;
const MAX_PDF_IMAGE_SIZE = 16_777_216;
const PDF_TIMEOUT_MS = 12_000;
const REJECTED_RETENTION_HOURS = 24;

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

class ParseError extends Error {
  code: string;
  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

function json(status: number, body: Record<string, unknown>) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json", "Cache-Control": "no-store" },
  });
}

function normalizeSpaces(value: string) {
  return value.replace(/\u00a0/g, " ").replace(/[\t\r ]+/g, " ").replace(/\n{3,}/g, "\n\n").trim();
}

function cleanLine(value: string) {
  return value.replace(/\s+/g, " ").replace(/^[ \t•·▪◦\-–—|]+|[ \t•·▪◦\-–—|]+$/g, "").trim();
}

function safeExcerpt(text: string, value: string, radius = 80) {
  if (!value) return null;
  const idx = text.toLocaleLowerCase("pt-BR").indexOf(value.toLocaleLowerCase("pt-BR"));
  if (idx < 0) return null;
  return normalizeSpaces(text.slice(Math.max(0, idx - radius), Math.min(text.length, idx + value.length + radius)));
}

function hex(buffer: ArrayBuffer) {
  return [...new Uint8Array(buffer)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function sha256(bytes: Uint8Array) {
  return hex(await crypto.subtle.digest("SHA-256", bytes));
}

function u16(data: Uint8Array, offset: number) {
  return data[offset] | (data[offset + 1] << 8);
}

function u32(data: Uint8Array, offset: number) {
  return (data[offset] | (data[offset + 1] << 8) | (data[offset + 2] << 16) | (data[offset + 3] << 24)) >>> 0;
}

function findEndOfCentralDirectory(data: Uint8Array) {
  const min = Math.max(0, data.length - 65_557);
  for (let i = data.length - 22; i >= min; i--) {
    if (u32(data, i) === 0x06054b50) return i;
  }
  return -1;
}

function validateDocxCentralDirectory(data: Uint8Array) {
  const eocd = findEndOfCentralDirectory(data);
  if (eocd < 0) throw new ParseError("DOCX_CORRUPT", "O DOCX não possui diretório ZIP válido.");

  const totalEntries = u16(data, eocd + 10);
  const centralSize = u32(data, eocd + 12);
  const centralOffset = u32(data, eocd + 16);
  if (totalEntries <= 0 || totalEntries > MAX_DOCX_ENTRIES) {
    throw new ParseError("DOCX_TOO_COMPLEX", "O DOCX contém arquivos internos demais.");
  }
  if (centralOffset + centralSize > data.length) throw new ParseError("DOCX_CORRUPT", "Diretório ZIP fora dos limites do arquivo.");

  const decoder = new TextDecoder("utf-8", { fatal: false });
  let cursor = centralOffset;
  let expandedTotal = 0;
  const names = new Set<string>();

  for (let entry = 0; entry < totalEntries; entry++) {
    if (cursor + 46 > data.length || u32(data, cursor) !== 0x02014b50) {
      throw new ParseError("DOCX_CORRUPT", "Entrada ZIP inválida.");
    }
    const compressedSize = u32(data, cursor + 20);
    const uncompressedSize = u32(data, cursor + 24);
    const nameLength = u16(data, cursor + 28);
    const extraLength = u16(data, cursor + 30);
    const commentLength = u16(data, cursor + 32);
    const nameStart = cursor + 46;
    const nameEnd = nameStart + nameLength;
    if (nameEnd > data.length) throw new ParseError("DOCX_CORRUPT", "Nome de entrada ZIP inválido.");

    const name = decoder.decode(data.slice(nameStart, nameEnd)).replace(/\\/g, "/");
    if (!name || name.startsWith("/") || name === ".." || name.includes("../")) {
      throw new ParseError("DOCX_PATH_TRAVERSAL", "O DOCX contém caminho interno inválido.");
    }
    names.add(name);
    expandedTotal += uncompressedSize;
    if (expandedTotal > MAX_DOCX_UNCOMPRESSED_BYTES) {
      throw new ParseError("DOCX_EXPANDED_TOO_LARGE", "O DOCX expandido excede o limite de segurança.");
    }
    if (uncompressedSize > 1_000_000) {
      if (compressedSize === 0) throw new ParseError("DOCX_SUSPICIOUS_COMPRESSION", "Compressão suspeita no DOCX.");
      const ratio = uncompressedSize / Math.max(1, compressedSize);
      if (ratio > MAX_DOCX_COMPRESSION_RATIO) {
        throw new ParseError("DOCX_SUSPICIOUS_COMPRESSION", "Taxa de compressão suspeita no DOCX.");
      }
    }
    cursor = nameEnd + extraLength + commentLength;
  }

  if (!names.has("[Content_Types].xml") || !names.has("word/document.xml")) {
    throw new ParseError("DOCX_NOT_WORD_DOCUMENT", "O arquivo ZIP não é um documento Word válido.");
  }
}

async function extractDocxText(bytes: Uint8Array) {
  validateDocxCentralDirectory(bytes);
  let zip: JSZip;
  try {
    zip = await JSZip.loadAsync(bytes, { checkCRC32: true, createFolders: false });
  } catch {
    throw new ParseError("DOCX_CORRUPT", "O DOCX está corrompido.");
  }
  const documentXml = zip.file("word/document.xml");
  if (!documentXml) throw new ParseError("DOCX_MISSING_DOCUMENT_XML", "O DOCX não contém o documento principal.");
  const xml = await documentXml.async("string");
  const upper = xml.toUpperCase();
  if (upper.includes("<!DOCTYPE") || upper.includes("<!ENTITY")) {
    throw new ParseError("DOCX_XML_UNSAFE", "O DOCX contém construções XML não permitidas.");
  }

  const paragraphs = [...xml.matchAll(/<w:p(?:\s[^>]*)?>([\s\S]*?)<\/w:p>/g)].map((m) => {
    const inner = m[1]
      .replace(/<w:tab\s*\/?\s*>/g, "\t")
      .replace(/<w:br\s*\/?\s*>/g, "\n");
    const pieces = [...inner.matchAll(/<w:t(?:\s[^>]*)?>([\s\S]*?)<\/w:t>/g)].map((t) =>
      t[1]
        .replace(/&lt;/g, "<")
        .replace(/&gt;/g, ">")
        .replace(/&amp;/g, "&")
        .replace(/&quot;/g, '"')
        .replace(/&apos;/g, "'")
    );
    return cleanLine(pieces.join(""));
  }).filter(Boolean);

  const text = normalizeSpaces(paragraphs.join("\n"));
  if (!text) throw new ParseError("NO_TEXT", "Não encontramos texto utilizável no DOCX.");
  if (text.length > MAX_TEXT_CHARS) throw new ParseError("TEXT_TOO_LARGE", "O texto extraído excede o limite do Beta 1.0.");
  return text;
}

async function extractPdfText(bytes: Uint8Array) {
  const parse = async () => {
    let pdf;
    try {
      pdf = await getDocumentProxy(bytes, { maxImageSize: MAX_PDF_IMAGE_SIZE });
    } catch (err) {
      const name = err instanceof Error ? err.name : "";
      const msg = err instanceof Error ? err.message.toLowerCase() : "";
      if (name.includes("Password") || msg.includes("password")) {
        throw new ParseError("PDF_PASSWORD_PROTECTED", "PDF protegido por senha não é aceito no Beta 1.0.");
      }
      throw new ParseError("PDF_CORRUPT", "O PDF não pôde ser lido com segurança.");
    }
    if (pdf.numPages > MAX_PDF_PAGES) throw new ParseError("PDF_TOO_MANY_PAGES", "O PDF excede o limite de páginas do Beta 1.0.");
    const result = await extractText(pdf, { mergePages: true });
    const text = normalizeSpaces(String(result.text ?? ""));
    if (!text) throw new ParseError("NO_TEXT", "Este PDF não possui texto utilizável. Envie um PDF textual ou DOCX.");
    if (text.length > MAX_TEXT_CHARS) throw new ParseError("TEXT_TOO_LARGE", "O texto extraído excede o limite do Beta 1.0.");
    return text;
  };

  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new ParseError("PDF_PARSE_TIMEOUT", "O PDF excedeu o tempo seguro de processamento.")), PDF_TIMEOUT_MS)
  );
  return await Promise.race([parse(), timeout]);
}

const EMAIL_RE = /(?<![\w.+-])([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})(?![\w.-])/gi;
const PHONE_RE = /(?<!\d)(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?(?:9\s*)?\d{4}[-\s]?\d{4}(?!\d)/g;
const URL_RE = /\b(?:https?:\/\/|www\.)[^\s<>]+/gi;
const LINKEDIN_RE = /\b(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[^\s<>]+/gi;

const SECTION_ALIASES: Record<string, string[]> = {
  experiencia: ["experiência", "experiencia", "experiência profissional", "experiencia profissional", "histórico profissional", "historico profissional"],
  formacao: ["formação", "formacao", "formação acadêmica", "formacao academica", "educação", "educacao"],
  competencias: ["competências", "competencias", "habilidades", "skills", "conhecimentos"],
  idiomas: ["idiomas", "línguas", "linguas"],
  certificacoes: ["certificações", "certificacoes", "cursos", "cursos e certificações", "cursos e certificacoes"],
  resumo: ["resumo", "resumo profissional", "perfil", "perfil profissional", "objetivo"],
};

function evidence(value: unknown, confidence: "HIGH" | "MEDIUM" | "LOW", source_excerpt: string | null, inferred = false) {
  return { value, confidence, source_excerpt, inferred, user_confirmed: false };
}

function uniqueMatches(text: string, re: RegExp, group = 0) {
  re.lastIndex = 0;
  const seen = new Set<string>();
  const result: string[] = [];
  for (const match of text.matchAll(re)) {
    const raw = String(match[group] ?? match[0]).trim().replace(/[.,;)]+$/g, "");
    const key = raw.toLocaleLowerCase("pt-BR");
    if (raw && !seen.has(key)) { seen.add(key); result.push(raw); }
  }
  return result;
}

function splitSections(text: string) {
  const lookup = new Map<string, string>();
  for (const [canonical, aliases] of Object.entries(SECTION_ALIASES)) {
    for (const alias of aliases) lookup.set(alias, canonical);
  }
  const sections: Record<string, string[]> = { cabecalho: [] };
  let current = "cabecalho";
  for (const raw of text.split("\n")) {
    const line = cleanLine(raw);
    if (!line) continue;
    const heading = line.toLocaleLowerCase("pt-BR").replace(/:$/, "").replace(/\s+/g, " ");
    if (line.length <= 60 && lookup.has(heading)) {
      current = lookup.get(heading)!;
      sections[current] ??= [];
      continue;
    }
    sections[current] ??= [];
    sections[current].push(line);
  }
  return sections;
}

function candidateName(lines: string[]) {
  for (const line of lines.slice(0, 8)) {
    if (line.includes("@") || /\d{4}/.test(line) || line.length > 80) continue;
    const words = line.split(/\s+/);
    if (words.length >= 2 && words.length <= 6 && words.every((w) => /[A-Za-zÀ-ÿ]/.test(w))) {
      return evidence(line, "MEDIUM", line, true);
    }
  }
  return null;
}

function buildDraft(text: string) {
  const sections = splitSections(text);
  const emails = uniqueMatches(text, EMAIL_RE, 1);
  const phones = uniqueMatches(text, PHONE_RE);
  const linkedin = uniqueMatches(text, LINKEDIN_RE);
  const urls = uniqueMatches(text, URL_RE).filter((u) => !u.toLocaleLowerCase("pt-BR").includes("linkedin.com/in/"));

  const draft: Record<string, unknown> = {
    name: candidateName(sections.cabecalho ?? []),
    emails: emails.slice(0, 5).map((v) => evidence(v, "HIGH", safeExcerpt(text, v))),
    phones: phones.slice(0, 5).map((v) => evidence(v, "HIGH", safeExcerpt(text, v))),
    linkedin: linkedin.slice(0, 5).map((v) => evidence(v, "HIGH", safeExcerpt(text, v))),
    links: urls.slice(0, 10).map((v) => evidence(v, "HIGH", safeExcerpt(text, v))),
    summary: null,
    experience_evidence: [],
    education_evidence: [],
    skills_evidence: [],
    languages_evidence: [],
    certifications_evidence: [],
    requires_user_confirmation: true,
  };

  const mappings: Array<[string, string]> = [
    ["experiencia", "experience_evidence"], ["formacao", "education_evidence"],
    ["competencias", "skills_evidence"], ["idiomas", "languages_evidence"],
    ["certificacoes", "certifications_evidence"],
  ];
  const summary = sections.resumo ?? [];
  if (summary.length) {
    const value = summary.slice(0, 12).join("\n");
    draft.summary = evidence(value, "HIGH", value, false);
  }
  for (const [section, target] of mappings) {
    const lines = (sections[section] ?? []).slice(0, 80);
    draft[target] = lines.map((line) => evidence(line, "MEDIUM", line, false));
  }
  return draft;
}

async function markRejected(serviceClient: ReturnType<typeof createClient>, row: Record<string, unknown>, code: string) {
  const retention = new Date(Date.now() + REJECTED_RETENTION_HOURS * 60 * 60 * 1000).toISOString();
  await serviceClient.from("career_documents").update({
    file_status: "rejected",
    rejection_code: code,
    raw_file_retention_until: retention,
  }).eq("id", row.id).eq("user_id", row.user_id);
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

  const { data: row, error: rowError } = await serviceClient.from("career_documents")
    .select("id,user_id,original_filename_display,detected_type,size_bytes,sha256,storage_object_path,file_status,deleted_at")
    .eq("id", documentId).eq("user_id", user.id).maybeSingle();
  if (rowError) return json(503, { error: "DOCUMENT_LOOKUP_FAILED" });
  if (!row || row.deleted_at || row.file_status === "deleted") return json(404, { error: "DOCUMENT_NOT_FOUND" });

  const { data: existingDraft } = await serviceClient.from("career_profile_drafts")
    .select("id,status,draft_json,parser_version")
    .eq("document_id", row.id).eq("parser_version", PARSER_VERSION).maybeSingle();
  if (existingDraft) {
    return json(200, { document_id: row.id, draft_id: existingDraft.id, status: "DRAFT_REQUIRES_CONFIRMATION", idempotent: true, candidate_profile_draft: existingDraft.draft_json });
  }

  if (row.file_status !== "quarantined" && row.file_status !== "safe_for_parse") {
    return json(409, { error: "DOCUMENT_STATE_NOT_PROCESSABLE", file_status: row.file_status });
  }
  if (!row.storage_object_path) return json(409, { error: "RAW_FILE_NOT_AVAILABLE" });

  const { data: blob, error: downloadError } = await serviceClient.storage.from(BUCKET).download(row.storage_object_path);
  if (downloadError || !blob) return json(503, { error: "QUARANTINE_DOWNLOAD_FAILED" });
  const bytes = new Uint8Array(await blob.arrayBuffer());

  try {
    if (bytes.length <= 0 || bytes.length > MAX_FILE_BYTES || bytes.length !== Number(row.size_bytes)) {
      throw new ParseError("FILE_SIZE_MISMATCH", "O arquivo não corresponde ao metadado de quarentena.");
    }
    const digest = await sha256(bytes);
    if (digest !== row.sha256) throw new ParseError("FILE_HASH_MISMATCH", "O arquivo não corresponde ao hash de quarentena.");

    let text: string;
    if (row.detected_type === "pdf") {
      if (!(bytes[0] === 0x25 && bytes[1] === 0x50 && bytes[2] === 0x44 && bytes[3] === 0x46 && bytes[4] === 0x2d)) {
        throw new ParseError("TYPE_MISMATCH", "A assinatura PDF não corresponde ao arquivo.");
      }
      text = await extractPdfText(bytes);
    } else if (row.detected_type === "docx") {
      if (!(bytes[0] === 0x50 && bytes[1] === 0x4b)) throw new ParseError("TYPE_MISMATCH", "A assinatura DOCX não corresponde ao arquivo.");
      text = await extractDocxText(bytes);
    } else {
      throw new ParseError("UNSUPPORTED_REAL_TYPE", "Tipo real não suportado.");
    }

    await serviceClient.from("career_documents").update({ file_status: "safe_for_parse", rejection_code: null }).eq("id", row.id).eq("user_id", user.id);
    const draft = buildDraft(text);
    const { data: draftRow, error: draftError } = await serviceClient.from("career_profile_drafts").insert({
      user_id: user.id,
      document_id: row.id,
      draft_version: 1,
      draft_json: draft,
      parser_version: PARSER_VERSION,
      status: "requires_confirmation",
    }).select("id").single();

    if (draftError || !draftRow) {
      const { data: racedDraft } = await serviceClient.from("career_profile_drafts")
        .select("id,draft_json").eq("document_id", row.id).eq("parser_version", PARSER_VERSION).maybeSingle();
      if (racedDraft) return json(200, { document_id: row.id, draft_id: racedDraft.id, status: "DRAFT_REQUIRES_CONFIRMATION", idempotent: true, candidate_profile_draft: racedDraft.draft_json });
      return json(503, { error: "DRAFT_WRITE_FAILED" });
    }

    await serviceClient.from("career_documents").update({ file_status: "parsed", parser_version: PARSER_VERSION }).eq("id", row.id).eq("user_id", user.id);
    await serviceClient.from("career_audit_events").insert({
      user_id: user.id,
      event_type: "resume_parse",
      entity_type: "career_document",
      entity_id: row.id,
      outcome: "parsed",
      reason_code: "DRAFT_REQUIRES_CONFIRMATION",
      metadata_safe: { parser_version: PARSER_VERSION, detected_type: row.detected_type },
    });

    return json(200, { document_id: row.id, draft_id: draftRow.id, status: "DRAFT_REQUIRES_CONFIRMATION", idempotent: false, candidate_profile_draft: draft });
  } catch (err) {
    const parseError = err instanceof ParseError ? err : new ParseError("PARSER_INTERNAL_ERROR", "Falha controlada no parser.");
    await markRejected(serviceClient, row, parseError.code);
    return json(422, { error: parseError.code, message: parseError.message });
  }
});
