# VSA Preventive Release Gate — 2026-09-14

Scope: ORBIT/VSA only. Cena Certa, UGI and other publishing routes are out of scope.

A VSA item may reach Metricool brand `6935441` only when the exact final MP4 is bound by SHA-256 to a V2 release receipt that passes the preventive validator.

Hard blocks include: unapproved/foreign-accent voice; missing or wrong V2 mask; title/caption outside safe zones; generic filler; PERSON_PROFILE target mismatch or unrelated celebrity filler; reuse of a previous final/master/CTA composite as source; stale work directory; wrong Metricool brand/channel; pre-CTA legacy/unrelated-frame evidence; final master changed after QA; scheduling before release gate.

Retry policy: build from zero on failure; maximum three attempts per topic; after the third failure substitute an eligible backup topic while preserving the slot. A failed item must not block unrelated schedule slots.

Proof requirement: CI self-test must accept a valid receipt and reject every deliberately bad case before merge.
