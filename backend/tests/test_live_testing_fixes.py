# backend/tests/test_live_testing_fixes.py
"""
Comprehensive Regression Test Suite for EmoTrack Live Testing Fixes:
1. Grounded Emotional Summary: Absence of generic 'cognitive strain about performance and workload';
   correct reflection of personal time / exhaustion without pathologizing;
   preservation of mixed completion + remaining tasks.
2. Follow-Up Questions: Responsive to positive emotional direction and satisfaction;
   exploring accomplishments rather than prematurely redirecting to difficulty/challenges.
3. Wellness Trend Interpretation: Accurate volatility & rebound handling for
   [44, 87, 54, 55] (Fluctuating/Stabilizing) and [44, 87, 54, 55, 67] (Improving with Rebound).
4. Tailored Suggestions: Rest and gentle pauses for exhaustion; savoring for accomplishments;
   avoiding reflexive productivity commands.
5. Simple Human-Centered Integration: End-to-end pipeline execution with clean responses.
"""

import sys
import os
import unittest

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.trend_service import calculate_longitudinal_trend
from ml.agents.tools import (
    tool_generate_follow_up_question,
    tool_synthesize_conversational_explanation,
    tool_generate_grounded_recommendations,
    extract_grounded_topics
)
from ml.agents.orchestrator import orchestrator


class TestLiveTestingFixes(unittest.TestCase):

    def test_trend_interpretation_oscillating_series(self):
        """
        Sequence: [44, 87, 54, 55]
        Previously mislabeled 'Needs Attention: downward drift'.
        Must be labeled as Fluctuating / Stabilizing.
        """
        # History is in reverse chronological order: [54, 87, 44]
        history = [{"wellness_score": 54}, {"wellness_score": 87}, {"wellness_score": 44}]
        current_score = 55
        result = calculate_longitudinal_trend(current_score=current_score, history=history)

        self.assertEqual(result["points"], [44, 87, 54, 55])
        self.assertEqual(result["direction"], "Fluctuating")
        self.assertNotIn("downward drift", result["message"].lower())
        self.assertIn("stabilize", result["message"].lower())
        print("[PASS] Verified trend [44, 87, 54, 55] is Fluctuating/Stabilizing (not downward drift)")

    def test_trend_interpretation_rebounding_series(self):
        """
        Sequence: [44, 87, 54, 55, 67]
        Previously mislabeled 'Stable: steady and consistent'.
        Must be labeled as Improving with upward rebound.
        """
        # History in reverse chronological order: [55, 54, 87, 44]
        history = [{"wellness_score": 55}, {"wellness_score": 54}, {"wellness_score": 87}, {"wellness_score": 44}]
        current_score = 67
        result = calculate_longitudinal_trend(current_score=current_score, history=history)

        self.assertEqual(result["points"], [44, 87, 54, 55, 67])
        self.assertEqual(result["direction"], "Improving")
        self.assertNotIn("steady and consistent", result["message"].lower())
        self.assertIn("rebound", result["message"].lower())
        print("[PASS] Verified trend [44, 87, 54, 55, 67] is Improving with upward rebound (not steady and consistent)")

    def test_trend_interpretation_truly_stable_series(self):
        """
        Sequence: [62, 60, 63, 61]
        Should be labeled Stable.
        """
        history = [{"wellness_score": 63}, {"wellness_score": 60}, {"wellness_score": 62}]
        current_score = 61
        result = calculate_longitudinal_trend(current_score=current_score, history=history)

        self.assertEqual(result["points"], [62, 60, 63, 61])
        self.assertEqual(result["direction"], "Stable")
        self.assertIn("steady and consistent", result["message"].lower())
        print("[PASS] Verified trend [62, 60, 63, 61] is Stable")

    def test_follow_up_question_for_positive_completion(self):
        """
        When user expresses completion and satisfaction (even with work remaining),
        follow-up question must explore accomplishment and relief, NOT challenges or demands.
        """
        text = "I completed all my work on time and I feel good. There is still more work left, but I am happy with what I finished."
        q = tool_generate_follow_up_question(
            text=text,
            primary_emotion="Joy",
            secondary_emotion="Neutral",
            is_ambiguous=False,
            uncertainty_score=0.2,
            full_context=text,
            turn_count=1
        )

        q_lower = q.lower()
        self.assertNotIn("challenging or demanding", q_lower)
        self.assertNotIn("what's feeling most challenging", q_lower)
        # Should reference satisfaction, relief, or accomplishment
        has_positive_tone = any(w in q_lower for w in ["satisfying", "satisfaction", "accomplishment", "relief", "milestone", "wins"])
        self.assertTrue(has_positive_tone, f"Question did not explore positive accomplishment: {q}")
        print(f"[PASS] Verified positive follow-up question: '{q}'")

    def test_follow_up_question_for_exhaustion_personal_time(self):
        """
        When user expresses exhaustion and longing for personal time,
        the question should explore restorative rest or space, not generic challenges.
        """
        text = "I'm exhausted and just want some personal time for myself away from all this."
        q = tool_generate_follow_up_question(
            text=text,
            primary_emotion="Sadness",
            secondary_emotion="Neutral",
            is_ambiguous=False,
            uncertainty_score=0.3,
            full_context=text,
            turn_count=1
        )

        q_lower = q.lower()
        has_rest_theme = any(w in q_lower for w in ["rest", "recharge", "breathing room", "personal time", "quiet"])
        self.assertTrue(has_rest_theme, f"Question did not focus on rest or personal space: {q}")
        print(f"[PASS] Verified rest-focused follow-up question: '{q}'")

    def test_explanation_synthesis_exhaustion_no_pathologizing(self):
        """
        For reflections about exhaustion and personal time:
        - NEVER output 'cognitive strain about performance and workload'
        - Explicitly reflect user's desire for personal time and rest
        - Affirms natural need for rest rather than performance deficiency
        """
        turns = [{"text": "I'm exhausted and just want some personal time for myself away from all these non-stop demands."}]
        explanation = tool_synthesize_conversational_explanation(
            turns_summary=turns,
            final_emotion="Sadness",
            stress_level="Moderate"
        )

        self.assertNotIn("cognitive strain about performance and workload", explanation)
        self.assertTrue("personal time" in explanation.lower() or "exhausted" in explanation.lower())
        self.assertIn("rest and personal recovery rather than a performance shortcoming", explanation)
        print("[PASS] Verified non-pathologizing explanation for exhaustion and personal time")

    def test_explanation_synthesis_mixed_completion_and_remaining_work(self):
        """
        For reflections with completion and work remaining:
        - Preserves BOTH the accomplishment/satisfaction AND awareness of remaining tasks
        - Distinguishes user statement from model inference
        """
        turns = [{"text": "I completed all my work on time and I feel good, although there is still more work left, but I am happy with what I finished."}]
        explanation = tool_synthesize_conversational_explanation(
            turns_summary=turns,
            final_emotion="Joy",
            stress_level="Low"
        )

        exp_lower = explanation.lower()
        self.assertNotIn("cognitive strain about performance and workload", exp_lower)
        self.assertTrue("satisfaction" in exp_lower or "relief" in exp_lower)
        self.assertTrue("remaining" in exp_lower or "additional work" in exp_lower or "ahead" in exp_lower)
        self.assertIn("tentatively", exp_lower)
        print("[PASS] Verified mixed reflection explanation preserves both milestone and remaining tasks")

    def test_grounded_recommendations_exhaustion(self):
        """
        For exhaustion / personal time:
        - Must provide restful, boundary-protecting suggestions
        - Must NOT command user to 'Break the mountain into steps: Pick just one small, manageable task to complete in the next 20 minutes'
        """
        text = "I'm exhausted and just want some personal time for myself."
        recs = tool_generate_grounded_recommendations(emotion="Sadness", stress_level="Moderate", user_text=text)

        recs_str = " ".join(recs)
        self.assertNotIn("Pick just one small, manageable task to complete in the next 20 minutes", recs_str)
        self.assertTrue("pause" in recs_str.lower() or "rest" in recs_str.lower() or "pocket" in recs_str.lower())
        print("[PASS] Verified restful recommendations for exhaustion:")
        for r in recs:
            print(f"   - {r}")

    def test_grounded_recommendations_completion_with_remaining(self):
        """
        For completion with work remaining:
        - Suggests savoring the milestone and pacing the next stretch
        - Does NOT immediately command user to grind more
        """
        text = "I completed all my work on time and feel good, but there is still more work left."
        recs = tool_generate_grounded_recommendations(emotion="Joy", stress_level="Low", user_text=text)

        recs_str = " ".join(recs)
        self.assertTrue("savor" in recs_str.lower() or "milestone" in recs_str.lower())
        self.assertTrue("pace" in recs_str.lower())
        print("[PASS] Verified milestone-savoring recommendations for task completion:")
        for r in recs:
            print(f"   - {r}")

    def test_full_pipeline_orchestrator_integration(self):
        """
        Runs the full agentic orchestrator end-to-end on an exhaustion reflection.
        Verifies clean, human-centered output.
        """
        text = "I'm feeling really drained and just need some personal time for myself."
        result = orchestrator.run(text=text, user_id=1, history=[])

        self.assertIn("emotion", result)
        self.assertIn("stress", result)
        self.assertIn("wellness_score", result)
        self.assertIn("explanation", result)
        self.assertNotIn("cognitive strain about performance and workload", result["explanation"])
        self.assertNotIn("solidified around", result["insights"])
        print("[PASS] Verified full agentic orchestrator end-to-end pipeline execution")


if __name__ == "__main__":
    unittest.main()
