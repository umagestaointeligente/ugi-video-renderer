#!/usr/bin/env python3
import json, hashlib, sys
from pathlib import Path
p=Path('config/ugi/growth-policy.json')
d=json.loads(p.read_text(encoding='utf-8'))
required=['schema_version','policy_id','north_star','pre_generation_inputs','platform_independence','tiktok','instagram','youtube','creative_novelty','commerce_gate','publication_evidence','experiment_loop','lifecycle_events']
missing=[k for k in required if k not in d]
if missing: raise SystemExit('GROWTH_POLICY_FAIL missing='+','.join(missing))
assert d['policy_id']=='ugi-growth-engine'
assert d['north_star']['organic_views_per_content_platform']==10000
assert d['platform_independence']['enabled'] is True
assert d['commerce_gate']['fail_closed'] is True
assert d['publication_evidence']['verified_requires_readback'] is True
sha=hashlib.sha256(p.read_bytes()).hexdigest()
print('GROWTH_POLICY_LOADED=true')
print('GROWTH_POLICY_ID='+d['policy_id'])
print('GROWTH_POLICY_SHA256='+sha)
print('GROWTH_TARGET_VIEWS='+str(d['north_star']['organic_views_per_content_platform']))
print('GROWTH_RUNTIME_GATE=PASS')
