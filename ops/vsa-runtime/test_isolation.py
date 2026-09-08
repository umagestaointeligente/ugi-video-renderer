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

# A normal release job must carry semantic topic identity + history + QA + rights proof.
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
        'social_account_id':88527,
        'write_paths':['exports/vsa/test.mp4']
    }
    job.write_text(json.dumps(payload),encoding='utf-8')
    run(['validate-job','--job',str(job)])

    # Missing 60-day topic gate must block.
    bad=Path(td)/'bad-topic.json'
    payload_bad=dict(payload); payload_bad.pop('topic_history_gate')
    bad.write_text(json.dumps(payload_bad),encoding='utf-8')
    run(['validate-job','--job',str(bad)],2)

    # A known semantic topic repeated inside 60 days must fail closed.
    repeat=Path(td)/'repeat.json'
    repeat_payload=dict(
        payload,
        content_id='VSA-RUNTIME-REPEAT',
        semantic_topic_id='lightning_tree_internal_explosion',
        publish_date_local='2026-09-10'
    )
    repeat.write_text(json.dumps(repeat_payload),encoding='utf-8')
    run(['validate-job','--job',str(repeat)],2)

    # A materially new event may pass only with the complete exception manifest.
    exception=Path(td)/'repeat-exception.json'
    exception_payload=dict(
        repeat_payload,
        repeat_exception=True,
        repeat_exception_reason='material new event for deterministic gate test',
        new_event_source='https://example.com/new-event',
        new_event_date='2026-09-10'
    )
    exception.write_text(json.dumps(exception_payload),encoding='utf-8')
    run(['validate-job','--job',str(exception)])

    # PERSON_PROFILE requires direct visual reference to the real person.
    person=Path(td)/'person.json'
    person_payload=dict(payload, content_id='VSA-RUNTIME-PERSON', content_class='PERSON_PROFILE', person_visual_reference_gate='PASS')
    person.write_text(json.dumps(person_payload),encoding='utf-8')
    run(['validate-job','--job',str(person)])

    person_bad=Path(td)/'person-bad.json'
    person_bad_payload=dict(payload, content_id='VSA-RUNTIME-PERSON-BAD', content_class='PERSON_PROFILE')
    person_bad.write_text(json.dumps(person_bad_payload),encoding='utf-8')
    run(['validate-job','--job',str(person_bad)],2)

# Direct pre-production topic check must block known repeat and pass a new topic.
run(['check-topic','--semantic-topic-id','runtime_test_unique_topic_2','--content-id','VSA-CHECK-NEW','--publish-date-local','2026-09-10'])
run(['check-topic','--semantic-topic-id','rocket_exhaust_spiral_sky','--content-id','VSA-CHECK-REPEAT','--publish-date-local','2026-09-10'],2)

print(json.dumps({
    'status':'PASS',
    'suite':'VSA_ISOLATION_V3',
    'topic_lock_days':60,
    'semantic_ledger_gate':True,
    'breaking_exception_manifest_gate':True,
    'person_reference_gate':True,
    'cena_certa_untouched_by_design':True
}))
