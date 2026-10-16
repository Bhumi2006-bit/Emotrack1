# backend/services/analysis_service.py
"""
Analysis Service Coordinator
Bridges REST API requests, ML & Agentic workflows, and Database persistence.
"""

from typing import Dict, Any, List
from database.models import get_analyses_for_user, save_analysis, get_user_by_id
from ml.agents.orchestrator import orchestrator

def process_user_reflection(user_id: int, text: str) -> Dict[str, Any]:
    """
    Coordinates the full analysis pipeline for a user's text reflection.
    """
    # 1. Fetch user's recent historical analyses for context & multi-entry trend calculation
    history = get_analyses_for_user(user_id, limit=10)

    # 2. Run Agentic Orchestrator
    state = orchestrator.run(text=text, user_id=user_id, history=history)

    # 3. Persist Analysis Record to Database
    user = get_user_by_id(user_id)
    analysis_id = None
    if user and user.get("save_history", 1):
        analysis_id = save_analysis(
            user_id=user_id, input_text=text, primary_emotion=state["emotion"],
            emotion_confidence=state["emotion_confidence"], emotion_distribution=state["emotion_distribution"],
            stress_level=state["stress"], stress_confidence=state["stress_confidence"],
            wellness_score=state["wellness_score"], wellness_status=state["wellness_status"],
            trend_direction=state["trend"]["direction"], trend_entries=state["trend"]["based_on_entries"],
            insight=state["insights"], recommendations=state["recommendations"], context_signals=state["context_signals"]
        )

    # 4. Return structured response matching blueprint
    return {
        "analysis_id": analysis_id,
        "saved_to_history": bool(analysis_id),
        "input_text": text,
        "emotion": {
            "label": state["emotion"],
            "confidence": state["emotion_confidence"],
            "distribution": state["emotion_distribution"]
        },
        "stress": {
            "level": state["stress"],
            "confidence": state["stress_confidence"],
            "explanation": state.get("stress_explanation", "")
        },
        "wellness": {
            "score": state["wellness_score"],
            "status": state["wellness_status"],
            "description": state.get("wellness_description", ""),
            "disclaimer": "Non-diagnostic wellness indicator derived from application signals and self-reported reflections."
        },
        "trend": state["trend"],
        "insight": state["insights"],
        "recommendations": state["recommendations"],
        "recommendation_objects": state.get("recommendation_objects", []),
        "explanation": {
            "summary": state["explanation"],
            "signals": state.get("context_signals", {}).get("xai_attributions", [])
        },
        "conversational_explanation": state["explanation"],
        "context_signals": state.get("context_signals", {}),
        "execution_trace": state.get("execution_trace", [])
    }


