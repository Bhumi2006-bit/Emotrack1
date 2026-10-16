# backend/tests/test_interpersonal_uncertainty.py
"""
Comprehensive Regression Test Suite for Interpersonal Uncertainty,
Mixed Signals, Unmentioned Entity Suppression, and 'I don't know' Handling.

Covers 6 Crucial Capabilities:
1. Romantic feelings & mixed signals grounding without workload/plans hallucination.
2. User correcting Surprise to Sadness in relationship context without workload introduction.
3. Mixed positive + negative interpersonal experiences.
4. Unrelated topics (workload/exams/plate/hurdle) strictly suppressed when unmentioned.
5. User answering "I don't know" gracefully halts multi-turn dialogue and validates uncertainty.
6. Genuine workload reflections continue to explore academic/workload context properly.
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from ml.agents.tools import (
    extract_grounded_topics,
    tool_generate_initial_interpretation,
    tool_generate_follow_up_question,
    tool_detect_user_corrections,
    tool_synthesize_conversational_explanation,
    tool_generate_grounded_recommendations
)
from ml.agents.orchestrator import AgenticOrchestrator
from ml.agents.agent_state import AgentState, TurnRecord

UNMENTIONED_WORKLOAD_ENTITIES = [
    "viva", "exam", "submission", "submissions", "assignment", "assignments",
    "internship", "on your plate", "hurdle", "workload", "tomorrow"
]

def test_1_romantic_feelings_and_mixed_signals():
    print("Test 1: Romantic feelings & mixed signals context grounding...")
    entry = "I really like this guy, but I keep getting mixed signals from him and I'm unsure if he feels the same way. I spend so much time analyzing our conversations."
    topics = extract_grounded_topics(entry)

    assert topics["has_relationship_uncertainty"] is True, "Failed to identify relationship uncertainty"
    assert topics["has_mixed_signals"] is True, "Failed to identify mixed signals"
    assert topics["has_work_or_tasks"] is False, "Incorrectly flagged work or tasks"

    # Initial interpretation must address uncertainty/mixed signals, NOT workload
    initial_interp = tool_generate_initial_interpretation(
        text=entry,
        primary_emotion="Surprise",
        is_ambiguous=True,
        uncertainty_score=0.45
    )
    assert initial_interp is not None
    assert "mixed signals" in initial_interp.lower() or "uncertainty" in initial_interp.lower()
    for entity in UNMENTIONED_WORKLOAD_ENTITIES:
        assert entity not in initial_interp.lower(), f"Hallucinated '{entity}' in initial interpretation"

    # Follow-up question must explore interpersonal dynamics, NOT plans or workload
    q = tool_generate_follow_up_question(
        text=entry,
        primary_emotion="Surprise",
        is_ambiguous=True,
        uncertainty_score=0.45,
        full_context=entry,
        turn_count=1
    )
    q_lower = q.lower()
    for entity in UNMENTIONED_WORKLOAD_ENTITIES:
        assert entity not in q_lower, f"Hallucinated '{entity}' in follow-up question: {q}"
    assert "throw off your plans" not in q_lower, f"Surprise question hallucinated plans: {q}"
    print("  [OK] Test 1 passed.")

def test_2_correcting_surprise_to_sadness_in_relationship():
    print("Test 2: Correcting Surprise to Sadness in relationship context...")
    entry = "I like someone, but their mixed signals leave me wondering how they feel. I spend all day decoding conversations."
    user_correction = "It's not surprise. I'm feeling down and drained because I don't know where I stand."

    corr_res = tool_detect_user_corrections(
        text=user_correction,
        prior_question="Did this unexpected turn feel like a welcome surprise, or was it jarring and unsettling?",
        prior_emotion="Surprise"
    )
    assert "Surprise" in corr_res["rejected_emotions"]

    # Generate follow-up question after rejection
    q = tool_generate_follow_up_question(
        text=user_correction,
        primary_emotion="Sadness",
        rejected_emotions=["Surprise"],
        full_context=entry + " " + user_correction,
        turn_count=2
    )
    q_lower = q.lower()
    for entity in UNMENTIONED_WORKLOAD_ENTITIES:
        assert entity not in q_lower, f"Hallucinated '{entity}' after emotion correction: {q}"
    assert "already on your plate" not in q_lower, f"Hallucinated 'plate' in rejection question: {q}"
    assert "uncertainty" in q_lower or "interaction" in q_lower or "signals" in q_lower or "connection" in q_lower, f"Question not grounded in relationship context: {q}"

    # Verify recommendations
    recs = tool_generate_grounded_recommendations("Sadness", "Moderate", entry + " " + user_correction)
    assert len(recs) == 3
    recs_text = " ".join(recs).lower()
    assert "observe patterns over time" in recs_text or "decoding" in recs_text
    assert "release the urgency" in recs_text
    assert "self-worth" in recs_text
    print("  [OK] Test 2 passed.")

def test_3_mixed_positive_and_negative_interpersonal():
    print("Test 3: Mixed positive and negative interpersonal reflection...")
    entry = "I had a great time talking to him today, but later I realized he might just be being friendly. It left me feeling confused."
    topics = extract_grounded_topics(entry)
    assert topics["has_relationship_uncertainty"] is True
    assert topics["has_work_or_tasks"] is False

    q = tool_generate_follow_up_question(
        text=entry,
        primary_emotion="Joy",
        secondary_emotion="Sadness",
        is_ambiguous=True,
        uncertainty_score=0.48,
        full_context=entry,
        turn_count=1
    )
    q_lower = q.lower()
    for entity in UNMENTIONED_WORKLOAD_ENTITIES:
        assert entity not in q_lower, f"Hallucinated '{entity}' in mixed reflection: {q}"
    print("  [OK] Test 3 passed.")

def test_4_unmentioned_topics_strictly_suppressed():
    print("Test 4: Strict suppression of unmentioned entities across questions and narrative...")
    context = "I keep waiting for a clear answer from my friend about our summer trip, but they never reply."
    q = tool_generate_follow_up_question(
        text=context,
        primary_emotion="Sadness",
        full_context=context,
        turn_count=1
    )
    q_lower = q.lower()
    for entity in ["viva", "exam", "submissions", "assignments", "internship", "on your plate"]:
        assert entity not in q_lower, f"Suppressed entity '{entity}' was hallucinated in question: {q}"

    # Synthesized narrative
    turns_summary = [{"text": context, "primary_emotion": "Sadness"}]
    explanation = tool_synthesize_conversational_explanation(
        turns_summary=turns_summary,
        final_emotion="Sadness",
        stress_level="Moderate"
    )
    exp_lower = explanation.lower()
    for entity in ["viva", "exam", "submissions", "assignments", "internship", "workload demands"]:
        assert entity not in exp_lower, f"Suppressed entity '{entity}' was hallucinated in explanation: {explanation}"
    print("  [OK] Test 4 passed.")

def test_5_user_answering_i_dont_know():
    print("Test 5: User answering 'I don't know' stops dialogue and validates uncertainty...")
    orchestrator = AgenticOrchestrator()

    # Simulate Turn 1: user entry
    t1_text = "I like him, but mixed signals are really confusing me."
    state = AgentState(session_id="test-idk-session", user_id=1, initial_text=t1_text, current_text=t1_text)
    state.turn_count = 1
    state.current_emotion = {"primary_emotion": "Surprise", "confidence": 0.60, "is_ambiguous": True, "margin": 0.05}
    state.final_primary_emotion = "Surprise"
    state.final_confidence = 0.60
    state.turns.append(TurnRecord(turn_number=1, user_text=t1_text, primary_emotion="Surprise", confidence=0.60, assistant_question="Did this unexpected turn feel like a welcome surprise, or was it jarring and unsettling?"))

    # Turn 2: User corrects surprise
    t2_text = "It's not surprise. Just sad."
    state.turn_count = 2
    state.current_text = t2_text
    state.rejected_emotions = ["Surprise"]
    state.final_primary_emotion = "Sadness"
    state.current_emotion = {"primary_emotion": "Sadness", "confidence": 0.70, "is_ambiguous": False, "margin": 0.20}
    state.final_confidence = 0.70
    state.turns.append(TurnRecord(turn_number=2, user_text=t2_text, primary_emotion="Sadness", confidence=0.70, assistant_question="When signals feel mixed or contradictory, does that uncertainty make you feel more anxious about where you stand, or drained from constantly trying to make sense of it?"))

    # Turn 3: User answers "I don't know"
    t3_text = "I don't know."
    state.turn_count = 3
    state.current_text = t3_text

    # Stopping policy must return True to finalize
    should_stop = orchestrator._evaluate_stopping_policy(state, force_finalize=False)
    assert should_stop is True, "Stopping policy failed to halt on 'I don't know' at turn 3"

    # Explanation must acknowledge that uncertainty and distinguish unknown from stated facts
    turns_summary = [
        {"text": t1_text, "primary_emotion": "Surprise"},
        {"text": t2_text, "primary_emotion": "Sadness"},
        {"text": t3_text, "primary_emotion": "Sadness"}
    ]
    explanation = tool_synthesize_conversational_explanation(
        turns_summary=turns_summary,
        final_emotion="Sadness",
        stress_level="Moderate",
        rejected_emotions=["Surprise"]
    )
    exp_lower = explanation.lower()
    assert "difficult to know or define" in exp_lower or "natural response" in exp_lower
    assert "unknown" in exp_lower or "ambiguity" in exp_lower
    assert "surprise does not match" in exp_lower or "surprise" in exp_lower
    print("  [OK] Test 5 passed.")

def test_6_genuine_workload_remains_active():
    print("Test 6: Genuine workload reflections properly explore academic context...")
    entry = "I have my viva tomorrow and three project submissions due tonight."
    topics = extract_grounded_topics(entry)
    assert topics["has_viva"] is True
    assert topics["has_submissions"] is True
    assert topics["has_tomorrow"] is True
    assert topics["has_work_or_tasks"] is True

    q = tool_generate_follow_up_question(
        text=entry,
        primary_emotion="Fear",
        full_context=entry,
        turn_count=1
    )
    q_lower = q.lower()
    assert "viva" in q_lower or "submission" in q_lower, f"Failed to explore genuine workload in question: {q}"

    recs = tool_generate_grounded_recommendations("Fear", "High", entry)
    recs_text = " ".join(recs).lower()
    assert "viva" in recs_text or "concept" in recs_text or "stopping time" in recs_text
    print("  [OK] Test 6 passed.")

if __name__ == "__main__":
    print("\n=== Running Interpersonal Uncertainty & Grounding Regression Suite ===")
    test_1_romantic_feelings_and_mixed_signals()
    test_2_correcting_surprise_to_sadness_in_relationship()
    test_3_mixed_positive_and_negative_interpersonal()
    test_4_unmentioned_topics_strictly_suppressed()
    test_5_user_answering_i_dont_know()
    test_6_genuine_workload_remains_active()
    print("\nALL 6 REGRESSION TESTS PASSED SUCCESSFULLY!\n")
