import importlib.util
import hashlib
import json
import pathlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

ROOT=pathlib.Path(__file__).resolve().parents[2]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
r=load('renderer','production/vsa/pilots/oct13_triple/render_oct13_triple.py')
v=load('validator','scripts/vsa/validate_release_receipt.py')
c=load('compliance','scripts/vsa/check_workflow_compliance.py')

class NarrationTests(unittest.TestCase):
    def exercise(self,case,bundle=False):
        with tempfile.TemporaryDirectory() as td:
            target=pathlib.Path(td)/'voice.mp3';target.write_bytes(b'stale')
            source=pathlib.Path(td)/'source.mp3';source.write_bytes(b'audio')
            key=hashlib.sha256(json.dumps([r.VOICE,'-2%','fala'],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
            entry={'voice':r.VOICE,'rate':'-2%','text':'fala','file':'source.mp3','sha256':r.sha(source)}
            if case=='hash':entry['sha256']='0'*64
            if case=='identity':entry['text']='outra fala'
            if case=='traversal':entry['file']='../outside.mp3'
            manifest=pathlib.Path(td)/'bundle.json';manifest.write_text(json.dumps({'clips':{key:entry}}))
            calls=[]
            def run(args,**kwargs):
                calls.append(args)
                if args[0]=='edge-tts':
                    if case=='timeout':raise subprocess.TimeoutExpired(args,60)
                    pathlib.Path(args[-1]).write_bytes(b'' if case=='empty' else b'audio')
                    return SimpleNamespace(returncode=1 if case in ('403','failed','tls') else 0,stderr='WSServerHandshakeError: 403' if case=='403' else 'SSLCertVerificationError' if case=='tls' else 'unavailable')
                if case=='decode':raise subprocess.CalledProcessError(1,args)
                return SimpleNamespace(returncode=0,stderr='max_volume: -inf dB' if case=='silent' else 'max_volume: -10.0 dB')
            with patch.dict(r.os.environ,{'VSA_NARRATION_BUNDLE':str(manifest)} if bundle else {},clear=True),patch.object(r.subprocess,'run',side_effect=run),patch.object(r,'duration',return_value=float('nan') if case=='invalid' else 4.):
                if case=='success':r.synthesize_narration('fala','-2%',target)
                else:
                    with self.assertRaises(RuntimeError):r.synthesize_narration('fala','-2%',target)
            self.assertEqual(target.exists(),case=='success')
            self.assertFalse(target.with_name('voice.partial.mp3').exists())
            self.assertLessEqual(sum(c[0]=='edge-tts' for c in calls),1)
            if bundle:self.assertFalse(any(c[0]=='edge-tts' for c in calls))
    def test_provider_failures(self):
        for case in ('403','tls','failed','timeout','empty','invalid','decode','silent','success'):
            with self.subTest(case=case):self.exercise(case)
    def test_bundle_fail_closed(self):
        for case in ('hash','identity','traversal','decode','success'):
            with self.subTest(case=case):self.exercise(case,True)

class AcquisitionTests(unittest.TestCase):
    def test_real_audio_decode_and_silence_gate(self):
        import shutil
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):self.skipTest('FFmpeg not installed')
        with tempfile.TemporaryDirectory() as td:
            for name,source,valid in [('tone','sine=frequency=440:duration=0.5',True),('silence','anullsrc=r=48000:cl=mono',False)]:
                audio=pathlib.Path(td)/(name+'.wav')
                subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i',source,'-t','0.5',str(audio)],check=True)
                if valid:self.assertGreater(r.validate_narration_audio(audio),0)
                else:
                    with self.assertRaisesRegex(RuntimeError,'SILENT'):r.validate_narration_audio(audio)
    def test_interrupted_download_discards_stale_and_partial(self):
        with tempfile.TemporaryDirectory() as td:
            target=pathlib.Path(td)/'video.mp4';target.write_bytes(b'stale')
            response=SimpleNamespace(raise_for_status=lambda:None)
            def chunks(_):yield b'partial';raise OSError('interrupted')
            response.iter_content=chunks
            from contextlib import nullcontext
            with patch.object(r.requests,'get',return_value=nullcontext(response)):
                with self.assertRaises(OSError):r.dl('https://example.invalid',target)
            self.assertFalse(target.exists());self.assertFalse(target.with_name('video.mp4.partial').exists())

class ReleaseTests(unittest.TestCase):
    def test_workflow_guard_rejects_fake_gate(self):
        workflow=pathlib.Path('.github/workflows/vsa-oct13-triple.yml')
        text=(ROOT/workflow).read_text()
        for mutation in ('comment','swallowed','missing_self_test'):
            candidate=text
            if mutation=='comment':candidate=candidate.replace('python scripts/vsa/validate_release_receipt.py','echo scripts/vsa/validate_release_receipt.py')+'\n# ./.github/actions/vsa-release-gate\n'
            if mutation=='swallowed':candidate=candidate.replace('--master "$OUT/$slug/VSA_${slug}_OCT13.mp4"','--master "$OUT/$slug/VSA_${slug}_OCT13.mp4" || true')
            if mutation=='missing_self_test':candidate=candidate.replace('--self-test','--not-self-test')
            with patch.object(pathlib.Path,'read_text',return_value=candidate):self.assertTrue(c.check(workflow))
        with patch.object(pathlib.Path,'read_text',return_value=text):self.assertEqual(c.check(workflow),[])
    def test_render_cannot_self_certify(self):
        policy=json.loads((ROOT/'config/vsa/VSA_VISUAL_STORY_ENGINE_V1.json').read_text())
        with tempfile.TemporaryDirectory() as td:
            master=pathlib.Path(td)/'master.mp4';master.write_bytes(b'test')
            with patch.object(r,'duration',return_value=50):
                receipt=r.receipt(r.TOPICS['pendulo_newton'],{'slug':'pendulo_newton'},master,[],[])
            self.assertFalse(receipt['release_eligible'])
            self.assertEqual(receipt['release_token']['status'],'PENDING_QA')
            self.assertFalse(any(receipt['gates'].values()))
            self.assertIn('SCHEDULER_RELEASE_TOKEN_FAIL',v.validate_receipt(policy,receipt,master))
    def test_duration_boundaries(self):
        for value in (44.9,55.1,float('nan'),float('inf')):
            with self.assertRaises(RuntimeError):r.require_duration('test',value)
        for value in (45,55):r.require_duration('test',value)
    def test_narration_preflight_blocks_long_content(self):
        with tempfile.TemporaryDirectory() as td,patch.object(r,'synthesize_narration'),patch.object(r,'duration',return_value=10):
            with self.assertRaisesRegex(RuntimeError,'DURATION_PREFLIGHT_FAIL'):
                r.prepare_narration('test',r.TOPICS['pendulo_newton'],pathlib.Path(td))

if __name__=='__main__':unittest.main()
