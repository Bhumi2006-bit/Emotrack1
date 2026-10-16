# backend/ml/agents/recommendation_agent.py
"""
Recommendation Agent
Selects non-prescriptive, supportive self-care suggestions based on state.
"""

from typing import Dict, Any
from services.recommendation_service import generate_recommendations

class RecommendationAgent:
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        text = state.get("text", "")
        emotion = state.get("emotion", "Neutral")
        stress = state.get("stress", "Low")

        recs = generate_recommendations(text, emotion, stress, limit=3)
        state["recommendation_objects"] = recs
        state["recommendations"] = [f"{r['title']}: {r['description']}" for r in recs]
        return state
