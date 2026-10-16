# backend/test_backend.py
import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from database.connection import init_db
from database.seed_data import seed_database
from routes.auth import login, LoginRequest
from routes.dashboard import get_dashboard_summary
from services.analysis_service import process_user_reflection
from services.trend_service import calculate_longitudinal_trend
from ml.models.emotion_model import emotion_classifier
from ml.models.stress_model import stress_classifier

def run_tests():
    print("--- 1. Testing Database & Seeding ---")
    init_db()
    seed_database()
    print("[OK] DB and seed passed.")

    print("\n--- 2. Testing Authentication ---")
    login_res = login(LoginRequest(email="demo@emotrack.ai", password="demo123"))
    assert "access_token" in login_res
    assert login_res["user"]["name"] == "Bhumi"
    print(f"[OK] Auth passed. User: {login_res['user']['name']}, Streak: {login_res['user']['streak_days']}")

    print("\n--- 3. Testing Dashboard API ---")
    dash = get_dashboard_summary(user_id=1)
    assert dash["wellness"]["score"] >= 0 and dash["wellness"]["score"] <= 100
    assert 1 <= len(dash["weekly_trend"]) <= 7
    assert len(dash["emotion_distribution"]) >= 1
    assert len(dash["recent_analyses"]) > 0
    print(f"[OK] Dashboard passed. Wellness: {dash['wellness']['score']}, Emotion: {dash['emotion']['label']}, Entries: {dash['total_entries']}")

    print("\n--- 4. Testing Real DistilRoBERTa Emotion Pipeline & Preprocessing ---")
    sanity_sentences = [
        ("I am angry and frustrated by work.", ["Anger"]),
        ("I am ngry and frustated by work.", ["Anger"]),
        ("I am not happy today.", ["Sadness", "Neutral"]),
        ("I am furious about what happened.", ["Anger"]),
        ("I am scared about my exams.", ["Fear"]),
        ("I feel completely hopeless and sad.", ["Sadness"]),
        ("I can't believe it, this is amazing!", ["Joy", "Surprise"]),
        ("I had pizza for lunch.", ["Neutral", "Joy"]),
        ("i am loving the day today", ["Joy"])
    ]

    for sent, expected_emotions in sanity_sentences:
        pred = emotion_classifier.predict(sent)
        emo = pred["primary_emotion"]
        conf = pred["confidence"]
        dist = pred["distribution"]
        dist_sum = sum(dist.values())
        assert 0.98 <= dist_sum <= 1.02, f"Distribution sum was {dist_sum} for {sent}"
        assert emo in ["Joy", "Neutral", "Sadness", "Fear", "Anger", "Surprise", "Disgust"]
        assert 0.0 <= conf <= 1.0
        # Check against expected semantic emotion category
        assert emo in expected_emotions, f"Expected {expected_emotions} for '{sent}', got {emo} ({conf*100:.1f}%)"
        print(f"[OK] \"{sent}\" -> {emo} ({conf*100:.1f}%) [Softmax sum: {dist_sum:.3f}]")

    print("\n--- 5. Testing End-to-End Analysis Pipeline & Explainability ---")
    test_text = "I am angry and frustrated by work."
    analysis_res = process_user_reflection(user_id=1, text=test_text)
    assert "analysis_id" in analysis_res
    assert analysis_res["emotion"]["label"] == "Anger"
    assert analysis_res["stress"]["level"] in ["Low", "Moderate", "High"]
    assert 0 <= analysis_res["wellness"]["score"] <= 100
    assert analysis_res["wellness"]["status"] in ["Positive Pattern", "Balanced", "Needs Attention"]
    assert "At Risk" not in analysis_res["wellness"]["status"]
    
    # Check that explainability words actually exist in the input text!
    signals = analysis_res["explanation"]["signals"]
    input_words_lower = [w.lower() for w in test_text.split()]
    for sig in signals:
        clean_sig = sig["word"].lower().strip(".,!?:;\"'()[]{}")
        assert any(clean_sig in w for w in input_words_lower), f"Attributed word '{sig['word']}' was not in input text!"
    print(f"[OK] End-to-end analysis passed. Signals: {[s['word'] for s in signals]}")

    print("\n--- 6. Testing Multi-Entry Trend Threshold Logic ---")
    # For < 3 entries
    sparse_trend = calculate_longitudinal_trend(current_score=60, history=[{"wellness_score": 62}])
    assert sparse_trend["direction"] == "Insufficient Data"
    assert "Not enough historical data" in sparse_trend["message"]
    print("[OK] Trend < 3 entries correctly returned 'Insufficient Data'")

    # For >= 3 entries
    rich_trend = calculate_longitudinal_trend(
        current_score=75,
        history=[{"wellness_score": 60}, {"wellness_score": 63}, {"wellness_score": 68}]
    )
    assert rich_trend["direction"] in ["Improving", "Stable", "Needs Attention"]
    assert rich_trend["based_on_entries"] >= 3
    print(f"[OK] Trend >= 3 entries correctly computed trajectory: {rich_trend['direction']} (based on {rich_trend['based_on_entries']} entries)")

    print("\n=======================================================")
    print("ALL TESTS PASSED WITH REAL DISTILROBERTA TRANSFORMER")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
