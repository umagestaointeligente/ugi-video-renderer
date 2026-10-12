#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, importlib.util, json, pathlib, subprocess, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MOD_PATH = ROOT / "scripts/vsa/assisted_animation_stage.py"
REG_PATH = ROOT / "config/vsa/VSA_ASSISTED_ANIMATION_CAPABILITIES_V1.json"
spec = importlib.util.spec_from_file_location("assisted", MOD_PATH)
aa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aa)

class AssistedAnimationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REG_PATH.read_text(encoding="utf-8"))
        cls.td = tempfile.TemporaryDirectory()
        cls.tmp = pathlib.Path(cls.td.name)
        cls.motion = cls._video("motion.mp4",720,1280,True)
        cls.horizontal = cls._video("horizontal.mp4",1280,720,True)
        cls.lowres = cls._video("lowres.mp4",360,640,True)
        cls.static = cls._video("static.mp4",720,1280,False)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    @classmethod
    def _video(cls,name,w,h,motion):
        p=cls.tmp/name
        src = f"testsrc2=size={w}x{h}:rate=30:duration=3.2" if motion else f"color=c=blue:size={w}x{h}:rate=30:duration=3.2"
        subprocess.run(["ffmpeg","-y","-loglevel","error","-f","lavfi","-i",src,
                        "-c:v","libx264","-preset","ultrafast","-crf","30","-pix_fmt","yuv420p",p],check=True)
        return p

    def relaxed(self,tool="zsky"):
        r=copy.deepcopy(self.registry)
        if tool=="zsky":
            r["tools"]["zsky"]["free_output_fit_for_vsa_production"]=True
            r["tools"]["zsky"]["free_video_watermark_present"]=False
            r["tools"]["zsky"]["current_blocker"]=None
        if tool=="steve_ai":
            r["tools"]["steve_ai"]["free_output_fit_for_vsa_production"]=True
            r["tools"]["steve_ai"]["free_downloadable_video"]=True
            r["tools"]["steve_ai"]["commercial_use_free"]=True
            r["tools"]["steve_ai"]["current_blocker"]=None
        return r

    def req(self,**kw):
        d={"video_id":"teste","topic_title":"Teste VSA","narration_status":"approved",
           "approved_script":"A gota vaporizou ao tocar a superfície muito quente. Depois o vapor sustentou a gota e ela deslizou pela panela."}
        d.update(kw); return d

    def scene(self,tool="zsky"):
        return {"scene_id":"scene_03","narration_excerpt":"A gota vaporizou sobre a superfície quente.",
                "main_verb":"vaporizou","caption_safe_area":"central-lower","tool_candidate":tool}

    def meta(self,tool="zsky",**kw):
        d={"generation_tool":tool,"video_id":"video_a","watermark_present":False,"rights_confirmed":True,
           "commercial_use_confirmed":True,"download_allowed":True,"cost_brl":0,"credits_consumed":0,
           "payment_required":False,"card_required":False,"trial_with_future_charge":False,
           "narration_visual_match":True,"continuity_ok":True,"physical_coherence":True,
           "historical_scientific_fidelity":True,"deformed_characters_or_anatomy":False,
           "generated_text_or_bad_text":False,"human_decision":"APROVAR PARA MONTAGEM"}
        d.update(kw); return d

    def test_01_selects_zsky(self):
        p=aa.plan(self.req(),self.registry)
        self.assertEqual(p["scenes"][0]["tool_candidate"],"zsky")

    def test_02_selects_steve_ai(self):
        req=self.req(approved_script="Léo ilustra uma comparação simples entre dois caminhos. Depois o personagem mostra a sequência educativa passo a passo.",
                     scene_hints=[{"match":"Léo","requires_leo":True},{"match":"personagem","tool_candidate":"steve_ai"}])
        p=aa.plan(req,self.registry)
        self.assertTrue(any(s["tool_candidate"]=="steve_ai" for s in p["scenes"]))

    def test_03_selects_current_pipeline_when_real_footage_exists(self):
        p=aa.plan(self.req(real_footage_available=True),self.registry)
        self.assertTrue(all(s["tool_candidate"]=="current_pipeline" for s in p["scenes"]))

    def test_04_rejects_horizontal_video(self):
        r=aa.validate(self.horizontal,self.scene(),self.meta(),self.relaxed())
        self.assertIn("ORIENTATION_NOT_VERTICAL",r["errors"])

    def test_05_rejects_below_minimum_resolution(self):
        r=aa.validate(self.lowres,self.scene(),self.meta(),self.relaxed())
        self.assertIn("RESOLUTION_BELOW_MINIMUM",r["errors"])

    def test_06_rejects_duplicate_file(self):
        digest=aa.sha(self.motion)
        ledger={"entries":[{"sha256":digest,"video_id":"video_a"}]}
        r=aa.validate(self.motion,self.scene(),self.meta(),self.relaxed(),ledger)
        self.assertIn("DUPLICATE_FILE",r["errors"])

    def test_07_rejects_scene_without_motion(self):
        r=aa.validate(self.static,self.scene(),self.meta(),self.relaxed())
        self.assertIn("SCENE_WITHOUT_MEANINGFUL_MOTION",r["errors"])

    def test_08_rejects_declared_watermark(self):
        r=aa.validate(self.motion,self.scene(),self.meta(watermark_present=True),self.relaxed())
        self.assertEqual(r["state"],"rejected_watermark")

    def test_09_rejects_unconfirmed_rights(self):
        r=aa.validate(self.motion,self.scene(),self.meta(rights_confirmed=False),self.relaxed())
        self.assertEqual(r["state"],"rejected_rights")

    def test_10_rejects_credit_consumption(self):
        r=aa.validate(self.motion,self.scene(),self.meta(credits_consumed=1),self.relaxed())
        self.assertEqual(r["state"],"rejected_cost")

    def test_11_human_denial_falls_back(self):
        r=aa.validate(self.motion,self.scene(),self.meta(human_decision="REJEITAR E USAR PIPELINE ATUAL"),self.relaxed())
        self.assertEqual(r["state"],"fallback_to_current_pipeline")
        self.assertFalse(r["approved_for_editing"])

    def test_12_rejects_narration_visual_mismatch(self):
        r=aa.validate(self.motion,self.scene(),self.meta(narration_visual_match=False),self.relaxed())
        self.assertEqual(r["state"],"rejected_inaccurate")

    def test_13_rejects_same_animation_on_different_topic(self):
        digest=aa.sha(self.motion)
        ledger={"entries":[{"sha256":digest,"video_id":"outro_video"}]}
        r=aa.validate(self.motion,self.scene(),self.meta(video_id="video_a"),self.relaxed(),ledger)
        self.assertEqual(r["state"],"rejected_duplicate_animation")

    def test_14_current_terms_force_safe_fallback(self):
        r=aa.validate(self.motion,self.scene(),self.meta(),self.registry)
        self.assertFalse(r["approved_for_editing"])
        self.assertEqual(r.get("fallback"),"current_pipeline")
        self.assertTrue(any("ZSKY_FREE_WATERMARK_POLICY_BLOCK"==x for x in r["errors"]))

    def test_15_integration_normalizes_timeline_asset(self):
        out=self.tmp/"normalized.mp4"; patch=self.tmp/"patch.json"
        validation={"state":"approved_for_editing","approved_for_editing":True}
        p=aa.integrate(self.motion,self.scene(),validation,out,patch)
        self.assertEqual(p["state"],"integrated_into_timeline")
        self.assertEqual(p["format"]["width"],1080)
        self.assertEqual(p["format"]["height"],1920)
        self.assertEqual(p["format"]["fps"],30.0)
        self.assertEqual(p["format"]["audio_streams"],0)
        self.assertFalse(p["publication_allowed"])

    def test_16_publication_stays_disabled(self):
        p=aa.plan(self.req(),self.registry)
        self.assertFalse(p["production_enabled"])
        self.assertFalse(p["automatic_publication"])
        self.assertFalse(p["publication_allowed"])
        self.assertFalse(self.registry["tools"]["zsky"]["automatic_publication"])
        self.assertFalse(self.registry["tools"]["steve_ai"]["automatic_publication"])

if __name__=="__main__":
    unittest.main(verbosity=2)
