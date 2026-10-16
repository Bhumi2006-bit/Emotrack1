# backend/services/wellness_service.py
"""
Wellness Indicator Service (Application-Defined, Non-Diagnostic)

Calculates a supportive self-reflection wellness score bounded strictly within [0, 100].
Combines:
1. Baseline anchor grounded in Dreaddit stress level (Low: 75, Moderate: 55, High: 35)
2. Emotion valence offset scaled with classification confidence (without confidence inversion)
3. Deterministic exponential moving average smoothing against past observations
4. Explicit non-diagnostic notice
"""

from typing import Dict, Any, List, Optional

EMOTION_OFFSETS = {
    "Joy": +15,
    "Neutral": +5,
    "Surprise": +2,
    "Sadness": -10,
    "Anger": -12,
    "Fear": -15,
    "Disgust": -12
}

NON_DIAGNOSTIC_DISCLAIMER = (
    "This is an experimental application-defined wellness indicator designed for mindful self-reflection. "
    "It is not a clinical scale, psychological diagnostic tool, or substitute for professional mental healthcare."
)

def calculate_wellness_indicator(
    primary_emotion: str,
    emotion_confidence: float,
    stress_level: str,
    stress_confidence: float,
    history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Computes application-defined wellness score bounded in [0, 100] and status pattern.
    """
    # 1. Base anchor grounded in stress level
    if stress_level == "High":
        base = 35
    elif stress_level == "Moderate":
        base = 55
    else:  # Low
        base = 75

    # 2. Emotion valence contribution scaled by confidence (clamped [0.0, 1.0])
    conf = max(0.0, min(1.0, float(emotion_confidence or 0.5)))
    offset = EMOTION_OFFSETS.get(primary_emotion, 0)
    raw_score = base + int(round(offset * conf))

    # 3. Deterministic multi-entry history smoothing (70% current, 30% recent baseline)
    if history and len(history) >= 2:
        recent_scores = [
            h.get("wellness_score") for h in history[:3]
            if isinstance(h.get("wellness_score"), (int, float))
        ]
        if recent_scores:
            avg_recent = sum(recent_scores) / len(recent_scores)
            smoothed_score = int(round(0.70 * raw_score + 0.30 * avg_recent))
        else:
            smoothed_score = raw_score
    else:
        smoothed_score = raw_score

    # 4. Strict clamping within [0, 100]
    final_score = max(0, min(100, smoothed_score))

    # 5. Non-clinical categorical pattern
    if final_score >= 70:
        status = "Positive Pattern"
        description = "Your reflection reflects an uplifting, restorative, or productive pattern."
    elif final_score >= 50:
        status = "Balanced"
        description = "Your recent entries indicate a relatively stable, balanced equilibrium."
    else:
        status = "Needs Reflection"
        description = "Elevated strain or fatigue patterns detected in this reflection. A mindful pause or grounding activity may be helpful."

    return {
        "score": final_score,
        "status": status,
        "description": description,
        "disclaimer": NON_DIAGNOSTIC_DISCLAIMER
    }
