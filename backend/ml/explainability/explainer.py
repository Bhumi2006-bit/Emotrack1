# backend/ml/explainability/explainer.py
"""
Contextual Model Attribution & Explainability

Uses feature occlusion (perturbation-based sensitivity analysis) directly on the
deployed transformer model. Only words that ACTUALLY appear in the user's reflection
are evaluated. Zero hardcoded dictionary lookups.
"""

from typing import List, Dict, Any
import re
import torch
import torch.nn.functional as F

STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "you", "your", "he", "she",
    "it", "its", "they", "them", "a", "an", "the", "and", "or", "but", "if",
    "because", "as", "until", "while", "of", "at", "by", "for", "with", "about",
    "against", "between", "into", "through", "during", "before", "after", "to",
    "from", "in", "out", "on", "off", "over", "under", "then", "once", "here",
    "there", "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
    "too", "very", "can", "will", "just", "should", "now", "am", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do",
    "does", "did", "doing", "feeling", "feel", "feels", "felt", "everything",
    "something", "anything", "really", "much", "many", "even", "also", "would",
    "could", "im", "ive", "today", "tomorrow", "yesterday", "day", "days", "lot"
}

def extract_contextual_signals(text: str, detected_emotion: str) -> List[Dict[str, Any]]:
    """
    Extracts genuine contextual attribution by measuring occlusion probability drops
    on the deployed transformer model. Evaluates ONLY content words present in user's text.
    Returns qualitative influence labels and relative sensitivity scores.
    """
    from ml.models.emotion_model import emotion_classifier, LABEL_MAP

    words = text.strip().split()
    if len(words) <= 1:
        return []

    # 1. Base probability with full text
    base_prob = emotion_classifier.get_label_probability(text, detected_emotion)

    # 2. Occlusion test on each content word from the user's actual input
    signals = []
    seen_words = set()

    for i, raw_word in enumerate(words):
        clean_word = re.sub(r'[^a-zA-Z0-9\'-]', '', raw_word).lower()
        if not clean_word or len(clean_word) < 3 or clean_word in STOPWORDS:
            continue
        if clean_word in seen_words:
            continue
        seen_words.add(clean_word)

        # Create text omitting this word
        occluded_text = " ".join([w for j, w in enumerate(words) if j != i])
        if not occluded_text.strip():
            continue

        occ_prob = emotion_classifier.get_label_probability(occluded_text, detected_emotion)

        # Probability drop when this word was removed
        drop = max(0.0, base_prob - occ_prob)
        signals.append({
            "word": raw_word.strip(".,!?:;\"'()[]{}"),
            "drop": drop
        })

    # Sort descending by sensitivity drop
    signals.sort(key=lambda x: x["drop"], reverse=True)

    top_signals = signals[:4]
    results = []
    for s in top_signals:
        raw_drop = s["drop"]
        if raw_drop >= 0.08:
            influence = "Significant indicator"
            weight = min(0.85, 0.50 + round(raw_drop * 2, 2))
        elif raw_drop >= 0.03:
            influence = "Moderate indicator"
            weight = min(0.60, 0.30 + round(raw_drop * 2, 2))
        else:
            influence = "Contextual nuance"
            weight = max(0.15, round(raw_drop * 2, 2)) if raw_drop > 0.001 else 0.20

        results.append({
            "word": s["word"],
            "weight": weight,
            "drop": round(raw_drop, 4),
            "influence_level": influence,
            "type": "transformer_occlusion_attribution"
        })

    return results
