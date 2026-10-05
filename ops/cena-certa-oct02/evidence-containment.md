# Oct02 evidence containment

Issues 59/60/61/62/65/66/67/68 retain their historical records. They are technical render observations, not production editorial or publication approvals. The 24 issued item records are retained as scene reservations; they are not a complete 60-day publication history.

The Oct02 renderer emits technical status only. Source identity, rights, visual review, transformation, CTA and complete perceptual history require fresh receipts bound to content ID, final SHA-256 and run/attempt/commit/job. Empty production receipts intentionally block. The guard recomputes final-file SHA and rejects overlapping reserved source intervals even if file/frame hashes change. It validates perceptual-check receipts; it does not itself implement or manufacture the perceptual-history service.

A single four-network job closes the whole batch before any release or PASS issue. Historical production is manual only, serialized; no replay on merge. Releases use run/attempt tags, have no clobber, and pin the commit. YouTube narrated CTA is no longer excluded; actual CTA inspection is still required. FFmpeg check failures now raise rather than masquerading as successful QA.

Validation: 10 local regressions passed. Hosted PR checks remain required. No production run, release upload, social publication, Metricool operation, historical issue mutation or merge was performed by this change. Broader future-date workflows are outside this patch.

Companions: renderer PR 56 and orbit-media-labs-automation PR 499 remain independently pending. This ports the renderer evidence validator into Oct02 without merging either PR.
