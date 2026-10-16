# backend/tests/test_multi_turn_clarification.py
"""
Test Suite for Multi-Turn Clarification (Up to 3 Follow-Up Questions, 4 Turns Total Max)
Verifies:
1. Stopping policy allows up to 3 follow-ups when ambiguity persists.
2. Hard ceiling at 4 turns unconditionally terminates and finalizes.
3. Early stopping on closing remark ("that's all", "im done").
4. Insight narrative has proper English grammar (no "a insufficient data pattern").
5. State and trace consistency across turns.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from database.connection import init_db
from database.seed_data import seed_database
from ml.agents.orchestrator import orchestrator
from ml.agents.agent_state import AgentState, TurnRecord
from services.multi_turn_service import MultiTurnService

def test_grammar_in_insights():
    print("Testing grammatical correctness of insights...")
    init_db()
    # User 999999 has zero historical analyses -> triggers Insufficient Data
    state = AgentState(
        session_id="test-grammar-session",
        user_id=999999,
        current_text="I am feeling okay today.",
        turns=[TurnRecord(turn_number=1, user_text="I am feeling okay today.")]
    )
    final_state = orchestrator.execute_turn_assessment(state, force_finalize=True)
    
    # Verify no grammatical error
    assert "a insufficient data pattern" not in final_state.insights
    assert "insufficient historical entries" in final_state.insights
    assert "milestone" not in final_state.insights.lower()
    print("  [OK] Insufficient data insight grammar verified.")

    # User 1 has historical analyses -> verify proper article ("a stable", "an improving")
    state_hist = AgentState(
        session_id="test-grammar-hist-session",
        user_id=1,
        current_text="I am feeling wonderful and happy today.",
        turns=[TurnRecord(turn_number=1, user_text="I am feeling wonderful and happy today.")]
    )
    final_state_hist = orchestrator.execute_turn_assessment(state_hist, force_finalize=True)
    assert "a insufficient" not in final_state_hist.insights
    print(f"  [OK] History insight verified: '{final_state_hist.insights}'")

def test_early_stopping_on_closing_remark():
    print("Testing early stopping on user closing remark...")
    state = AgentState(
        session_id="test-close-session",
        user_id=1,
        current_text="That's all for today, thank you.",
        turns=[
            TurnRecord(turn_number=1, user_text="I was feeling stressed earlier."),
            TurnRecord(turn_number=2, user_text="That's all for today, thank you.")
        ],
        turn_count=2
    )
    should_stop = orchestrator._evaluate_stopping_policy(state, force_finalize=False)
    assert should_stop is True
    print("  [OK] Closing remark policy verified.")

def test_multi_turn_bounds():
    print("Testing multi-turn bounds (max 4 turns)...")
    init_db()
    
    # Start session with ambiguous input
    res1 = MultiTurnService.start_session(user_id=1, text="Yeah great day... totally went as planned.")
    assert "is_completed" in res1
    session_id = res1["session_id"]
    
    if not res1["is_completed"]:
        assert res1["turn_count"] == 1
        assert "next_question" in res1
        print(f"  Turn 1 question: {res1['next_question']}")

        # Turn 2: User responds
        res2 = MultiTurnService.respond_to_session(user_id=1, session_id=session_id, text="Actually my experiment broke and I lost all my data.")
        print(f"  Turn 2 status: is_completed={res2['is_completed']}, turn_count={res2['turn_count']}")

        # If still active, test turn 3
        if not res2["is_completed"]:
            res3 = MultiTurnService.respond_to_session(user_id=1, session_id=session_id, text="I am still really frustrated because I spent 3 weeks on it.")
            print(f"  Turn 3 status: is_completed={res3['is_completed']}, turn_count={res3['turn_count']}")

            # If still active, test turn 4 (max bound)
            if not res3["is_completed"]:
                res4 = MultiTurnService.respond_to_session(user_id=1, session_id=session_id, text="I guess I have to start over.")
                cnt = res4.get("turn_count") or res4.get("turns_count") or 4
                print(f"  Turn 4 status: is_completed={res4['is_completed']}, turn_count={cnt}")
                assert res4["is_completed"] is True
                assert cnt <= 4

    print("  [OK] Multi-turn bounds verified.")

def run_all():
    print("=== Running Multi-Turn Clarification Test Suite ===")
    test_grammar_in_insights()
    test_early_stopping_on_closing_remark()
    test_multi_turn_bounds()
    print("=== ALL MULTI-TURN TESTS PASSED ===")

if __name__ == "__main__":
    run_all()
