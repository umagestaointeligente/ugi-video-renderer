# UGI autonomous policy watchdog

The watchdog is event-driven and preserves the deployed Cloudflare Worker,
existing credentials, publication schedules, renderer, and multi-AI council.
It wakes after existing engine, rendering, policy, and Buffer-readback runs;
there is no new cron trigger and no cross-project credential sharing.

The inspector validates that Buffer remains the only publisher, Metricool
remains read-only analytics, publication recovery stays bounded, and the latest
growth-runtime receipt matches the active policy hash. Existing Buffer or
command-authentication failures become deduplicated GitHub incident records
rather than unproven success or unauthorized remediation.

Worker health is queried read-only. No public publication, retry, payment,
Worker deployment, credential change, or destructive operation is performed.
The existing `magic-engine/multi_ai_council.py` remains the authorized
zero-cost-first multi-model integration when its configured credentials and
providers are available.
