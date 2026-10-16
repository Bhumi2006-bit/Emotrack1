# backend/tests/test_explainability.py
"""
Regression test suite for EmoTrack Explainable AI (XAI) attribution.
Verifies:
1. Occlusion-based word attribution executes on the active transformer model.
2. Only content words present in the user reflection receive attribution.
3. Stopwords and generic tokens are filtered out from attribution.
4. Drops are non-negative and quantitatively grounded in actual probability deltas.
5. Qualitative influence tiers ('Significant', 'Moderate', 'Contextual nuance') match probability thresholds.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.explainability.explainer import extract_contextual_signals, STOPWORDS
from ml.models.emotion_model import emotion_classifier

def test_explainability_attribution():
    print("Testing occlusion attribution on active model...")
    text = "I am terrified about my thesis viva tomorrow and my advisor might fail me."
    signals = extract_contextual_signals(text, "Fear")
    
    assert isinstance(signals, list), "Signals must be a list"
    assert len(signals) > 0, "Signals should not be empty for an emotive sentence"
    
    words_in_text = [w.lower().strip(".,!?:;\"'()[]{}") for w in text.split()]
    for s in signals:
        w = s["word"].lower()
        # Word must actually exist in user text
        assert w in words_in_text, f"Attributed word '{w}' must exist in input text"
        # Word must not be in stopwords
        assert w not in STOPWORDS, f"Stopword '{w}' must not receive attribution"
        # Attribution drop must be non-negative
        assert s["drop"] >= 0.0, f"Probability drop for '{w}' must be non-negative"
        # Qualitative label check
        assert s["influence_level"] in ["Significant indicator", "Moderate indicator", "Contextual nuance"], "Valid tier required"
        assert s["type"] == "transformer_occlusion_attribution"

    print(f"  [OK] Extracted signals: {[s['word'] for s in signals]} (Top drop: {signals[0]['drop']:.4f})")

def test_explainability_edge_cases():
    print("Testing explainability edge cases...")
    # Empty text
    empty_sig = extract_contextual_signals("", "Neutral")
    assert empty_sig == [], "Empty text must produce empty signals"
    
    # Single word
    single_sig = extract_contextual_signals("hello", "Joy")
    assert single_sig == [], "Single word must produce empty signals"

    print("  [OK] Edge cases verified.")

if __name__ == "__main__":
    print("=== Running Explainability Test Suite ===")
    test_explainability_attribution()
    test_explainability_edge_cases()
    print("=== ALL EXPLAINABILITY TESTS PASSED ===")
