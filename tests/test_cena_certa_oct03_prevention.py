import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import cena_certa_oct03_pack as pack

class PreventionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for name,path in [('OUT',self.root/'out'),('WORK',self.root/'work'),
                          ('HISTORY',self.root/'history.json'),('ROOT',self.root),
                          ('MANIFEST',self.root/'manifest.json'),('ANTI',self.root/'anti.json')]:
            mock=patch.object(pack,name,path);mock.start();self.addCleanup(mock.stop)
        pack.PHASE='TEST';pack.CONTEXT={}
        self.env=patch.dict(os.environ,{'GITHUB_RUN_ID':'123','GITHUB_RUN_ATTEMPT':'1','GITHUB_SHA':'a'*40})
        self.env.start();self.addCleanup(self.env.stop)

    def test_403_is_not_retried_and_globo_has_no_youtube_variant(self):
        with patch.object(pack,'run',side_effect=RuntimeError('HTTP Error 403: Forbidden')) as run,patch.object(pack.time,'sleep') as sleep:
            with self.assertRaisesRegex(RuntimeError,'SOURCE_ACCESS_DENIED'):
                pack.download_source({'id':'candidate','source_id':'42','source':'https://globoplay.globo.com/v/42/'},{})
            self.assertEqual(run.call_count,1);sleep.assert_not_called()
            self.assertNotIn('--extractor-args',run.call_args.args[0])

    def test_missing_history_blocks_instead_of_accepting_80_percent(self):
        items=[dict(id=i,status='PUBLISHED',media=f'https://example.invalid/{i}.mp4') for i in range(10)]
        pack.HISTORY.write_text(json.dumps({'items':items}))
        with patch.object(pack,'dhashes',side_effect=lambda url,*a:[1,2,3] if '/9.' not in url else []):
            with self.assertRaisesRegex(RuntimeError,'HISTORY_FINGERPRINT_COVERAGE_FAIL:9/10'):
                pack.history_index()
        d=json.loads((pack.OUT/'diagnostic.json').read_text())
        self.assertEqual(d['missing'],[{'id':9,'network':None}]);self.assertEqual(d['status'],'BLOCKED')

    def test_empty_history_never_passes(self):
        pack.HISTORY.write_text('{"items":[]}')
        with self.assertRaisesRegex(RuntimeError,'HISTORY_FINGERPRINT_COVERAGE_FAIL'):pack.history_index()

    def test_repeat_stays_blocked_and_keeps_match_evidence(self):
        master=self.root/'master.mp4';master.write_bytes(b'fixture')
        with patch.object(pack,'dhashes',return_value=[7]*36):
            with self.assertRaisesRegex(RuntimeError,'SCENE_FINGERPRINT_REPEAT_FAIL'):
                pack.visual_gate([({'id':'CANDIDATE'},master)],[({'id':385523483,'network':'instagram'},[7]*50)])
        d=json.loads((pack.OUT/'diagnostic.json').read_text())
        self.assertEqual(d['scene_evidence']['best_history']['id'],385523483)
        self.assertEqual(d['scene_evidence']['threshold'],9)

    def test_execute_returns_failure_removes_stale_pass_and_binds_receipt(self):
        pack.OUT.mkdir();(pack.OUT/'summary.json').write_text('{"status":"PASS"}')
        with patch.object(pack,'main',side_effect=RuntimeError('source blocked')):
            self.assertEqual(pack.execute(),1)
        self.assertFalse((pack.OUT/'summary.json').exists())
        d=json.loads((pack.OUT/'diagnostic.json').read_text())
        self.assertEqual((d['run_id'],d['run_attempt'],d['commit']),('123','1','a'*40))

    def test_all_sources_preflight_before_first_render(self):
        items=[dict(id=f'item{i}',network=net,year=2023,source_id=str(i),source_start=0,source_end=36)
               for i,net in enumerate(['tiktok']*3+['instagram']*3+['youtube']*3+['facebook']*3)]
        pack.MANIFEST.write_text(json.dumps({'items':items}));pack.ANTI.write_text('{}')
        def download(item,cache):
            if item['id']=='item7':raise RuntimeError('SOURCE_ACCESS_DENIED')
            d=self.root/item['id'];d.mkdir();(d/'source.info.json').write_text(json.dumps({'id':item['source_id']}))
            return d/'source.mp4'
        with patch.object(pack,'history_index',return_value=([],1,10)),patch.object(pack,'download_source',side_effect=download),patch.object(pack,'duration',return_value=100),patch.object(pack,'render') as render,patch.object(pack,'download') as core:
            self.assertEqual(pack.execute(),1)
            render.assert_not_called();core.assert_not_called()

    def test_approval_cannot_move_between_runs_commits_or_attempts(self):
        receipt={'run_id':'123','run_attempt':'1','commit':'a'*40}
        self.assertTrue(pack.execution_receipt_matches(receipt))
        for key in receipt:
            changed=dict(receipt);changed[key]='other'
            self.assertFalse(pack.execution_receipt_matches(changed))
        self.assertFalse(pack.execution_receipt_matches({}))

    def test_source_identity_mismatch_is_not_retried(self):
        def download(*args,**kwargs):
            directory=pack.WORK/'sources'/'42'
            (directory/'source.info.json').write_text('{"id":"wrong"}')
        with patch.object(pack,'run',side_effect=download) as run,patch.object(pack.time,'sleep'):
            with self.assertRaisesRegex(RuntimeError,'SOURCE_IDENTITY_MISMATCH'):
                pack.download_source({'id':'candidate','source_id':'42','source':'https://globoplay.globo.com/v/42/'},{})
            self.assertEqual(run.call_count,1)

    def test_target_yaml_and_embedded_scripts_parse(self):
        for path in (ROOT/'.github/workflows').glob('cena-certa-*prevention.yml'):
            yaml.safe_load(path.read_text())
        for name in ('cena-certa-oct01-rights-discovery.yml','cena-certa-oct03-format-reset.yml'):
            d=yaml.safe_load((ROOT/'.github/workflows'/name).read_text())
            for job in d['jobs'].values():
                for step in job['steps']:
                    script=step.get('run')
                    if not script:continue
                    subprocess.run(['bash','-n'],input=script,text=True,check=True)
                    if "python - <<'PY'\n" in script:
                        compile(script.split("python - <<'PY'\n",1)[1].rsplit('\nPY',1)[0],name,'exec')

    def test_external_writes_follow_execution_guard(self):
        d=yaml.safe_load((ROOT/'.github/workflows/cena-certa-oct03-format-reset.yml').read_text())
        steps=d['jobs']['render-and-gate']['steps']
        guard=next(i for i,s in enumerate(steps) if s.get('name','').startswith('Verify execution-bound'))
        writes=[i for i,s in enumerate(steps) if 'gh release' in s.get('run','') or 'gh issue create' in s.get('run','')]
        self.assertTrue(writes and all(i>guard for i in writes))
        self.assertTrue(all('if' not in steps[i] for i in writes))

if __name__=='__main__':unittest.main()
