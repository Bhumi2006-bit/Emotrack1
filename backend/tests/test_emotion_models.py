# backend/tests/test_emotion_models.py
"""
Unit and Regression Tests for Emotion Classification Models:
1. Label Taxonomy (7 Ekman classes)
2. Probability distribution normalization (sum to 1.0)
3. Shannon Entropy uncertainty bounds [0.0, 1.0]
4. Ambiguity margin detection
5. Configurable backend switching and graceful fallback
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from ml.models.emotion_model import (
    TransformerEmotionClassifier,
    ALL_CLASSES,
    LABEL_MAP
)

def test_emotion_taxonomy():
    print("Testing emotion taxonomy...")
    assert len(ALL_CLASSES) == 7
    expected = {"Anger", "Disgust", "Fear", "Joy", "Neutral", "Sadness", "Surprise"}
    assert set(ALL_CLASSES) == expected
    print("  [OK] Taxonomy verified.")

def test_distilroberta_baseline_predict():
    print("Testing DistilRoBERTa predict contract...")
    clf = TransformerEmotionClassifier(backend="distilroberta")
    res = clf.predict("I am feeling thrilled and delighted about the good news!")
    
    assert res["primary_emotion"] == "Joy"
    assert res["confidence"] > 0.40
    assert 0.0 <= res["uncertainty_score"] <= 1.0
    assert "distribution" in res
    assert len(res["distribution"]) == 7
    total_p = sum(res["distribution"].values())
    assert abs(total_p - 1.0) < 0.02
    print("  [OK] DistilRoBERTa predict verified.")

def test_empty_input_handling():
    print("Testing empty input edge cases...")
    clf = TransformerEmotionClassifier(backend="distilroberta")
    res = clf.predict("")
    assert res["primary_emotion"] == "Neutral"
    assert res["is_ambiguous"] is True
    assert res["uncertainty_score"] >= 0.70
    print("  [OK] Empty input handling verified.")

def test_ensemble_or_fallback():
    print("Testing Ensemble backend...")
    clf = TransformerEmotionClassifier(backend="ensemble")
    res = clf.predict("I am terrified that I might fail tomorrow's test.")
    
    assert res["primary_emotion"] in ["Fear", "Sadness"]
    assert res["confidence"] > 0.30
    assert 0.0 <= res["uncertainty_score"] <= 1.0
    assert res["backend_type"] in ["ensemble", "distilroberta"]
    print(f"  [OK] Ensemble inference verified (Backend: {res['backend_type']}).")

def test_invalid_backend_graceful_fallback():
    print("Testing invalid backend graceful fallback...")
    clf = TransformerEmotionClassifier(backend="non_existent_model_xyz")
    assert clf.fallback_active is True
    assert clf.active_backend == "distilroberta"
    res = clf.predict("Everything is going well today.")
    assert res["primary_emotion"] in ALL_CLASSES
    print("  [OK] Graceful fallback verified.")

def test_get_label_probability():
    print("Testing get_label_probability...")
    clf = TransformerEmotionClassifier(backend="distilroberta")
    p = clf.get_label_probability("I am really happy today!", "Joy")
    assert 0.0 <= p <= 1.0
    assert p > 0.40
    print("  [OK] get_label_probability verified.")

def run_all():
    print("=== Running Emotion Models Test Suite ===")
    test_emotion_taxonomy()
    test_distilroberta_baseline_predict()
    test_empty_input_handling()
    test_ensemble_or_fallback()
    test_invalid_backend_graceful_fallback()
    test_get_label_probability()
    print("=== ALL EMOTION MODEL TESTS PASSED ===")

if __name__ == "__main__":
    run_all()
