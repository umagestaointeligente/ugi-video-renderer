#!/usr/bin/env python3
import json, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RT=ROOT/'ops'/'vsa-runtime'/'runtime.py'

def run(args, expect=0):
    p=subprocess.run([sys.executable,str(RT),*args],text=True,capture_output=True,cwd=ROOT)
    if p.returncode!=expect:
        raise AssertionError(f"expected {expect}, got {p.returncode}: {p.stdout} {p.stderr}")
    return p

# VSA target must pass.
run(['preflight','--channel','VSA','--account-id','88527','--write-path','canonical/vsa/v1/output.json'])
# Cena Certa accounts and paths must fail closed.
run(['preflight','--channel','VSA','--account-id','88240'],2)
run(['preflight','--channel','VSA','--write-path','canonical/cena-certa/should-never-write.json'],2)
run(['preflight','--channel','Cena Certa'],2)

# A normal release job must carry topic + rights + QA + thematic music + real-footage proof.
with tempfile.TemporaryDirectory() as td:
    job=Path(td)/'job.json'
    payload={
        'channel':'VSA',
        'content_id':'VSA-RUNTIME-TEST-UNIQUE',
        'title':'test',
        'script':'ok',
        'semantic_map':'PASS',
        'semantic_topic_id':'runtime_test_unique_topic',
        'publish_date_local':'2026-09-10',
        'rights_manifest':'PASS',
        'base_video_qa':'PASS',
        'final_qa':'PASS',
        'topic_history_gate':'PASS',
        'music_track_title':'Classical vibes 4',
        'music_artist_or_composer':'Grigoriy Nuzhny',
        'music_source':'Mixkit',
        'music_license_or_usage_basis':'Mixkit Stock Music Free License',
        'music_editorial_class':'science_documentary',
        'music_form':'documentary film score',
        'music_has_vocals':False,
        'music_composition_gate':'PASS',
        'music_theme_match_gate':'PASS',
        'music_audibility_gate':'PASS',
        'music_no_tone_or_game_style_gate':'PASS',
        'music_rights_gate':'PASS',
        'real_footage_applicability':'REQUIRED',
        'real_footage_gate':'PASS',
        'real_footage_block_count':3,
        'distinct_real_clip_count':2,
        'social_account_id':88527,
        'write_paths':['exports/vsa/test.mp4']
    }
    job.write_text(json.dumps(payload),encoding='utf-8')
    run(['validate-job','--job',str(job)])

    # Missing music metadata/gates must block.
    bad_music_missing=Path(td)/'bad-music-missing.json'
    p=dict(payload); p.pop('music_track_title')
    bad_music_missing.write_text(json.dumps(p),encoding='utf-8')
    run(['validate-job','--job',str(bad_music_missing)],2)

    # Tone/game-like substitutes are forbidden.
    bad_music_tone=Path(td)/'bad-music-tone.json'
    p=dict(payload, music_form='sine_wave_bed')
    bad_music_tone.write_text(json.dumps(p),encoding='utf-8')
    run(['validate-job','--job',str(bad_music_tone)],2)

    bad_music_gate=Path(td)/'bad-music-gate.json'
    p=dict(payload, music_theme_match_gate='FAIL')
    bad_music_gate.write_text(json.dumps(p),encoding='utf-8')
    run(['validate-job','--job',str(bad_music_gate)],2)

    bad_music_vocals=Path(td)/'bad-music-vocals.json'
    p=dict(payload, music_has_vocals=True)
    bad_music_vocals.write_text(json.dumps(p),encoding='utf-8')
    run(['validate-job','--job',str(bad_music_vocals)],2)

    # Real footage alternation is fail-closed for observable topics.
    bad_footage_missing=Path(td)/'bad-footage-missing.json'
    p=dict(payload); p.pop('real_footage_applicability')
    bad_footage_missing.write_text(json.dumps(p),encoding='utf-8')
    run(['validate-job','--job',str(bad_footage_missing)],2)

    bad_footage_blocks=Path(td)/'bad-footage-blocks.json'
    p=dict(payload, real_footage_block_count=2)
    bad_footage_blocks.write_text(json.dumps(p),encoding='utf-8')
    run(['validate-job','--job',str(bad_footage_blocks)],2)

    bad_footage_distinct=Path(td)/'bad-footage-distinct.json'
    p=dict(payload, distinct_real_clip_count=1)
    bad_footage_distinct.write_text(json.dumps(p),encoding='utf-8')
    run(['validate-job','--job',str(bad_footage_distinct)],2)

    abstract=Path(td)/'abstract.json'
    p=dict(payload, content_id='VSA-RUNTIME-ABSTRACT', real_footage_applicability='NOT_APPLICABLE', real_footage_not_applicable_reason='No directly observable subject exists; explanation is intrinsically abstract.')
    abstract.write_text(json.dumps(p),encoding='utf-8')
    run(['validate-job','--job',str(abstract)])

    # Missing 60-day topic gate must block.
    bad=Path(td)/'bad-topic.json'
    p=dict(payload); p.pop('topic_history_gate')
    bad.write_text(json.dumps(p),encoding='utf-8')
    run(['validate-job','--job',str(bad)],2)

    # A known semantic topic repeated inside 60 days must fail closed.
    repeat=Path(td)/'repeat.json'
    repeat_payload=dict(payload, content_id='VSA-RUNTIME-REPEAT', semantic_topic_id='lightning_tree_internal_explosion', publish_date_local='2026-09-10')
    repeat.write_text(json.dumps(repeat_payload),encoding='utf-8')
    run(['validate-job','--job',str(repeat)],2)

    # A materially new event may pass only with the complete exception manifest.
    exception=Path(td)/'repeat-exception.json'
    exception_payload=dict(repeat_payload, repeat_exception=True, repeat_exception_reason='material new event for deterministic gate test', new_event_source='https://example.com/new-event', new_event_date='2026-09-10')
    exception.write_text(json.dumps(exception_payload),encoding='utf-8')
    run(['validate-job','--job',str(exception)])

    # PERSON_PROFILE requires actual person video, not a still/proxy.
    person=Path(td)/'person.json'
    person_payload=dict(payload, content_id='VSA-RUNTIME-PERSON', content_class='PERSON_PROFILE', person_visual_reference_gate='PASS', person_real_video_segments_gate='PASS', person_real_video_segment_count=2)
    person.write_text(json.dumps(person_payload),encoding='utf-8')
    run(['validate-job','--job',str(person)])

    person_still_only=Path(td)/'person-still-only.json'
    p=dict(person_payload, person_real_video_segment_count=1)
    person_still_only.write_text(json.dumps(p),encoding='utf-8')
    run(['validate-job','--job',str(person_still_only)],2)

    person_na=Path(td)/'person-na.json'
    p=dict(person_payload, real_footage_applicability='NOT_APPLICABLE', real_footage_not_applicable_reason='attempted bypass')
    person_na.write_text(json.dumps(p),encoding='utf-8')
    run(['validate-job','--job',str(person_na)],2)

# Direct pre-production topic check must block known repeat and pass a new topic.
run(['check-topic','--semantic-topic-id','runtime_test_unique_topic_2','--content-id','VSA-CHECK-NEW','--publish-date-local','2026-09-10'])
run(['check-topic','--semantic-topic-id','rocket_exhaust_spiral_sky','--content-id','VSA-CHECK-REPEAT','--publish-date-local','2026-09-10'],2)

print(json.dumps({
    'status':'PASS',
    'suite':'VSA_ISOLATION_V5_REAL_FOOTAGE_GATE',
    'topic_lock_days':60,
    'semantic_ledger_gate':True,
    'breaking_exception_manifest_gate':True,
    'person_reference_gate':True,
    'person_real_video_segments_gate':True,
    'real_footage_alternation_gate':True,
    'minimum_real_footage_blocks':3,
    'minimum_distinct_real_clips':2,
    'music_real_composition_gate':True,
    'music_theme_match_gate':True,
    'music_audibility_gate':True,
    'music_no_tone_or_game_style_gate':True,
    'music_rights_gate':True,
    'cena_certa_untouched_by_design':True
}))
