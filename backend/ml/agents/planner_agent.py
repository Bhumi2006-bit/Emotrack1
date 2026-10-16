# backend/ml/agents/planner_agent.py
"""
Planner Agent
Responsible for inspecting input reflections, validating text length/content,
and preparing pipeline execution context.
"""

from typing import Dict, Any

class PlannerAgent:
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        text = state.get("text", "").strip()
        state["char_count"] = len(text)
        state["word_count"] = len(text.split())
        state["execution_plan"] = [
            "detect_emotions",
            "classify_stress",
            "evaluate_wellness",
            "compute_trajectory_trend",
            "synthesize_insights",
            "filter_recommendations",
            "extract_prototype_signals"
        ]
        return state
