# UGI Signal Engine — Sandbox V1

Status: EXPERIMENTAL / ISOLATED / NO PRODUCTION HOOKS

This pilot tests deterministic traction scoring before any LLM/Gemini semantic step.

## Production safety

- Branch only: `sandbox/ugi-signal-engine-luna-v1`
- No changes to `main`
- No publishing, scheduling or social account access
- No secrets in repository files
- No GitHub Actions trigger in V1
- JSON is the machine-readable source of truth

## Important correction: traction velocity

`views / hours_since_publication` is only an average since publication. It is **not** true recent velocity.

V1 prefers two or more snapshots and calculates:

`recent_views_per_hour = (views_now - views_previous) / elapsed_hours`

If only one snapshot exists, the engine may calculate an explicitly labelled fallback `average_views_per_hour_since_publish`, but it must never be presented as measured recent velocity.

## Input

A JSON file containing videos and statistic snapshots. Example:

```json
{
  "videos": [
    {
      "video_id": "abc",
      "title": "Example",
      "published_at": "2026-08-28T00:00:00Z",
      "snapshots": [
        {"captured_at": "2026-08-28T01:00:00Z", "views": 1000, "likes": 80, "comments": 10},
        {"captured_at": "2026-08-28T03:00:00Z", "views": 1800, "likes": 140, "comments": 18}
      ]
    }
  ]
}
```

## Output

Per video:

- measured/fallback velocity
- engagement rate
- snapshot age
- measurement mode
- deterministic traction rank

Only the small final shortlist should be sent to an LLM/Gemini for semantic UGI fit and hook generation.

## API collection

YouTube Data API collection is deliberately separated from this scoring engine. This keeps API quotas, credentials and network failure out of the deterministic scoring core. A collector can be added later after quota/readback validation.
