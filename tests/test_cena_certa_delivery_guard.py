import copy, importlib.util, json, os, pathlib, sys, tempfile, unittest, subprocess, shutil
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import cena_certa_delivery_guard as guard
import cena_certa_oct13_compile as compiler
import cena_certa_oct13_pack as pack
pack.EDITORIAL=ROOT/'ops/cena-certa-oct13/editorial-v2-9-proposed.json'

class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.out=pathlib.Path(self.tmp.name);self.env={'GITHUB_SHA':'a'*40,'GITHUB_RUN_ID':'1','GITHUB_RUN_ATTEMPT':'2'}
        self.manifest={'items':[]};self.summary={'commit':'a'*40,'run_id':'1','run_attempt':'2','items':[], 'history_fingerprint_coverage':1.,'history_eligible_media':10}
        for i in range(12):
            x={'id':f'FIXTURE_{i}','network':['tiktok','instagram','youtube','facebook'][i//3],'slot':str(i),'title':str(i),'source':'https://example.com/media.mp4','source_id':str(i),'segments':[[0,12]]}
            self.manifest['items'].append(x)
            p=self.out/x['network']/(x['id']+'.mp4');p.parent.mkdir(exist_ok=True);p.write_bytes(b'synthetic fixture bytes')
            self.summary['items'].append({**x,'sha256':guard.digest(p),'gates':{k:True for k in guard.CONTENT_GATES+guard.MEASURED_GATES}})
    def validate(self): return guard.validate_delivery(self.out,self.summary,self.manifest,self.env)
    def test_valid_delivery(self): self.assertTrue(self.validate())
    def test_hash_mutation(self):
        (self.out/'tiktok/FIXTURE_0.mp4').write_bytes(b'changed')
        with self.assertRaisesRegex(RuntimeError,'SHA_FAIL'):self.validate()
    def test_provenance(self):
        for key in ['commit','run_id','run_attempt']:
            with self.subTest(key=key):
                s=copy.deepcopy(self.summary);s[key]='wrong'
                with self.assertRaisesRegex(RuntimeError,'PROVENANCE'):guard.validate_delivery(self.out,s,self.manifest,self.env)
    def test_missing_all_required_gates(self):
        for gate in guard.CONTENT_GATES+guard.MEASURED_GATES:
            with self.subTest(gate=gate):
                s=copy.deepcopy(self.summary);s['items'][0]['gates'].pop(gate)
                with self.assertRaisesRegex(RuntimeError,'GATE_MISSING'):guard.validate_delivery(self.out,s,self.manifest,self.env)
    def test_string_true_not_boolean(self):
        self.summary['items'][0]['gates']['CTA_FINAL_PASS']='true'
        with self.assertRaisesRegex(RuntimeError,'GATE_MISSING'):self.validate()
    def test_extra_master(self):
        (self.out/'tiktok/extra.mp4').write_bytes(b'unknown')
        with self.assertRaisesRegex(RuntimeError,'UNEXPECTED'):self.validate()
    def test_duplicate_id(self):
        self.summary['items'][1]['id']=self.summary['items'][0]['id']
        with self.assertRaisesRegex(RuntimeError,'ITEM_SET'):self.validate()
    def test_manifest_drift(self):
        self.summary['items'][0]['source']='https://example.com/other.mp4'
        with self.assertRaisesRegex(RuntimeError,'MANIFEST_DRIFT'):self.validate()
    def test_review_requires_same_sha(self):
        review={'reviewer':'fixture reviewer','manifest_sha256':'b'*64,'items':{x['id']:{'sha256':x['sha256'],'gates':{k:True for k in guard.CONTENT_GATES}} for x in self.summary['items']}}
        guard.validate_review(self.summary,review,'b'*64)
        review['items']['FIXTURE_0']['sha256']='wrong'
        with self.assertRaisesRegex(RuntimeError,'QA_SHA'):guard.validate_review(self.summary,review,'b'*64)
    def test_review_requires_exact_items(self):
        with self.assertRaisesRegex(RuntimeError,'ITEM_SET'):guard.validate_review(self.summary,{'reviewer':'fixture','manifest_sha256':'b'*64,'items':{}},'b'*64)

class CompilerPreventionTests(unittest.TestCase):
    def doc(self):
        doc=json.loads((ROOT/'ops/cena-certa-oct13/editorial-v2-9-proposed.json').read_text())
        for i,x in enumerate(doc['items']):
            d=(x['target_duration_sec']['min']+x['target_duration_sec']['max'])/2
            x.update(source_url=f'https://example.com/{i}.mp4',source_id=f'FIXTURE_{i}',source_segments=[[0,d]],media_type='LIVE_ACTION',rights_evidence={'status':'VERIFIED','scope':'SOCIAL_REPUBLISH','proof_url':'https://example.com/license'})
        return doc
    def test_duplicate_id(self):
        d=self.doc();d['items'][1]['id']=d['items'][0]['id'];self.assertIn('ITEM_ID_INVALID_OR_DUPLICATE',str(compiler.compile_editorial(d)[1]))
    def test_path_escape(self):
        d=self.doc();d['items'][0]['id']='../../escape';self.assertIn('ITEM_ID_INVALID',str(compiler.compile_editorial(d)[1]))
    def test_source_collision(self):
        d=self.doc();d['items'][1]['source_id']=d['items'][0]['source_id'];self.assertIn('URL_COLLISION',str(compiler.compile_editorial(d)[1]))
    def test_nan_target(self):
        d=self.doc();d['items'][0]['target_duration_sec']['min']=float('nan');self.assertIsNone(compiler.compile_editorial(d)[0])
    def test_bad_clock(self):
        d=self.doc();d['items'][0]['slot']='2026-10-13T99:99:00-03:00';self.assertIsNone(compiler.compile_editorial(d)[0])
    def test_complete_input_drift(self):
        d=self.doc();items=compiler.compile_editorial(d)[0]['items'];items[0]['source']='https://example.com/changed.mp4'
        with patch.object(pathlib.Path,'read_text',return_value=json.dumps(d)),self.assertRaisesRegex(RuntimeError,'COMPILED_INPUT_DRIFT'):pack.editorial_alignment_gate(items)

class HistoryTests(unittest.TestCase):
    def doc(self,n=5):return {'generated_at':datetime.now(timezone.utc).isoformat(),'items':[{'status':'PUBLISHED','media':f'https://example.com/{i}.mp4'} for i in range(n)]}
    def test_empty(self):
        with patch.object(pathlib.Path,'read_text',return_value=json.dumps(self.doc(0))),self.assertRaisesRegex(RuntimeError,'EMPTY'):pack.history_index()
    def test_eighty_percent(self):
        def hs(url,*a):return [] if url.endswith('4.mp4') else [1]*24
        with patch.object(pathlib.Path,'read_text',return_value=json.dumps(self.doc())),patch.object(pack,'duration',return_value=12),patch.object(pack,'dhashes_center',side_effect=hs),self.assertRaisesRegex(RuntimeError,'COVERAGE'):pack.history_index()
    def test_partial_decode(self):
        with patch.object(pathlib.Path,'read_text',return_value=json.dumps(self.doc())),patch.object(pack,'duration',return_value=12),patch.object(pack,'dhashes_center',return_value=[1]*3),self.assertRaisesRegex(RuntimeError,'COVERAGE'):pack.history_index()
    def test_stale(self):
        d=self.doc();d['generated_at']=(datetime.now(timezone.utc)-timedelta(days=2)).isoformat()
        with patch.object(pathlib.Path,'read_text',return_value=json.dumps(d)),self.assertRaisesRegex(RuntimeError,'STALE'):pack.history_index()
    def test_full(self):
        with patch.object(pathlib.Path,'read_text',return_value=json.dumps(self.doc())),patch.object(pack,'duration',return_value=12),patch.object(pack,'dhashes_center',return_value=[1]*24):self.assertEqual(pack.history_index()[1],1.)
    def test_truncated_source(self):
        with self.assertRaisesRegex(RuntimeError,'TRUNCATED'):pack.normalized_segments({'id':'x','segments':[[0,20]]},15)

@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg unavailable')
class RealMediaTests(unittest.TestCase):
    def test_real_h264_aac_master_passes_measurements(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'fixture.mp4'
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','testsrc2=size=1080x1920:rate=30','-f','lavfi','-i','sine=frequency=440:sample_rate=48000','-t','12','-c:v','libx264','-threads','2','-preset','ultrafast','-crf','32','-pix_fmt','yuv420p','-c:a','aac','-y',str(p)],check=True,capture_output=True)
            pack.validate_master(p)
    def test_detector_failure_is_not_pass(self):
        probe={'streams':[{'codec_type':'video','codec_name':'h264','width':1080,'height':1920,'pix_fmt':'yuv420p','avg_frame_rate':'30/1'},{'codec_type':'audio','codec_name':'aac','sample_rate':'48000'}]}
        with patch.object(pack,'probe',return_value=probe),patch.object(pack,'run',side_effect=RuntimeError('DETECTOR_FAILURE')) as r:
            with self.assertRaisesRegex(RuntimeError,'DETECTOR_FAILURE'):pack.validate_master('fixture')
            self.assertTrue(r.call_args.kwargs['check'])

if __name__=='__main__':unittest.main()
