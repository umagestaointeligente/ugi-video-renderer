#!/usr/bin/env python3
import json, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RT=ROOT/'ops'/'vsa-runtime'/'runtime.py'
MASK_SHA='ac8162ee849f154edf2519ef649f64cd470737df7b5ecbabb7085f72059cfd56'

def run(args, expect=0):
    p=subprocess.run([sys.executable,str(RT),*args],text=True,capture_output=True,cwd=ROOT)
    if p.returncode!=expect:
        raise AssertionError(f"expected {expect}, got {p.returncode}: {p.stdout} {p.stderr}")
    return p

# Exact VSA Metricool brand passes; other project brands and paths fail closed.
run(['preflight','--channel','VSA','--account-id','6935441','--write-path','canonical/vsa/v1/output.json'])
for bad in ('6809869','6935401','6945839'):
    run(['preflight','--channel','VSA','--account-id',bad],2)
run(['preflight','--channel','VSA','--write-path','canonical/cena-certa/should-never-write.json'],2)
run(['preflight','--channel','Cena Certa'],2)

with tempfile.TemporaryDirectory() as td:
    job=Path(td)/'job.json'
    payload={
        'channel':'VSA','social_account_id':6935441,
        'content_id':'VSA-RUNTIME-TEST-UNIQUE','title':'test','script':'ok','semantic_map':'PASS',
        'semantic_topic_id':'runtime_test_unique_topic','publish_date_local':'2026-09-14',
        'rights_manifest':'PASS','base_video_qa':'PASS','final_qa':'PASS','topic_history_gate':'PASS',
        'music_track_title':'Classical vibes 4','music_artist_or_composer':'Grigoriy Nuzhny',
        'music_source':'Mixkit','music_license_or_usage_basis':'Mixkit Stock Music Free License',
        'music_editorial_class':'science_documentary','music_form':'documentary film score','music_has_vocals':False,
        'music_composition_gate':'PASS','music_theme_match_gate':'PASS','music_audibility_gate':'PASS',
        'music_no_tone_or_game_style_gate':'PASS','music_rights_gate':'PASS',
        'real_footage_applicability':'REQUIRED','real_footage_gate':'PASS','real_footage_block_count':3,'distinct_real_clip_count':2,
        'mask_sha256':MASK_SHA,'clean_header_gate':'PASS','clean_cc_zone_gate':'PASS','single_title_render_gate':'PASS','canonical_mask_v2_gate':'PASS',
        'legacy_v1_body_shell_used':False,'header_cover_panel_used':False,
        'voice_profile':'pt-BR-AntonioNeural','voice_ptbr_neutral_gate':'PASS',
        'fresh_build':True,'prior_final_master_used':False,
        'pre_cta_contamination_gate':'PASS','legacy_or_unrelated_frame_before_cta':False,
        'final_master_qa_gate':'PASS','scheduler_release_token_gate':'PASS',
        'write_paths':['exports/vsa/test.mp4']
    }
    job.write_text(json.dumps(payload),encoding='utf-8')
    run(['validate-job','--job',str(job)])

    def blocked(name, **changes):
        p=dict(payload); p.update(changes); f=Path(td)/(name+'.json'); f.write_text(json.dumps(p),encoding='utf-8'); run(['validate-job','--job',str(f)],2)

    blocked('british-voice',voice_profile='en-GB-RyanNeural',voice_ptbr_neutral_gate='FAIL')
    blocked('wrong-mask',mask_sha256='0'*64)
    blocked('stale-master',fresh_build=False,prior_final_master_used=True)
    blocked('moon-tail',pre_cta_contamination_gate='FAIL',legacy_or_unrelated_frame_before_cta=True)
    blocked('release-token',scheduler_release_token_gate='FAIL')
    blocked('wrong-brand',social_account_id=6809869)

    person=dict(payload,content_id='VSA-RUNTIME-PERSON',content_class='PERSON_PROFILE',person_visual_reference_gate='PASS',person_real_video_segments_gate='PASS',person_real_video_segment_count=2,entity_integrity_gate='PASS')
    f=Path(td)/'person.json'; f.write_text(json.dumps(person),encoding='utf-8'); run(['validate-job','--job',str(f)])
    person_bad=dict(person,entity_integrity_gate='FAIL'); f=Path(td)/'person-bad.json'; f.write_text(json.dumps(person_bad),encoding='utf-8'); run(['validate-job','--job',str(f)],2)

run(['check-topic','--semantic-topic-id','runtime_test_unique_topic_2','--content-id','VSA-CHECK-NEW','--publish-date-local','2026-09-14'])

print(json.dumps({
  'status':'PASS','suite':'VSA_PREVENTIVE_METRICOOL_ISOLATION_V1',
  'metricool_brand_id':6935441,'youtube_channel_id':'UCm0UMO6lNWlr66YSIS1p4iQ',
  'voice_ptbr_gate':True,'mask_v2_gate':True,'fresh_build_gate':True,
  'pre_cta_contamination_gate':True,'entity_integrity_gate':True,
  'scheduler_release_token_gate':True,'cena_certa_untouched_by_design':True
}))
