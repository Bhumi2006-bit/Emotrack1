# backend/tests/test_wellness_service.py
"""
Unit Tests for Wellness Indicator Formula:
1. Strict clamping between 0 and 100
2. Baseline stress anchoring (Low: 75, Moderate: 55, High: 35)
3. Emotion valence scaling without confidence inversion
4. Deterministic multi-entry trajectory smoothing
5. Non-diagnostic disclaimer presence
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from services.wellness_service import calculate_wellness_indicator

def test_extreme_bounds():
    print("Testing extreme bounds [0, 100]...")
    # Worst case: High stress, Fear with 1.0 confidence
    worst = calculate_wellness_indicator("Fear", 1.0, "High", 1.0)
    assert 0 <= worst["score"] <= 100
    assert worst["score"] == 20
    assert worst["status"] in ["Needs Reflection", "Needs Attention"]

    # Best case: Low stress, Joy with 1.0 confidence
    best = calculate_wellness_indicator("Joy", 1.0, "Low", 1.0)
    assert 0 <= best["score"] <= 100
    assert best["score"] == 90
    assert best["status"] == "Positive Pattern"

    # Neutral baseline: Low stress, Neutral with 0.8 confidence
    neutral = calculate_wellness_indicator("Neutral", 0.8, "Low", 0.8)
    assert 70 <= neutral["score"] <= 85
    assert neutral["status"] == "Positive Pattern"
    print("  [OK] Extreme bounds verified.")

def test_confidence_scaling():
    print("Testing confidence scaling without inversions...")
    # Low confidence on Fear should produce less negative valence than high confidence on Fear
    high_conf_fear = calculate_wellness_indicator("Fear", 0.9, "Moderate", 0.9)
    low_conf_fear = calculate_wellness_indicator("Fear", 0.1, "Moderate", 0.9)

    # Moderate base is 55. High conf fear: 55 - 14 = 41. Low conf fear: 55 - 2 = 53.
    assert high_conf_fear["score"] < low_conf_fear["score"]
    assert 0 <= high_conf_fear["score"] <= 100
    assert 0 <= low_conf_fear["score"] <= 100
    print("  [OK] Confidence scaling verified.")

def test_historical_smoothing():
    print("Testing deterministic history smoothing...")
    history = [
        {"wellness_score": 80},
        {"wellness_score": 85},
        {"wellness_score": 82}
    ]
    # Current acute event is High stress / Fear (raw = 20)
    res_smoothed = calculate_wellness_indicator("Fear", 1.0, "High", 1.0, history=history)
    # Expected: 0.70 * 20 + 0.30 * 82.33 = 14 + 24.7 = ~39
    assert res_smoothed["score"] > 20  # Smoothed towards baseline
    assert res_smoothed["score"] < 50
    print(f"  [OK] History smoothing verified (Raw: 20 -> Smoothed: {res_smoothed['score']}).")

def test_non_diagnostic_notice():
    print("Testing non-diagnostic notice...")
    res = calculate_wellness_indicator("Joy", 0.9, "Low", 0.9)
    assert "disclaimer" in res
    assert "not a clinical scale" in res["disclaimer"].lower() or "not constitute" in res["disclaimer"].lower() or "application-defined" in res["disclaimer"].lower()
    print("  [OK] Disclaimer verified.")

def run_all():
    print("=== Running Wellness Indicator Test Suite ===")
    test_extreme_bounds()
    test_confidence_scaling()
    test_historical_smoothing()
    test_non_diagnostic_notice()
    print("=== ALL WELLNESS TESTS PASSED ===")

if __name__ == "__main__":
    run_all()
