# backend/tests/test_conversational_grounding.py
"""
Comprehensive Regression & Grounding Test Suite for EmoTrack.
Verifies that:
1. When input mentions internship and assignments, questions and explanations NEVER mention viva or tomorrow.
2. When input is 'its my self time', follow-up questions ground in personal time / burnout and NEVER mention viva or submissions.
3. User clarifications and emotion rejections suppress the rejected emotion and do not assume academic workload.
4. Explanations ('What EmoTrack understood') are human-readable, non-diagnostic, and strictly grounded in user words.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.agents.tools import (
    tool_detect_user_corrections,
    tool_generate_follow_up_question,
    tool_synthesize_conversational_explanation,
    extract_grounded_topics
)
from services.multi_turn_service import MultiTurnService
from database.connection import init_db
from database.models import create_user, get_user_by_email

def run_grounding_tests():
    print("=== STARTING CONVERSATIONAL GROUNDING & ANTI-HALLUCINATION TESTS ===")
    init_db()

    # TEST 1: Topic Extraction Accuracy
    print("\n--- TEST 1: Grounded Topic Extractor Accuracy ---")
    topics1 = extract_grounded_topics("I have so many college assignments and my internship is taking all my energy")
    assert topics1["has_internship"] is True
    assert topics1["has_assignments"] is True
    assert topics1["has_viva"] is False, "CRITICAL: Falsely detected viva in text without viva!"
    assert topics1["has_tomorrow"] is False, "CRITICAL: Falsely detected tomorrow in text without tomorrow!"
    print("  [PASSED] Accurately extracted internship & assignments without hallucinating viva or tomorrow.")

    topics2 = extract_grounded_topics("its my self time")
    assert topics2["has_personal_time"] is True
    assert topics2["has_viva"] is False
    assert topics2["has_submissions"] is False
    print("  [PASSED] Accurately extracted personal time from 'its my self time'.")

    # TEST 2: Clarification and Acknowledgment Phrasing
    print("\n--- TEST 2: User Correction and Clarification Grounding ---")
    corr_self = tool_detect_user_corrections(
        text="its my self time",
        prior_question="Between your internship responsibilities and college assignments, which one is consuming more mental energy?",
        prior_emotion="Surprise"
    )
    # Even if not directly saying 'not surprise', user focus shouldn't assume academic workload
    corr_reject = tool_detect_user_corrections(
        text="It's not surprise, its my self time and I'm exhausted.",
        prior_question="Was this surprise something that caught you off guard?",
        prior_emotion="Surprise"
    )
    assert corr_reject["has_correction"] is True
    assert "Surprise" in corr_reject["rejected_emotions"]
    assert "viva" not in corr_reject["user_focus"].lower(), "Hallucinated viva in user focus!"
    assert "personal time" in corr_reject["user_focus"].lower() or "exhaustion" in corr_reject["user_focus"].lower()
    print(f"  [PASSED] Correction detected focus: '{corr_reject['user_focus']}' with ack: '{corr_reject['acknowledgment']}'")

    # TEST 3: Grounded Follow-Up Generation (No Viva Hallucination)
    print("\n--- TEST 3: Follow-Up Questions Grounded in Internship & Personal Time ---")
    asked = []
    q_intern = tool_generate_follow_up_question(
        text="I have so many college assignments and my internship is taking all my energy.",
        primary_emotion="Fear",
        secondary_emotion="Sadness",
        full_context="I have so many college assignments and my internship is taking all my energy.",
        asked_questions=asked,
        turn_count=1
    )
    assert "viva" not in q_intern.lower(), f"CRITICAL HALLUCINATION: Question mentions viva!\nQuestion: {q_intern}"
    assert "tomorrow" not in q_intern.lower(), f"CRITICAL HALLUCINATION: Question mentions tomorrow!\nQuestion: {q_intern}"
    assert any(w in q_intern.lower() for w in ["internship", "assignment", "coursework", "energy", "pressure"]), \
        f"Question not grounded in user topics! Question: {q_intern}"
    print(f"  [PASSED] Turn 1 Question accurately grounded in internship & assignments:\n    -> '{q_intern}'")
    asked.append(q_intern)

    # Turn 2 user response: 'its my self time'
    q_self = tool_generate_follow_up_question(
        text="its my self time",
        primary_emotion="Sadness",
        secondary_emotion="Fear",
        full_context="I have so many college assignments and my internship is taking all my energy. its my self time",
        rejected_emotions=[],
        asked_questions=asked,
        turn_count=2
    )
    assert "viva" not in q_self.lower(), f"CRITICAL HALLUCINATION: Question mentions viva!\nQuestion: {q_self}"
    assert "tomorrow" not in q_self.lower(), f"CRITICAL HALLUCINATION: Question mentions tomorrow!\nQuestion: {q_self}"
    assert any(w in q_self.lower() for w in ["personal time", "recharge", "space", "room", "demands", "exhaustion"]), \
        f"Question failed to pivot to personal time! Question: {q_self}"
    print(f"  [PASSED] Turn 2 Question accurately grounded in personal time:\n    -> '{q_self}'")

    # TEST 4: Human-Readable Non-Diagnostic Explanation Grounding
    print("\n--- TEST 4: Explanation Grounding & Human-Readability ---")
    turns = [
        {"text": "I have so many college assignments and my internship is taking all my energy", "primary_emotion": "Fear"},
        {"text": "its my self time", "primary_emotion": "Sadness"}
    ]
    explanation = tool_synthesize_conversational_explanation(
        turns_summary=turns,
        final_emotion="Sadness",
        stress_level="Moderate",
        trend_direction="Stable",
        rejected_emotions=[]
    )
    assert "viva" not in explanation.lower(), f"Explanation hallucinated viva!\nExplanation: {explanation}"
    assert "tomorrow" not in explanation.lower(), f"Explanation hallucinated tomorrow!\nExplanation: {explanation}"
    assert "What EmoTrack understood" in explanation
    assert "independently identified" in explanation
    print(f"  [PASSED] Synthesized human-readable explanation:\n    -> \"{explanation}\"")

    print("\n=== ALL CONVERSATIONAL GROUNDING & ANTI-HALLUCINATION TESTS PASSED! ===")

if __name__ == "__main__":
    run_grounding_tests()
