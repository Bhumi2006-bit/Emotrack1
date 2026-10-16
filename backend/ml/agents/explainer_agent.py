# backend/ml/agents/explainer_agent.py
"""
Explainer Agent
Produces prototype contextual signal attribution for transparency.
"""

from typing import Dict, Any
from ml.explainability.explainer import extract_contextual_signals

class ExplainerAgent:
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        text = state.get("text", "")
        emotion = state.get("emotion", "Neutral")

        signals = extract_contextual_signals(text, emotion)
        state["explanation"] = {
            "type": "prototype_contextual_evidence",
            "detected_target": emotion,
            "signals": signals,
            "note": "Prototype signal attribution. Full model token attribution (SHAP/IG) to be connected with fine-tuned transformer."
        }
        state["context_signals"] = signals
        return state
