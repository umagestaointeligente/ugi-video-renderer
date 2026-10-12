# VSA Assisted Animation Pilot V1

Status: PILOT_FAIL_CLOSED  
Stage: ANIMAÇÃO EXPLICATIVA ASSISTIDA  
Branch scope: VSA only  
Automatic publication: disabled  
Production calls to external tools: disabled  
Maximum incremental cost: R$ 0,00

## 1. Architecture found

The active VSA path on main is already fail-closed:

1. `config/vsa/VSA_VISUAL_STORY_ENGINE_V1.json` is the active VSA story/release policy.
2. `scripts/vsa/render_preventive_v3.py` validates sources/entity integrity, wipes the workdir, runs the canonical renderer, binds SHA-256 and emits the release receipt.
3. `scripts/vsa/render_canonical_v2.py` is the current visual renderer.
4. `scripts/vsa/validate_release_receipt.py` validates the exact master/release token and prevents schedule mutation before the gate.
5. `.github/actions/vsa-release-gate/action.yml` is the canonical final release gate.

No generic external-tool capability registry was discoverable in the accessible main-branch VSA paths. To avoid modifying the active VSA policy, this pilot adds a scoped capability overlay:

`config/vsa/VSA_ASSISTED_ANIMATION_CAPABILITIES_V1.json`

The existing VSA policy and release gate remain authoritative downstream.

## 2. Placement in the VSA flow

Approved narration
→ assisted visual plan
→ manual generation package
→ optional manual ZSky/Steve generation
→ controlled asset intake
→ technical validation
→ editorial/human review
→ approved-for-editing normalization
→ timeline patch for current renderer
→ current VSA preview/render path
→ current VSA final QA/release gate
→ human approval
→ publication remains outside this pilot

The pilot never writes to Metricool, YouTube Studio, Instagram or Facebook.

## 3. Tool status verified on 2026-09-19

### ZSky AI

Official site: https://zsky.ai/  
Terms: https://zsky.ai/terms  
Pricing: https://zsky.ai/pricing

Current public terms indicate:
- free generation is available without card;
- commercial use is allowed on free;
- automated/bot/headless/free-tier API use is prohibited;
- free video output carries a ZSky wordmark/watermark plate.

VSA decision:
- usage_mode: manual_pilot_only
- production_enabled: false
- automatic_publication: false
- current blocker: rejected_watermark
- effective production route: current_pipeline

The watermark must not be hidden, cropped or removed. A free ZSky clip can be inspected as a pilot, but it cannot be admitted into a VSA production master while that watermark remains mandatory.

### Steve AI

Official site: https://www.steve.ai/  
Pricing: https://app.steve.ai/pricing  
Commercial-rights FAQ: https://support.steve.ai/en/articles/8295555-can-i-monetize-the-videos-i-create-with-steve-ai

Current public information indicates:
- a Free account exists;
- the Free comparison table does not provide downloadable video format;
- Steve AI states monetization/commercial rights come with paid plans.

VSA decision:
- usage_mode: manual_pilot_only
- production_enabled: false
- automatic_publication: false
- current blocker: rejected_rights / download not eligible
- effective production route: current_pipeline

Under the R$ 0 rule, Steve AI can be used for prompt/storyboard exploration only. A production asset is fail-closed unless zero-cost download and commercial rights are explicitly verified in the future.

## 4. Routing

ZSky candidate:
- mechanisms, machines, phenomena, non-graphic anatomy, planetary motion, reconstructions, maps, scale, internal structures, cinematic conceptual scenes.

Steve AI candidate:
- 2D explainer, illustrated sequence, timeline, infographic, youth/light tone, Léo scenes without speaking avatar.

Current pipeline:
- better verified real footage exists;
- real public figure is required;
- candidate tool is blocked by watermark, cost, rights or download;
- animation adds no comprehension.

The planner records both:
- tool_candidate
- production_route

Today, external candidates can be proposed, but production_route remains current_pipeline whenever the current zero-cost terms fail VSA policy.

## 5. Visual contract

Each selected scene contains:

- scene_id
- narration_excerpt
- visual_purpose
- main_verb
- visual_action
- tool_candidate
- usage_mode
- production_route
- duration_seconds
- aspect_ratio
- target_resolution
- prompt_pt
- prompt_en
- negative_prompt
- first_frame
- development
- last_frame
- camera_motion
- caption_safe_area
- continuity_notes
- representation_disclosure
- publication_allowed

VERB → VISUAL is enforced at planning level.

Examples:
- vaporizou → visible liquid-to-vapor transition;
- afundou → visible descent/submersion;
- curvou → visible trajectory change;
- deslizou → visible lateral displacement.

## 6. Manual package

Command example:

python scripts/vsa/assisted_animation_stage.py plan \
  --request examples/vsa/assisted_animation/leidenfrost_request.json \
  --out /tmp/leidenfrost_plan.json \
  --package /tmp/leidenfrost_manual_package.md

The package contains:
- official tool link;
- PT prompt;
- EN prompt;
- duration;
- format;
- narration excerpt;
- first/last frame;
- camera direction;
- continuity;
- current blocker;
- effective production route.

No external tool is opened automatically.

## 7. Controlled intake

Expected filename:

vsa_[video_id]_[scene_id]_[tool]_[version].mp4

Examples:

vsa_leidenfrost_scene_01_zsky_v01.mp4  
vsa_leidenfrost_scene_03_steve_ai_v01.mp4

Required operator metadata includes:
- generation_tool
- video_id
- watermark_present
- rights_confirmed
- commercial_use_confirmed
- download_allowed
- cost_brl
- credits_consumed
- payment_required
- card_required
- trial_with_future_charge
- narration_visual_match
- continuity_ok
- physical_coherence
- historical_scientific_fidelity
- deformed_characters_or_anatomy
- generated_text_or_bad_text
- human_decision

Human decisions:
- APROVAR PARA MONTAGEM
- REFAZER
- REJEITAR E USAR PIPELINE ATUAL

Approval only unlocks editing. It never unlocks publication.

## 8. Technical validation

The validator checks:
- readable video stream;
- vertical orientation;
- minimum 720x1280 input;
- 3–5 s target / max-normal 6 s contract;
- duration hard range;
- fps;
- codec discovery;
- unexpected audio;
- sampled black frames;
- sampled motion/freeze;
- SHA-256 duplicates;
- cross-topic duplicate animation;
- zero cost;
- rights/commercial-use declaration;
- download eligibility;
- watermark declaration;
- current public capability blocker.

Input may be normalized to 1080x1920 / 30 fps only after approval.

## 9. Editorial validation

Fail closed on:
- image/narration mismatch;
- discontinuity;
- physical incoherence;
- scientific/historical fidelity failure;
- deformed anatomy/characters;
- generated/broken text;
- watermark;
- rights uncertainty;
- payment/credits;
- duplicate animation.

## 10. Timeline integration

An approved asset is normalized with the existing FFmpeg runtime to:
- 1080x1920;
- 30 fps;
- H.264;
- yuv420p;
- original audio stripped by default.

The pilot does not mutate an active VSA timeline. It emits a timeline patch with:
- scene_id;
- normalized asset;
- SHA-256;
- narration excerpt;
- main verb;
- action-sync rule;
- transitions;
- safe-area note;
- preview_required=true;
- final_qa_required=true;
- publication_allowed=false.

This avoids duplicating the active VSA renderer.

## 11. States

Normal:
- draft_visual_plan
- awaiting_manual_generation
- asset_received
- technical_validation
- editorial_review
- approved_for_editing
- integrated_into_timeline
- preview_rendered
- final_qa
- ready_for_human_approval

Failure:
- rejected_watermark
- rejected_low_quality
- rejected_inaccurate
- rejected_discontinuity
- rejected_duplicate_animation
- rejected_rights
- rejected_cost
- returned_for_regeneration
- fallback_to_current_pipeline

## 12. Mandatory fallback

ZSky and Steve AI are optional.

Any blocker returns the scene to current_pipeline. The external tools are not allowed to become a production dependency.

## 13. Example ZSky prompt

Topic: Leidenfrost effect.

Create a vertical 9:16, five-second educational documentary clip. Show a macro scientific view of a water droplet touching a very hot metal surface. The lower layer of water must visibly vaporize first, forming a thin physically plausible vapor cushion between liquid and metal. Start with the droplet nearly touching the surface; show the vapor layer forming progressively; end with a clearly visible gap and the droplet supported above the metal. Use a gentle side macro camera move. No text, captions, logos, interface, watermark added to the composition, talking presenter, impossible motion or unrelated elements. Keep the central-lower caption area clear. This is an educational reconstruction, not authentic documentary footage.

## 14. Example Steve AI prompt

Topic: Leidenfrost effect with Léo.

Create a four-second vertical 9:16 premium 2D educational explainer. Léo is an illustrated silent character and does not lip-sync. He points to two simple visual states: on the left, a droplet touching hot metal directly; on the right, the same droplet separated from the metal by a visible vapor layer. Animate the transition so the viewer understands that the vapor layer reduces direct contact. No presenter, no talking avatar, no embedded text, no logo, no interface, no deformed character, no random scene changes. Preserve the central-lower caption safe area.

## 15. Safety invariants

This pilot contains no:
- external API call to ZSky/Steve;
- browser automation;
- credential handling;
- paid call;
- credit purchase;
- watermark removal;
- Metricool mutation;
- YouTube mutation;
- auto merge;
- auto publication.

Current publication routes remain unchanged.
