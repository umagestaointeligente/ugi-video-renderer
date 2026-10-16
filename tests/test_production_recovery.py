import copy
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import cena_certa_oct13_compile as c
import cena_certa_oct13_pack as p
import ugi_render_manifest as u

class RecoveryTests(unittest.TestCase):
    def test_new_date_is_supported_without_changing_historical_contract(self):
        doc=json.loads((ROOT/'ops/cena-certa-oct13/editorial-v2-9-proposed.json').read_text())
        doc['publication_date']='2026-10-16'
        for row in doc['items']:row['slot']=row['slot'].replace('2026-10-13','2026-10-16')
        _,old_errors=c.compile_editorial(doc)
        _,new_errors=c.compile_editorial(doc,expected_date='2026-10-16')
        self.assertTrue(any('SCOPE_DATE' in e for e in old_errors))
        self.assertFalse(any('SCOPE_DATE' in e or 'SLOT_INVALID' in e for e in new_errors))
    def test_recent_does_not_mean_only_2025(self):
        doc=json.loads((ROOT/'ops/cena-certa-oct13/editorial-v2-9-proposed.json').read_text())
        doc['items'][0]['title']='Aclamado (2004)'
        _,errors=c.compile_editorial(doc)
        self.assertFalse(any('YEAR' in x or 'ONLY_2025' in x for x in errors))
        doc['items'][0]['title']='Antigo (1989)'
        self.assertTrue(any('YEAR' in x for x in c.compile_editorial(doc)[1]))
    def test_unsupported_and_truncated_windows_block(self):
        for end in (31,float('nan'),float('inf')):
            with self.assertRaises(RuntimeError):p.normalized_segments({'id':'x','segments':[[0,end]]},30)
        self.assertEqual(p.normalized_segments({'id':'x','segments':[[0,30]]},30),[(0,30)])
    def test_local_intake_requires_real_hash_and_containment(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td);source=root/'media.mp4';source.write_bytes(b'not-video')
            with patch.object(p,'ROOT',root):
                for item in ({'source_file':'../escape.mp4'},{'source_file':'media.mp4','source_sha256':'0'*64}):
                    with self.assertRaises(RuntimeError):p.download_source(dict(source_id='test',**item),{})
    def test_tls_failure_is_terminal_without_disabling_validation(self):
        self.assertEqual(p.permanent_source_failure(RuntimeError('CERTIFICATE_VERIFY_FAILED')),'SOURCE_TLS_CERTIFICATE_FAIL')
        text=(ROOT/'scripts/cena_certa_oct13_pack.py').read_text()
        self.assertIn('"no-certifi"',text)
        self.assertNotIn('--no-check-certificates',text)
    def test_ugi_cannot_render_changed_source_or_narration(self):
        doc=json.loads((ROOT/'ops/production/baselines/ugi-oct07-replay.json').read_text())
        for field in ('source_sha256','narration_sha256','text_sha256'):
            row=copy.deepcopy(doc['items'][0]);row[field]='0'*64
            with tempfile.TemporaryDirectory() as td, self.assertRaisesRegex(ValueError,'MISMATCH'):
                u.render(row,pathlib.Path(td))
    def test_ugi_output_cannot_escape_checkout(self):
        with self.assertRaises(ValueError):u.local('../missing')

if __name__=='__main__':unittest.main()
