# VSA Oct13 preventive recovery

Baseline: `3e32ef5aca6e46a477990a22188e74d2af0c3710`, run `38308406238`, attempts 1–3.
All attempts fail on the first Edge TTS narration with HTTP 403. This change does not claim the remote provider has recovered.

## Changes

- Prepare every narration and CTA before downloads and animations. Render reuses those exact files within the fresh build.
- Timeout synthesis and audio decoding; classify provider 403 without exposing connection URLs; delete partial/stale files; never replace failed narration with silence or an unapproved voice.
- Optional `VSA_NARRATION_BUNDLE` points to a local JSON manifest of pre-generated narration. Each clip is bound to exact text, approved voice profile, rate and SHA-256, and must fully decode. Missing/mismatched clips block; no fallback to the network when a bundle was selected. Metadata is an identity claim, not independent proof of voice/accent: listening QA remains unverified and release remains blocked.
- Downloads are fresh and atomic; interrupted downloads cannot become cache hits. Actual duplicate asset bytes and insufficient source windows block before rendering. SAR is normalized for generated scene/CTA video.
- Run validator self-test explicitly. Remove the swallowed attempt to execute composite YAML as shell. Workflow compliance rejects the observed fake-gate and swallowed-validation patterns. This static guard is not a complete shell/YAML security verifier.
- Remove renderer self-certification of required gates, semantic match, rights verification, voice and tail review. Receipts remain `PENDING_QA`, `release_eligible=false`; final validator therefore blocks. Contact sheets and metadata alone cannot establish audiovisual quality.

## Bundle format

`clips` maps a SHA-256 key to `{voice, rate, text, file, sha256}`. The key is SHA-256 of UTF-8 `json.dumps([voice, rate, text], ensure_ascii=False, separators=(",", ":"))`. File paths resolve relative to the manifest and cannot escape its directory. Supply all scene clips and CTA; rates remain `-2%` and `+18%` respectively. No bundle files or approved listening results were invented in this change.

## Validation

- Python compilation passed.
- Seven unittest methods passed, including 12 provider/bundle subcases, interrupted acquisition, duration bounds/preflight, blocked self-certification, and three fake-gate variants.
- Existing receipt self-test blocked all 14 invalid cases.
- Updated workflow compliance passed; YAML parsing and `bash -n` passed for every embedded shell block.
- Tests use mocked provider/download responses. No successful live TTS, full triple render, end-to-end media QA or CI recovery is asserted.

## Acceptance and rollback

Recovery requires actual valid narration, usable source assets, full rendering and independent machine QA evidence for each required gate, bound to the exact master. This patch intentionally does not invent those results or tokens. Shared workflows outside Oct13 need separate compatibility checks before adopting the tightened guard. The changes are reviewable on an isolated branch, without altering production branch, schedules or Metricool. Rollback consists of discarding the proposed branch/PR before merge; production was not promoted.

## Follow-up: provider recovery investigation

Historical success run 36512160336 used edge-tts 7.2.8, aiohttp 3.14.3 and multidict 6.9.1. Failing Oct13 runs used edge-tts 7.2.8, aiohttp 3.14.5 and multidict 7.1.0. Two bounded local probes, after loading the system trust store into the verified SSL context, both received HTTP 403 and produced zero audio bytes. Before loading system certificates the local environment failed certificate verification; that local TLS issue must not be conflated with the GitHub 403. No SSL verification was disabled. These results do not support claiming that a dependency rollback restores TTS.

The PR CI now compares the two dependency pairs on GitHub runners with one bounded probe per pair, preserves only sanitized JSON reports for three days, and fails if either provider test fails. It never renders, issues a release token, publishes, schedules, or uploads narration. Probe success establishes only that the tested narration request produced decodable audible audio at that moment. Full recovery still requires the complete production gates.

Audio validation now uses a real FFmpeg decode and measured peak level. Silent audio or missing loudness measurement blocks; errors distinguish certificate failures from provider 403. Eight local unittest methods passed, including real tone acceptance and real silence rejection. No silent clip is a narration fallback.
