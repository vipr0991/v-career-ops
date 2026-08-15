import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline_manager import PipelineManager
from direct_scoring import get_scoring_client
from presentation_generator import PresentationGenerator
from linkedin_outreach import LinkedInOutreachHelper

class TestCareerOpsCore(unittest.TestCase):
    def test_pipeline_deduplication(self):
        test_file = "tests/test_pipeline_store.json"
        if os.path.exists(test_file):
            os.remove(test_file)
            
        pm = PipelineManager(storage_path=test_file)
        
        # 1. Insert first job
        job1 = pm.upsert_job({
            "title": "Marketing Operations Manager",
            "company": "Careem",
            "location": "Dubai, UAE",
            "score": {"overall_score": 90}
        })
        self.assertEqual(job1["stage"], "pipeline_saved")
        
        # 2. Insert same company + title + location (should deduplicate)
        job2 = pm.upsert_job({
            "title": "Marketing Operations Manager",
            "company": "Careem",
            "location": "Dubai",
            "score": {"overall_score": 92}
        })
        
        items = pm.get_all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], job1["id"])
        
        if os.path.exists(test_file):
            os.remove(test_file)

    def test_scoring_rubric_fallback(self):
        client = get_scoring_client()
        score_res = client._heuristic_fallback_score(
            jd="Looking for an AI content & automation specialist to scale marketing pipelines with SEO/PPC and multi-channel campaigns in Dubai.",
            title="AI Content Specialist",
            company="Tech GCC",
            location="Dubai, UAE"
        )
        
        self.assertIn("overall_score", score_res)
        self.assertGreaterEqual(score_res["overall_score"], 60)
        self.assertIn("category_scores", score_res)
        self.assertIn("skills_match", score_res["category_scores"])
        self.assertIn("strengths", score_res)
        self.assertGreater(len(score_res["strengths"]), 0)
        self.assertIn("ats_keywords_found", score_res)

    def test_linkedin_note_length(self):
        helper = LinkedInOutreachHelper()
        note = helper._fallback_note("Sarah", "Careem", "Marketing Automation Lead")
        self.assertLessEqual(len(note), 200)
        self.assertIn("Sarah", note)
        self.assertIn("Careem", note)

    def test_pptx_generation(self):
        gen = PresentationGenerator(output_dir="tests")
        deck_path = gen.generate_value_prop_deck(
            company_name="Talabat",
            job_title="Head of AI Marketing",
            research_data={"business_model": "Food and q-commerce delivery leader in MENA."}
        )
        self.assertTrue(os.path.exists(deck_path))
        self.assertGreater(os.path.getsize(deck_path), 0)
        
        if os.path.exists(deck_path):
            os.remove(deck_path)

if __name__ == "__main__":
    unittest.main()
