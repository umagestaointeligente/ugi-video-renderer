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
# A release job must carry QA + rights proof.
with tempfile.TemporaryDirectory() as td:
    job=Path(td)/'job.json'
    job.write_text(json.dumps({
        'channel':'VSA','title':'test','script':'ok','semantic_map':'PASS','rights_manifest':'PASS',
        'base_video_qa':'PASS','final_qa':'PASS','social_account_id':88527,
        'write_paths':['exports/vsa/test.mp4']
    }),encoding='utf-8')
    run(['validate-job','--job',str(job)])

print(json.dumps({'status':'PASS','suite':'VSA_ISOLATION_V1','cena_certa_untouched_by_design':True}))
