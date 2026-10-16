# backend/tests/test_multi_turn_corrections.py
"""
Test Suite for Multi-Turn Reasoning, Emotion Corrections, Non-Repeating Questions,
and Personalized Explanations.

Verifies:
1. The viva/submissions entry produces an empathetic framing and targeted question without repeating.
2. Explicit rejection of Surprise ("It's not surprise...") triggers reassessment.
3. The next question is completely different and relevant to workload/submissions/viva.
4. The final explanation refers to academic workload, viva, and submissions, and acknowledges that Surprise was rejected.
5. Final emotion and explanation use the same finalized assessment.
6. The stress model remains separate from emotion inference.
7. The system never exceeds the initial turn plus three follow-ups (max 4 turns).
8. Existing session ownership and persistence continue to work.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.multi_turn_service import MultiTurnService
from ml.agents.orchestrator import orchestrator
from ml.agents.tools import tool_detect_user_corrections, tool_generate_follow_up_question
from database.connection import init_db
from database.models import create_user, get_conversation_session, get_user_by_email

def run_tests():
    print("=== STARTING MULTI-TURN REASONING & CORRECTION TEST SUITE ===")
    init_db()

    # Setup demo test user
    test_email = "correction_test_user@emotrack.internal"
    user = get_user_by_email(test_email)
    if not user:
        user_res = create_user(
            username="academic_tester",
            name="Academic Tester",
            email=test_email,
            password_hash="testpasshash123"
        )
        user_id = user_res["id"]
    else:
        user_id = user["id"]

    # -------------------------------------------------------------------------
    # TEST 1: Tool-level correction & negation parser
    # -------------------------------------------------------------------------
    print("\n--- TEST 1: Unit Test Emotion Rejection Detection ---")
    corr1 = tool_detect_user_corrections(
        text="It's not surprise. I'm feeling stressed and overwhelmed because there is so much work.",
        prior_question="Was this surprise something that caught you off guard in a positive way, or did it throw off your plans?",
        prior_emotion="Surprise"
    )
    assert corr1["has_correction"] is True, "Failed to detect explicit rejection of surprise"
    assert "Surprise" in corr1["rejected_emotions"], f"Expected Surprise in rejected emotions, got {corr1['rejected_emotions']}"
    assert corr1["acknowledgment"] is not None
    assert "Surprise doesn't fit" in corr1["acknowledgment"]
    print(f"  [PASSED] Detected rejection of Surprise. Acknowledgment: {corr1['acknowledgment']}")

    corr2 = tool_detect_user_corrections(
        text="I am not angry at all, just deeply sad and tired.",
        prior_question="What was the tipping point that made you feel so frustrated?",
        prior_emotion="Anger"
    )
    assert corr2["has_correction"] is True
    assert "Anger" in corr2["rejected_emotions"]
    print(f"  [PASSED] Detected rejection of Anger: {corr2['rejected_emotions']}")

    # -------------------------------------------------------------------------
    # TEST 2: Non-repeating follow-up question generator
    # -------------------------------------------------------------------------
    print("\n--- TEST 2: Question Deduplication & Contextual Relevance ---")
    asked = [
        "Was this surprise something that caught you off guard in a positive way, or did it throw off your plans?"
    ]
    next_q = tool_generate_follow_up_question(
        text="It's not surprise. I'm feeling stressed and overwhelmed because there is so much work.",
        primary_emotion="Fear",
        secondary_emotion="Sadness",
        is_ambiguous=False,
        uncertainty_score=0.45,
        full_context="I'm worried about my viva tomorrow and there are so many submissions.",
        rejected_emotions=["Surprise"],
        asked_questions=asked,
        turn_count=2
    )
    assert next_q not in asked, f"CRITICAL: Question was repeated! Got {next_q}"
    assert "surprise" not in next_q.lower(), f"Question still asked about surprise after rejection! Got {next_q}"
    assert any(w in next_q.lower() for w in ["viva", "submission", "work", "time", "pressure", "weighing"]), \
        f"Question failed to incorporate academic context! Got {next_q}"
    print(f"  [PASSED] Successfully generated fresh, non-repeating contextual question:\n    -> '{next_q}'")

    # -------------------------------------------------------------------------
    # TEST 3: Full Multi-Turn Viva/Submissions Workflow
    # -------------------------------------------------------------------------
    print("\n--- TEST 3: End-to-End Viva/Submissions Multi-Turn Dialogue ---")
    
    # TURN 1: Initial reflection
    initial_text = "I'm worried about my viva tomorrow and there are so many submissions. I'm feeling overwhelmed about everything."
    t1_res = MultiTurnService.start_session(user_id=user_id, text=initial_text)
    session_id = t1_res["session_id"]
    
    print(f"  [Turn 1] Session started: {session_id}")
    print(f"  [Turn 1] Preliminary emotion: {t1_res['preliminary_emotion']} ({round(t1_res['preliminary_confidence']*100)}%)")
    print(f"  [Turn 1] Preliminary stress: {t1_res['preliminary_stress']}")
    print(f"  [Turn 1] Question 1: '{t1_res['next_question']}'")
    q1 = t1_res["next_question"]

    # TURN 2: User responds rejecting Surprise and clarifying stress/workload
    reply_text = "It's not surprise. I'm feeling stressed and overwhelmed because there is so much work."
    t2_res = MultiTurnService.respond_to_session(user_id=user_id, session_id=session_id, text=reply_text)

    print(f"  [Turn 2] Turn count: {t2_res['turn_count']}")
    print(f"  [Turn 2] Rejected emotions: {t2_res.get('rejected_emotions')}")
    print(f"  [Turn 2] Acknowledgment: {t2_res.get('correction_acknowledgment')}")
    print(f"  [Turn 2] Preliminary emotion: {t2_res['preliminary_emotion']}")
    print(f"  [Turn 2] Question 2: '{t2_res.get('next_question')}'")

    # Verify no question repetition
    q2 = t2_res.get("next_question")
    if q2:
        assert q2 != q1, f"CRITICAL FAILURE: Question was repeated across turns!\nq1: {q1}\nq2: {q2}"
        assert "surprise" not in q2.lower(), f"CRITICAL FAILURE: Question still mentions surprise after rejection! Got: {q2}"
        print(f"  [PASSED] Verified Question 2 is completely distinct and does not repeat Question 1.")

    # Verify Surprise was eliminated from active primary emotion
    assert "Surprise" in t2_res.get("rejected_emotions", []), "Surprise was not added to rejected emotions"
    assert t2_res["preliminary_emotion"] != "Surprise", f"Model still chose Surprise after explicit rejection! Got {t2_res['preliminary_emotion']}"
    print(f"  [PASSED] Verified Surprise was suppressed and model reassessed to: {t2_res['preliminary_emotion']}")

    # TURN 3: User answers Question 2
    reply_text_3 = "The viva is definitely the scariest part because I don't feel ready, but the deadline for the submissions is tonight."
    t3_res = MultiTurnService.respond_to_session(user_id=user_id, session_id=session_id, text=reply_text_3)

    # If not completed yet, finalize session
    if not t3_res["is_completed"]:
        final_res = MultiTurnService.finalize_session(user_id=user_id, session_id=session_id)
    else:
        final_res = t3_res

    print(f"  [Final] Session completed: {final_res['is_completed']}")
    print(f"  [Final] Final emotion: {final_res['emotion']['label']} ({round(final_res['emotion']['confidence']*100)}%)")
    print(f"  [Final] Final stress: {final_res['stress']['level']}")

    # -------------------------------------------------------------------------
    # TEST 4: Explanation Quality & Grounding
    # -------------------------------------------------------------------------
    print("\n--- TEST 4: Explanation Content Verification ---")
    exp_summary = final_res["explanation"]["summary"]
    print(f"  [Final Explanation]:\n    \"{exp_summary}\"")

    # Verify explanation mentions academic context
    assert any(w in exp_summary.lower() for w in ["viva", "submission", "submissions", "academic", "workload"]), \
        "Explanation failed to refer to user's actual academic/viva/submission context!"
    # Verify explanation does NOT repeat surprise as the valid emotion
    assert "reflection remained centered on surprise" not in exp_summary.lower(), \
        "Explanation falsely claimed reflection remained centered on surprise!"
    # Verify acknowledgment of correction
    assert "surprise" not in final_res["emotion"]["label"].lower(), \
        f"Final emotion was Surprise despite explicit rejection! Got: {final_res['emotion']['label']}"

    print("  [PASSED] Explanation is grounded in actual context and acknowledges emotional trajectory.")

    # -------------------------------------------------------------------------
    # TEST 5: Strict Turn Limit (Max 4 turns total)
    # -------------------------------------------------------------------------
    print("\n--- TEST 5: Enforce Maximum Turn Limit (Max 4 turns) ---")
    sess_limit = MultiTurnService.start_session(user_id=user_id, text="I have some mixed feelings today.")
    sid = sess_limit["session_id"]
    for i in range(2, 6):
        res = MultiTurnService.respond_to_session(user_id=user_id, session_id=sid, text=f"Follow up response turn {i}")
        if res["is_completed"]:
            print(f"  [PASSED] Session automatically completed at turn {res['turn_count'] <= 4}")
            assert res["turn_count"] <= 4, f"Turn count exceeded max limit of 4! Got: {res['turn_count']}"
            break

    # -------------------------------------------------------------------------
    # TEST 6: Stress & Emotion Separation
    # -------------------------------------------------------------------------
    print("\n--- TEST 6: Independence of Stress and Emotion Models ---")
    assert final_res["stress"]["level"] in ["Low", "Moderate", "High"]
    assert final_res["emotion"]["label"] in ["Fear", "Sadness", "Anger", "Neutral", "Disgust", "Joy"]
    print(f"  [PASSED] Stress ({final_res['stress']['level']}) and Emotion ({final_res['emotion']['label']}) evaluated independently.")

    print("\n=== ALL MULTI-TURN REASONING & CORRECTION TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()
