import copy, hashlib, json, sys, tempfile, unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from cena_certa_render_evidence_guard import CONTRACT, LAYERS, POSITIONS
from cena_certa_oct02_evidence import reconcile, NETWORKS

class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.history={'items':[]}
        self.execution=dict(run_id='123',run_attempt='1',head_sha='a'*40,job_id='render-and-gate')
        self.summary={'items':[]}; self.receipts={}; now=datetime.now(timezone.utc)
        for network in sorted(NETWORKS):
            ident='CC-'+network; data=network.encode(); (self.root/(ident+'.mp4')).write_bytes(data)
            sha=hashlib.sha256(data).hexdigest()
            item=dict(id=ident,network=network,sha256=sha,technical_status='PASS',source_id=network,source=network,source_start_sec=0,source_end_sec=30,execution=self.execution)
            self.summary['items'].append(item)
            self.receipts[ident]=dict(contract=CONTRACT,content_id=ident,master_sha256=sha,checked_at=now.isoformat(),execution=self.execution,
                source=dict(extracted_id=network,url=network,identity_pass=True,metadata_receipt='test-only'),
                rights=dict(status='PASS',evidence='test-only'),transformation=dict(status='PASS',evidence='test-only'),cta=dict(status='PASS',evidence='test-only'),
                visual=dict(status='PASS',evidence='test-only',exact_subject_match=True,source_cta_removed=True,frames={p:'test-only' for p in POSITIONS}),
                anti_repeat=dict(status='PASS',history_complete=True,history_receipt='test-only',history_start=(now-timedelta(days=60)).isoformat(),history_end=now.isoformat(),comparison_layers=list(LAYERS),fingerprint_receipt='test-only',scene_overlap_detected=False,reservation_history_sha256=hashlib.sha256(json.dumps(self.history,sort_keys=True).encode()).hexdigest()))
    def result(self):
        return reconcile(self.summary,self.receipts,self.root,self.history,self.execution)
    def test_complete_fixture_passes_without_publication_clearance(self):
        r=self.result(); self.assertEqual(r['status'],'PASS'); self.assertEqual(r['publication_status'],'NOT_VERIFIED')
    def test_empty_receipts_block_all(self):
        self.receipts={}; r=self.result(); self.assertEqual(r['status'],'BLOCK'); self.assertTrue(all(i['status']=='BLOCK' for i in r['items']))
    def test_wrong_attempt_run_commit_and_job_block(self):
        for k in self.execution:
            saved=copy.deepcopy(self.receipts); self.receipts['CC-youtube']['execution']=dict(self.execution,**{k:'wrong'})
            self.assertEqual(self.result()['status'],'BLOCK'); self.receipts=saved
    def test_missing_network_blocks_batch(self):
        self.summary['items'].pop(); self.assertEqual(self.result()['status'],'BLOCK')
    def test_reencoded_overlapping_source_blocks(self):
        self.history['items']=[dict(source_id='youtube',source_start_sec=2,source_end_sec=20,sha256='f'*64,frame_fingerprint_sha256='e'*64)]
        self.assertIn('PRIOR_SCENE_RESERVATION:CC-youtube',self.result()['errors'])
    def test_changed_history_invalidates_receipt(self):
        self.history['revision']=2; self.assertEqual(self.result()['status'],'BLOCK')
    def test_replaced_file_blocks_all(self):
        (self.root/'CC-youtube.mp4').write_bytes(b'replaced'); self.assertTrue(all(r['status']=='BLOCK' for r in self.result()['items']))
    def test_missing_cta_blocks(self):
        self.receipts['CC-youtube'].pop('cta'); self.assertEqual(self.result()['status'],'BLOCK')
    def test_workflow_has_one_batch_gate_before_side_effects(self):
        s=(Path(__file__).resolve().parents[1]/'.github/workflows/cena-certa-oct02-pack.yml').read_text()
        self.assertNotIn('matrix:',s); self.assertNotIn('--clobber',s); self.assertNotIn('  push:',s)
        self.assertLess(s.index('cena_certa_oct02_evidence.py'),s.index('gh release create'))
        self.assertLess(s.index('cena_certa_oct02_evidence.py'),s.index('gh issue create'))
    def test_youtube_cta_and_technical_only_render(self):
        s=(Path(__file__).resolve().parents[1]/'scripts/cena_certa_oct02_pack.py').read_text()
        self.assertNotIn('cta and item["network"]!="youtube"',s); self.assertNotIn('"EDITORIAL_PASS":True',s); self.assertNotIn('check=False',s)

if __name__=='__main__': unittest.main()
