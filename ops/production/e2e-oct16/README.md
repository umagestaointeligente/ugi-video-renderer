# Real media recovery acceptance

This is a nonpublishing acceptance run, not a scheduled editorial package.
Run `python scripts/production/e2e_render.py --channel cena-certa`, `--channel vsa`, or `--channel ugi` from the checkout. Install FFmpeg, DejaVu Sans, requests, Pillow, PyYAML, yt-dlp and edge-tts==7.3.1 first. The GitHub workflow **Three Channel Real Media E2E** can run the same three jobs through Run workflow.

Each channel must actually acquire public source media, use its real render path, and produce H.264 1080x1920 30 fps / AAC 48 kHz MP4 files. Independent checks decode the complete output, reject black intervals, insufficient motion, silent audio/tails and audio/video duration mismatch. The artifact package copies only files whose hashes still match after QA. A receipt alone is not the deliverable.

- Cena Certa: original PT-BR dialogue from a newly acquired scene of À Procura da Felicidade, a film in the proposed Oct16 Facebook grade. The test uses seconds 81–125 (the family-pressure/laundry scene), not the job-offer scene in the proposed editorial brief. It does not authorize that editorial substitution or grant republication rights. Globo must not be used for YouTube.
- VSA: the three pending Oct13 topics, synthesized with the original Antonio voice, actual scene sources, canonical mask/CTA and per-item receipts. Rebuilding pending candidates is not evidence of a new editorial topic or release approval.
- UGI: new public-domain US food-bank logistics footage (DVIDS 799059), a new PT-BR narration, captions timed to actual Edge word boundaries and ducked Carefree music. The caption must retain the music attribution in ATTRIBUTION.txt. The narration explicitly identifies the footage as US food-bank operations.

Every technical receipt retains release_allowed=false, published=false and scheduled=false. Full 180-day history checks, source rights and editorial/audio/visual review remain required before scheduling. A discovery URL, accessible video or a green test cannot be substituted for those approvals.

Recovery controls: public HTTPS intake without cookies or DRM bypass, bounded network/process timeouts, URL+SHA256 cache identity, exact narration/text identity, atomic source downloads, partial narration/metadata cleanup, per-channel failure isolation, and a nonzero exit on incomplete output. YouTube authentication failures are terminal for the provider probe; do not loop over the remaining links or silently replace scenes with trailers.

Visual inspection found and repaired two semantic faults beyond technical QA: the old second Newton source was a CGI wrecking-ball illustration mislabeled REAL, and Olivia's old opening window cut to Fauci. The Newton source is now the physical UniServeScienceVIDEO demonstration (CC BY 3.0, credit required) at 10 s; Olivia starts at 19 s with both participants visible. These repairs do not auto-approve unrelated scene or release gates.
