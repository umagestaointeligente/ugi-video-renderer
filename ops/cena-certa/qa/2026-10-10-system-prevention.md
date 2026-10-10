# System prevention audit — 2026-10-10

Base inspected: `6d65b4dbc3d2d83aedf0300e0012edbec746a675` in `ugi-video-renderer`.
Scope: syntax/structure inspection of all 265 main-branch workflows (801 original Bash steps and 159 embedded Python snippets), compilation of the repository Python sources, detailed Cena Certa renderer/release review, UGI observer/policy regression, VSA release-validator self-tests and workflow compliance review. This is not a certification of every operational branch, remote service or social account.

## Confirmed incident

- Oct11 source probe `38020917782`: three YouTube bot-access denials; the sources were subsequently replaced.
- Benchmark `38021028771`: an apostrophe in an overlay broke the FFmpeg filter grammar.
- Benchmark `38021588388`: `NO_BLACK_FAIL`; subsequent source-window offsets avoided the black sections.
- Successful `38022343452`, commit `65f7fe2de7bf23c00d90e6bb3a62d25f08337500`: issue #77 and logs match all 12 archived MP4 hashes. Artifact 11659695442 ZIP digest independently verified: `3ab8f784f9781e7c2d682ed8e7f606f72d5f44f4ce38700342acd7ac459eb51f`.
- The successful run executes the dated renderer but bypasses the existing editorial receipt guard. Its 263/263 history coverage proves processing coverage, not a complete 60-day query.
- Tropa streak 6 and Shaolin streak 5 are below the implemented 11-frame limit. This numerical result is not a contractual clearance or proof that matching images are different scenes. No threshold was loosened or arbitrarily lowered.

## Corrections

1. All 19 Cena Certa release routes now require the existing editorial guard before release creation/upload, and recheck before issuing PASS. Covers historical replay and Oct05/Oct07 repairs. The guard checks exact run ID, attempt, commit, master hash, all mandatory receipts and network subdirectories; invalid input overwrites stale approval with BLOCK. Existing assets cannot be silently overwritten with `--clobber`.
2. All identified Cena Certa FFmpeg black/silence checks now enforce process failure. An unsuccessful detector cannot be interpreted as a clean result.
3. Oct05/06/07/08/09/11 renderers require complete processing coverage, reject empty histories, persist raw candidate/history fingerprints, bind candidate fingerprints to masters, and record fingerprint file hashes. The release guard checks these files. Complete 60-day history evidence is still separately required.
4. Shared `textfile` overlays with `expansion=none` keep apostrophes, colons, percent expressions and other text out of FFmpeg syntax. Concat video legs use square pixels. Source windows reject non-finite, negative or out-of-range inputs instead of silently truncating clips.
5. Downloaded sources must match yt-dlp's extracted identity. Bot denials and identity mismatches stop blind retries. Normalized source metadata is preserved. Oct05/08/09/11 probes now consume the production manifest instead of a separately maintained list.
6. A legacy Sep26 in-render upload is contained; rendering records technical output only. Recent renderers and repair summaries no longer assign editorial approval constants.
7. New structural regression verifies actual Cena Certa guard steps, failure propagation, write ordering and overwrite protection. CI covers all dated renderers/helpers rather than Oct03 alone.
8. UGI's read-only observer accepts the documented Buffer legacy state while preserving Metricool primary routing. HTTP 403/404/429 are not positive reachability proof, and naive timestamps are rejected rather than assigned the runner timezone.
9. VSA workflow compliance parses actual gate actions and checks job/step write order and dependency protection; a comment or attempted shell execution of `action.yml` is not an action gate. GitHub release writes are included in the mutation checks.

## Validation

- Full workflow YAML, Bash syntax and embedded Python parse: PASS.
- All repository scripts/tests compile: PASS.
- Unit/regression suite: 50 tests run, 49 PASS and 1 skipped (social preflight belongs to the companion repository and is absent here).
- Real local FFmpeg textfile test with apostrophe, colon, brackets, backslash and percent expression: PASS.
- Cena Certa release-barrier audit: PASS, 19 workflows.
- VSA existing release-validator self-test: PASS, 14 invalid cases blocked.
- No real source ingest, TTS or final production render was executed by this audit. No social post, agenda mutation, Metricool change, release upload, merge or artifact deletion was performed.

## Activation and unresolved external/editorial conditions

The patch is isolated for review and has not been merged into production. Mandatory source/rights/visual/transformation/CTA/history receipts are not fabricated. Missing receipts intentionally BLOCK release and PASS generation, even after a successful technical render. Older schemas lacking those proofs need evidence migration before replay.

The main-branch VSA inventory contains 23 legacy workflows with compliance findings; several are read-only probes. They are not asserted to be active production routes. The checker now exposes them; they require per-route migration/retirement before an approved replay. Their historic schedules/publishing definitions were not rewritten during this audit.

VSA Oct09 production is on a separate operational branch. Logs of `37876957512`, `37877093226`, `37877314113` confirm duration blocks at projected 54.7827 s, final 42.9333 s, and projected 58.5493 s respectively. They are not runner failures. The branch's narration/scene timing needs a measured editorial/render correction; these dated production inputs are not part of the main-branch patch. The 45–55 s final gate remains intact.

External source availability, provider capacity and editorial approvals cannot be guaranteed by code. Preventive containment must stop and report those conditions rather than manufacture success. The old #77 PASS remains a historical technical result; this patch does not edit it into full contractual approval.
