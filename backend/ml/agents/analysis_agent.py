# backend/ml/agents/analysis_agent.py
"""
Analysis Agent
Coordinates model predictions for emotion and stress, and derives wellness and trend states.
"""

from typing import Dict, Any
from ml.models.emotion_model import emotion_classifier
from ml.models.stress_model import stress_classifier
from services.wellness_service import calculate_wellness_indicator
from services.trend_service import calculate_longitudinal_trend

class AnalysisAgent:
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        text = state.get("text", "")
        history = state.get("history", [])

        # 1. Run Emotion Model
        emo_res = emotion_classifier.predict(text)
        state["emotion"] = emo_res["primary_emotion"]
        state["emotion_confidence"] = emo_res["confidence"]
        state["emotion_distribution"] = emo_res["distribution"]

        # 2. Run Stress Model
        stress_res = stress_classifier.predict(text, emotion_distribution=state["emotion_distribution"])
        state["stress"] = stress_res["level"]
        state["stress_confidence"] = stress_res["confidence"]
        state["stress_explanation"] = stress_res["explanation"]

        # 3. Calculate Wellness Indicator
        wellness_res = calculate_wellness_indicator(
            primary_emotion=state["emotion"],
            emotion_confidence=state["emotion_confidence"],
            stress_level=state["stress"],
            stress_confidence=state["stress_confidence"],
            history=history
        )
        state["wellness_score"] = wellness_res["score"]
        state["wellness_status"] = wellness_res["status"]
        state["wellness_description"] = wellness_res["description"]

        # 4. Calculate Longitudinal Trend
        trend_res = calculate_longitudinal_trend(
            current_score=state["wellness_score"],
            history=history
        )
        state["trend"] = trend_res

        return state
