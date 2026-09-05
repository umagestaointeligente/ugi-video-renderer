# Cena Certa V2 — Portability Certification

This document preserves the evidence previously exposed as the `cena-certa-route-b-replay.yml` workflow.

The replay proved that the sealed Cena Certa V2 source snapshot and physical masters could be packaged and executed in an isolated GitLab-style environment using the same pinned runtime. It was a **portability certification**, not a live independent production fallback.

Certified snapshot:
- source SHA: `ee96bd0afaa15c4fea17bfedd85799167a93b6e8`
- source tree SHA: `2c550b44c4770b9c8a3157f8723de9b96153d001`
- Story blob: `bebaa2c265733236ab31cd80b24f8f8b46e740bd`
- CTA blob: `66cdec74979388a3435125a89584fc0a4c5d889a`
- runtime digest: `sha256:5e35dcb15a263b190fd91ad759c6e570d16a186c180fe18fe3f8080ac86acf9c`

Operational rule:
- This certification MUST NOT be counted as a production Route B.
- GitLab runtime cloning is forbidden in the GitHub production path.
- GitLab CI remains outside the critical path while its capacity is not live-proven.
- The only production render executor is the self-contained GitHub snapshot declared in `ops/cena-certa/route-registry.json`.

The old replay workflow was removed from `.github/workflows` to prevent an operator from mistaking a certification harness for a live fallback route.
