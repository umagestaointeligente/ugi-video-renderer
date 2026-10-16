import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('e2e',ROOT/'scripts/production/e2e_render.py')
e2e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e2e)
worker_spec=importlib.util.spec_from_file_location('tts_worker',ROOT/'scripts/media/edge_tts_worker.py')
worker=importlib.util.module_from_spec(worker_spec);worker_spec.loader.exec_module(worker)

class RealMediaTests(unittest.TestCase):
 def test_missing_word_boundaries_cannot_create_captions(self):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td);(p/'words').write_text(json.dumps({'type':'SentenceBoundary','text':'Oi'}))
   with self.assertRaisesRegex(RuntimeError,'WORD_BOUNDARIES_MISSING'):e2e.word_captions(p/'words',p/'captions.ass')
 def test_captions_use_actual_offsets(self):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td);(p/'words').write_text('\n'.join(json.dumps({'type':'WordBoundary','offset':o,'duration':d,'text':t}) for o,d,t in [(12500000,2500000,'Olá'),(15000000,5000000,'gestão')]))
   self.assertEqual(e2e.word_captions(p/'words',p/'captions.ass'),1)
   self.assertIn('0:00:01.25,0:00:02.00', (p/'captions.ass').read_text())
 def test_failed_synthesis_cleans_partial_audio_and_metadata(self):
  async def fail(text,voice,rate,output,metadata):
   output.write_bytes(b'partial');metadata.write_text('partial');raise TimeoutError()
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td);audio=p/'a.mp3';metadata=p/'words'
   args=['worker','--voice','pt-BR-AntonioNeural','--text','Teste','--write-media',str(audio),'--write-metadata',str(metadata)]
   with patch.object(sys,'argv',args),patch.object(worker,'synthesize',fail):self.assertEqual(worker.main(),1)
   self.assertFalse(audio.exists());self.assertFalse(metadata.exists())
 def test_nonpublic_source_rejected_before_network(self):
  with tempfile.TemporaryDirectory() as td:
   for url in ['http://example.com/a','https://user:pass@example.com/a']:
    with self.assertRaisesRegex(ValueError,'PUBLIC_HTTPS_REQUIRED'):e2e.acquire(url,pathlib.Path(td)/'source.mp4')
 def test_missing_master_cannot_gain_technical_pass(self):
  with patch.object(e2e.cc,'validate_master',side_effect=RuntimeError('BROKEN_MASTER')):
   with self.assertRaisesRegex(RuntimeError,'BROKEN_MASTER'):e2e.verify_master(ROOT/'missing.mp4')

 def test_changed_master_cannot_enter_artifacts(self):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td);source=p/'master.mp4';source.write_bytes(b'changed')
   row={'file':'master.mp4','sha256':'0'*64}
   with patch.object(e2e,'ROOT',p),self.assertRaisesRegex(RuntimeError,'MASTER_CHANGED_AFTER_QA'):e2e.stage_deliverables([row],p)
   self.assertEqual(list((p/'deliverables').glob('*.mp4')),[])

if __name__=='__main__':unittest.main()
