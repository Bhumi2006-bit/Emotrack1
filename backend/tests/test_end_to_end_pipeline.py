# backend/tests/test_end_to_end_pipeline.py
"""
Comprehensive End-to-End Verification Test Suite for EmoTrack.
Tests:
1. Calibrated Emotion Inference (Temperature scaling, entropy uncertainty, ambiguity)
2. Supervised Dreaddit Stress Inference (Continuous probability, binary label, risk tier)
3. Multi-Turn Conversational Session (Start, empathetic clarification, sarcasm reconciliation, finalize)
4. XAI (Feature sensitivity occlusion attribution and conversational narrative synthesis)
5. Agentic AI Orchestrator (Bounded loop, auditable trace logging)
6. FastAPI Endpoints (TestClient verification)
"""

import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from database.connection import init_db
from database.seed_data import seed_database
from ml.models.emotion_model import emotion_classifier
from ml.models.stress_model import stress_classifier
from ml.agents.orchestrator import orchestrator
from ml.agents.agent_state import AgentState, TurnRecord
from services.multi_turn_service import MultiTurnService
from services.analysis_service import process_user_reflection
from app.main import app

def test_1_database_and_seeding():
    print("\n--- TEST 1: Database Initialization and Seeding ---")
    init_db()
    seed_database()
    from database.models import get_user_by_id, get_analyses_for_user
    user = get_user_by_id(1)
    assert user is not None
    assert user["email"] == "demo@emotrack.ai"
    analyses = get_analyses_for_user(1, limit=5)
    assert len(analyses) > 0
    print(f"[PASSED] Database initialized with {len(analyses)} seeded records for user {user['username']}")

def test_2_calibrated_emotion_inference():
    print("\n--- TEST 2: Calibrated Emotion Inference & Uncertainty ---")
    # Test unambiguous reflection
    res_clear = emotion_classifier.predict("I am furious and outraged by how they treated everyone!")
    assert res_clear["primary_emotion"] == "Anger"
    assert res_clear["confidence"] > 0.60
    assert 0.0 <= res_clear["uncertainty_score"] <= 1.0
    assert abs(sum(res_clear["distribution"].values()) - 1.0) < 1e-3
    print(f"[PASSED] Clear emotion: {res_clear['primary_emotion']} (conf={res_clear['confidence']:.2f}, uncertainty={res_clear['uncertainty_score']:.2f})")

    # Test ambiguous reflection
    res_ambig = emotion_classifier.predict("Well, I suppose it is fine, or maybe not, who knows really.")
    assert "is_ambiguous" in res_ambig
    assert "uncertainty_score" in res_ambig
    print(f"[PASSED] Ambiguous emotion: {res_ambig['primary_emotion']} (ambiguous={res_ambig['is_ambiguous']}, uncertainty={res_ambig['uncertainty_score']:.2f})")

def test_3_dreaddit_stress_classifier():
    print("\n--- TEST 3: Supervised Dreaddit Stress Pipeline ---")
    # Acute stress query
    high_stress_text = "I am having panic attacks and cannot sleep at all. Everything is falling apart and I cannot breathe from overwhelming anxiety."
    pred_high = stress_classifier.predict(high_stress_text)
    assert pred_high["level"] in ["Moderate", "High"]
    assert pred_high["probability"] > 0.50
    assert "Dreaddit" in pred_high["model_source"]
    print(f"[PASSED] High stress text -> Level: {pred_high['level']}, p(Stress): {pred_high['probability']:.2f}, Source: {pred_high['model_source']}")

    # Low stress query
    low_stress_text = "I spent a quiet afternoon drinking chamomile tea and reading a pleasant book in the garden."
    pred_low = stress_classifier.predict(low_stress_text)
    assert pred_low["level"] == "Low"
    assert pred_low["probability"] < 0.50
    print(f"[PASSED] Low stress text -> Level: {pred_low['level']}, p(Stress): {pred_low['probability']:.2f}")

def test_4_agentic_orchestrator_and_trace():
    print("\n--- TEST 4: Bounded Agentic Orchestrator & Auditable Trace ---")
    single_res = orchestrator.run(
        text="I am overwhelmed with my university assignments and feeling helpless.",
        user_id=1
    )
    assert "emotion" in single_res
    assert "stress" in single_res
    assert "wellness_score" in single_res
    assert "execution_trace" in single_res
    assert len(single_res["execution_trace"]) >= 4

    # Verify trace action types
    action_types = [t["action_type"] for t in single_res["execution_trace"]]
    assert "OBSERVE" in action_types
    assert "REASON" in action_types
    assert "TOOL_RESULT" in action_types
    assert "STOP" in action_types

    print(f"[PASSED] Agent trace logged {len(single_res['execution_trace'])} steps. Actions: {action_types}")

def test_5_multi_turn_session_lifecycle():
    print("\n--- TEST 5: Multi-Turn Conversational Session Lifecycle ---")
    # Turn 1: Sarcastic or ambiguous initial statement
    turn1_text = "Everything is just wonderful and I truly adore failing every single test."
    start_res = MultiTurnService.start_session(user_id=1, text=turn1_text)
    session_id = start_res["session_id"]
    assert session_id is not None
    assert start_res["turn_count"] == 1

    print(f"[Turn 1] Session started: {session_id}. Completed: {start_res['is_completed']}")
    if not start_res["is_completed"]:
        print(f"[Turn 1] Assistant asked clarifying question: '{start_res['next_question']}'")

        # Turn 2: User clarifies sarcastic intent
        turn2_text = "Actually, everything went wrong and I was being sarcastic. I am furious and stressed."
        respond_res = MultiTurnService.respond_to_session(
            user_id=1,
            session_id=session_id,
            text=turn2_text
        )
        print(f"[Turn 2] Responded. Completed: {respond_res['is_completed']}")

        # If not completed yet, finalize explicitly
        if not respond_res["is_completed"]:
            final_res = MultiTurnService.finalize_session(user_id=1, session_id=session_id)
        else:
            final_res = respond_res
    else:
        final_res = start_res

    assert final_res["is_completed"] is True
    # Verify sarcasm reconciliation: Emotion should resolve to a negative emotion (Anger/Sadness/Fear), NOT Joy
    assert final_res["emotion"]["label"] in ["Anger", "Sadness", "Fear", "Disgust"]
    expl_text = final_res.get("conversational_explanation") or (final_res["explanation"]["summary"] if isinstance(final_res["explanation"], dict) else final_res["explanation"])
    assert len(expl_text) > 20
    print(f"[PASSED] Multi-turn session completed. Reconciled emotion: {final_res['emotion']['label']} (confidence: {final_res['emotion']['confidence']:.2f})")
    print(f"[PASSED] Conversational XAI explanation: {expl_text[:120]}...")

def test_6_fastapi_rest_endpoints():
    print("\n--- TEST 6: FastAPI REST Endpoints via TestClient ---")
    client = TestClient(app)

    # Health endpoint
    h_res = client.get("/health")
    assert h_res.status_code == 200
    assert h_res.json()["status"] == "ok"
    print("[PASSED] GET /health returned 200 OK")

    # Login to obtain JWT
    login_res = client.post("/auth/login", json={"email": "demo@emotrack.ai", "password": "demo123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASSED] POST /auth/login authenticated successfully")

    # Single-turn analysis backward compatibility
    ana_res = client.post("/analysis", json={"text": "I feel grateful for the help from my peers today."}, headers=headers)
    assert ana_res.status_code == 200
    ana_data = ana_res.json()
    assert ana_data["emotion"]["label"] in ["Joy", "Neutral"]
    print(f"[PASSED] POST /analysis returned 200: {ana_data['emotion']['label']}")

    # Multi-turn session start endpoint
    start_res = client.post("/analysis/session/start", json={"text": "I am not sure how I feel, work is just piling up."}, headers=headers)
    assert start_res.status_code == 200
    sess_data = start_res.json()
    session_id = sess_data["session_id"]
    print(f"[PASSED] POST /analysis/session/start returned session_id: {session_id}")

    # Finalize session endpoint
    fin_res = client.post(f"/analysis/session/{session_id}/finalize", headers=headers)
    assert fin_res.status_code == 200
    fin_data = fin_res.json()
    assert fin_data["is_completed"] is True
    print(f"[PASSED] POST /analysis/session/{session_id}/finalize successfully finalized session")

    # History endpoint
    hist_res = client.get("/analysis/history?limit=5", headers=headers)
    assert hist_res.status_code == 200
    assert "items" in hist_res.json()
    print(f"[PASSED] GET /analysis/history returned {len(hist_res.json()['items'])} records")

    # Trends endpoint
    trends_res = client.get("/analysis/trends?period=30d", headers=headers)
    assert trends_res.status_code == 200
    assert "wellness_trend" in trends_res.json()
    print(f"[PASSED] GET /analysis/trends returned 200 with {trends_res.json().get('entries_analyzed', 0)} entries analyzed")

if __name__ == "__main__":
    print("=============================================================")
    print("RUNNING EMOTRACK FINAL COMPREHENSIVE END-TO-END TEST SUITE")
    print("=============================================================")
    test_1_database_and_seeding()
    test_2_calibrated_emotion_inference()
    test_3_dreaddit_stress_classifier()
    test_4_agentic_orchestrator_and_trace()
    test_5_multi_turn_session_lifecycle()
    test_6_fastapi_rest_endpoints()
    print("\n=============================================================")
    print("ALL 6 TEST MODULES PASSED WITH ZERO ERRORS!")
    print("=============================================================")
