# backend/ml/agents/insight_agent.py
"""
Insight Agent
Generates the personalized AI narrative ('What EmoTrack noticed')
synthesizing current emotion, stress, and trajectory history with humility.
"""

from typing import Dict, Any

class InsightAgent:
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        emotion = state.get("emotion", "Neutral")
        stress = state.get("stress", "Low")
        trend = state.get("trend", {})
        trend_dir = trend.get("direction", "Stable")
        history = state.get("history", [])
        text = state.get("text", "").lower()

        context = None
        if any(word in text for word in ["exam", "assignment", "thesis", "class", "semester"]):
            context = "academic responsibilities"
        elif any(word in text for word in ["manager", "job", "office", "client", "meeting", "deadline"]):
            context = "work responsibilities"
        elif any(word in text for word in ["health", "sick", "ill", "pain", "doctor"]):
            context = "health-related concerns"
        elif any(word in text for word in ["lonely", "alone", "isolated", "friends", "family", "relationship"]):
            context = "social connection"

        # Construct thoughtful, non-authoritative observation
        if emotion == "Fear" and stress == "High":
            insight = (
                f"Your recent entry reflects increased concern around {context or 'upcoming responsibilities'}. "
                "While today's reflection shows heightened stress signals, your previous logs suggest these spikes "
                "tend to be temporary and ease once the initial task is broken into smaller steps."
            )
        elif emotion == "Joy":
            insight = (
                "A clear positive shift is apparent in your language today. "
                f"{('This reflection especially highlights ' + context + ' as meaningful to you. ') if context else ''}"
                "Moments of completion, social connection, and quiet progress can be stabilizing factors in your wellness patterns."
            )
        elif emotion == "Sadness":
            insight = (
                f"Your reflection suggests lower emotional energy or fatigue today{(' in relation to ' + context) if context else ''}. "
                "Patterns like this often appear following periods of prolonged effort and typically benefit from "
                "unpressured downtime."
            )
        elif emotion == "Anger":
            insight = (
                "Your entry expresses acute frustration, often associated with unexpected blockers or friction. "
                "Acknowledging the frustration without feeling rushed to solve everything right away can help restore equilibrium."
            )
        else:
            insight = (
                "Your thoughts reflect an even, steady tone. "
                "Maintaining regular routines during calm intervals helps reinforce resilience during future busy periods."
            )

        if trend_dir == "Improving":
            insight += " Overall, your multi-entry wellness pattern shows gentle positive momentum."
        elif trend_dir == "Needs Attention":
            insight += " Over the past several reflections, stress signals have been slightly elevated."

        state["insights"] = insight
        return state
