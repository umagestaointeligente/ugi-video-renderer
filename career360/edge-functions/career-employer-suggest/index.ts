import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

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

function clean(value: unknown, max = 80): string {
  if (typeof value !== "string") return "";
  return value.replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, max);
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
  if (userError || !userData.user) return json(401, { error: "INVALID_SESSION" });

  let payload: any;
  try { payload = await req.json(); } catch { return json(400, { error: "INVALID_JSON" }); }
  const q = clean(payload?.q);
  if (q.length < 2) return json(200, { items: [] });

  const service = createClient(url, serviceKey, { auth: { persistSession: false, autoRefreshToken: false } });
  const pattern = `%${q.replace(/[%_]/g, "")}%`;

  const [{ data: entities, error: entityError }, { data: aliases, error: aliasError }] = await Promise.all([
    service.from("career_employer_entities").select("canonical_name").eq("active", true).ilike("canonical_name", pattern).limit(8),
    service.from("career_employer_aliases").select("alias_name,career_employer_entities!inner(canonical_name,active)").eq("career_employer_entities.active", true).ilike("alias_name", pattern).limit(8),
  ]);

  if (entityError || aliasError) return json(503, { error: "EMPLOYER_SUGGEST_LOOKUP_FAILED" });

  const names: string[] = [];
  const seen = new Set<string>();
  const add = (name: unknown) => {
    if (typeof name !== "string") return;
    const trimmed = name.trim();
    if (!trimmed) return;
    const key = trimmed.toLocaleLowerCase("pt-BR");
    if (!seen.has(key)) { seen.add(key); names.push(trimmed); }
  };

  for (const row of entities ?? []) add(row.canonical_name);
  for (const row of aliases ?? []) add((row as any).career_employer_entities?.canonical_name ?? row.alias_name);

  return json(200, { items: names.slice(0, 8) });
});