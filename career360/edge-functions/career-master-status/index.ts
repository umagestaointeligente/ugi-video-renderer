import { createClient } from "jsr:@supabase/supabase-js@2.114.0";

const H = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const out = (status: number, body: unknown) => new Response(JSON.stringify(body), {
  status,
  headers: { ...H, "Content-Type": "application/json", "Cache-Control": "no-store" },
});

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: H });
  if (req.method !== "POST") return out(405, { error: "METHOD_NOT_ALLOWED" });
  const auth = req.headers.get("Authorization");
  if (!auth?.startsWith("Bearer ")) return out(401, { error: "AUTH_REQUIRED" });

  const url = Deno.env.get("SUPABASE_URL");
  const anon = Deno.env.get("SUPABASE_ANON_KEY");
  if (!url || !anon) return out(500, { error: "SERVER_CONFIG_ERROR" });

  const client = createClient(url, anon, {
    global: { headers: { Authorization: auth } },
    auth: { persistSession: false, autoRefreshToken: false },
  });
  const { data, error } = await client.rpc("career_master_status_v1");
  if (error) {
    const message = String(error.message || "");
    if (message.includes("MASTER_REQUIRED")) return out(403, { error: "MASTER_REQUIRED" });
    if (message.includes("AUTH_REQUIRED")) return out(401, { error: "AUTH_REQUIRED" });
    return out(503, { error: "MASTER_STATUS_FAILED" });
  }
  return out(200, data);
});