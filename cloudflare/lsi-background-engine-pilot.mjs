const VERSION = "lsi-background-engine-pilot-r1-2026-08-29";
const MIN_CADENCE_MS = 10000;
const MAX_CADENCE_MS = 86400000;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {"content-type":"application/json; charset=utf-8","cache-control":"no-store"},
  });
}

function cleanId(value) {
  const id = String(value || "").trim();
  if (!/^[A-Za-z0-9._-]{8,120}$/.test(id)) throw new Error("mission_id_invalid");
  return id;
}

function validateMission(body, missionId) {
  const objective = String(body?.objective || "").trim();
  if (!objective || objective.length > 8000) throw new Error("objective_invalid");
  const cadenceMs = Math.max(MIN_CADENCE_MS, Math.min(MAX_CADENCE_MS, Number(body?.cadence_ms ?? 60000)));
  const maxCycles = Math.max(1, Math.min(1000, Number(body?.max_cycles ?? 3)));
  const monetaryBudget = Number(body?.monetary_budget ?? 0);
  if (!Number.isFinite(monetaryBudget) || monetaryBudget < 0) throw new Error("monetary_budget_invalid");
  if (monetaryBudget > 0) throw new Error("pilot_zero_cost_only");
  return {
    mission_id: missionId,
    project_id: String(body?.project_id || "LSI").slice(0,120),
    objective,
    success_metric: String(body?.success_metric || "pilot_background_cycle_proof").slice(0,500),
    cadence_ms: cadenceMs,
    max_cycles: maxCycles,
    monetary_budget: 0,
    allowed_capabilities: Array.isArray(body?.allowed_capabilities) ? body.allowed_capabilities.slice(0,32).map(String) : ["state_only"],
    status: "ACTIVE",
    cycle_count: 0,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_cycle_at: null,
    next_alarm_at: null,
    execution_mode: "STATE_ONLY_PILOT",
    production_actions: false,
    external_paid_provider: false,
  };
}

export class MissionState {
  constructor(ctx, env) {
    this.ctx = ctx;
    this.env = env;
  }

  async fetch(request) {
    const url = new URL(request.url);
    if (request.method === "POST" && url.pathname.endsWith("/start")) {
      let body;
      try { body = await request.json(); } catch { return json({ok:false,error:"invalid_json"},400); }
      let mission;
      try { mission = validateMission(body, cleanId(body?.mission_id)); }
      catch (error) { return json({ok:false,error:String(error?.message ?? error)},400); }
      const existing = await this.ctx.storage.get("mission");
      if (existing && existing.status === "ACTIVE") return json({ok:false,error:"mission_already_active",mission:existing},409);
      const next = Date.now() + mission.cadence_ms;
      mission.next_alarm_at = new Date(next).toISOString();
      await this.ctx.storage.put("mission", mission);
      await this.ctx.storage.setAlarm(next);
      return json({ok:true,mission});
    }

    if (request.method === "POST" && url.pathname.endsWith("/tick")) {
      const mission = await this.runCycle("manual_tick");
      return json({ok:Boolean(mission), mission: mission || null});
    }

    if (request.method === "POST" && url.pathname.endsWith("/pause")) {
      const mission = await this.ctx.storage.get("mission");
      if (!mission) return json({ok:false,error:"mission_not_found"},404);
      mission.status = "PAUSED";
      mission.updated_at = new Date().toISOString();
      mission.next_alarm_at = null;
      await this.ctx.storage.put("mission", mission);
      await this.ctx.storage.deleteAlarm();
      return json({ok:true,mission});
    }

    if (request.method === "GET") {
      const mission = await this.ctx.storage.get("mission");
      return json({ok:Boolean(mission), mission: mission || null});
    }
    return json({ok:false,error:"not_found"},404);
  }

  async runCycle(reason) {
    const mission = await this.ctx.storage.get("mission");
    if (!mission || mission.status !== "ACTIVE") return mission || null;
    mission.cycle_count += 1;
    mission.last_cycle_at = new Date().toISOString();
    mission.updated_at = mission.last_cycle_at;
    mission.last_cycle = {
      reason,
      security_state:"PASS",
      action_state:"NO_EXTERNAL_ACTION_PILOT",
      cost_state:"ZERO_COST",
      evidence:["durable_object_alarm_or_tick"],
    };
    if (mission.cycle_count >= mission.max_cycles) {
      mission.status = "SUCCESS";
      mission.next_alarm_at = null;
      await this.ctx.storage.put("mission", mission);
      return mission;
    }
    const next = Date.now() + mission.cadence_ms;
    mission.next_alarm_at = new Date(next).toISOString();
    await this.ctx.storage.put("mission", mission);
    await this.ctx.storage.setAlarm(next);
    return mission;
  }

  async alarm() {
    await this.runCycle("durable_object_alarm");
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return json({
        ok:true,
        service:"lsi-background-engine-pilot",
        version:VERSION,
        durable_objects_bound:Boolean(env.MISSIONS),
        production_actions:false,
        external_paid_provider:false,
        zero_cost_policy:true,
      });
    }
    const match = url.pathname.match(/^\/missions\/([A-Za-z0-9._-]{8,120})(?:\/(start|tick|pause))?$/);
    if (!match) return json({ok:false,error:"not_found"},404);
    const missionId = match[1];
    const suffix = match[2] || "";
    const id = env.MISSIONS.idFromName(missionId);
    const stub = env.MISSIONS.get(id);
    const forwardUrl = new URL(request.url);
    forwardUrl.pathname = `/mission/${missionId}/${suffix}`;
    let body = undefined;
    if (request.method !== "GET") {
      const raw = await request.text();
      if (raw) {
        try {
          const parsed = JSON.parse(raw);
          parsed.mission_id = missionId;
          body = JSON.stringify(parsed);
        } catch { body = raw; }
      }
    }
    return stub.fetch(new Request(forwardUrl.toString(), {
      method: request.method,
      headers: request.headers,
      body,
    }));
  },
};
