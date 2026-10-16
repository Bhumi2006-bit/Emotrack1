# backend/services/multi_turn_service.py
"""
Multi-Turn Conversational Session Service.
Coordinates stateful multi-turn reflection dialogues, contextual reassessment,
agent orchestration, and persistence across turns.
"""

import uuid
import json
from typing import Dict, Any, Optional, List
from database.models import (
    get_user_by_id,
    save_analysis,
    get_analyses_for_user,
    save_conversation_session,
    get_conversation_session,
    update_conversation_session
)
from ml.agents.agent_state import AgentState, TurnRecord, TraceStep
from ml.agents.orchestrator import orchestrator

class MultiTurnService:
    @staticmethod
    def start_session(user_id: int, text: str) -> Dict[str, Any]:
        """
        Initiates Turn 1 of an empathetic reflection session.
        Runs initial inference and determines if follow-up clarification is warranted.
        """
        session_id = str(uuid.uuid4())
        user_history = get_analyses_for_user(user_id, limit=10)

        # Initialize Agent State
        state = AgentState(
            session_id=session_id,
            user_id=user_id,
            current_text=text,
            turn_count=1,
            user_history=user_history
        )
        turn_1 = TurnRecord(
            turn_number=1,
            user_text=text,
            turn_type="initial"
        )
        state.turns.append(turn_1)

        # Execute Turn Assessment through Agentic Orchestrator
        final_state = orchestrator.execute_turn_assessment(state, force_finalize=False)

        turns_payload = [t.dict() if hasattr(t, "dict") else t.model_dump() for t in final_state.turns]
        analysis_id = None

        if final_state.is_completed:
            # Assessment reached confidence threshold without needing follow-up
            analysis_id = MultiTurnService._persist_final_analysis(user_id, final_state)
            save_conversation_session(
                session_id=session_id,
                user_id=user_id,
                status="completed",
                turn_count=final_state.turn_count,
                initial_text=text,
                turns_data=turns_payload,
                final_analysis_id=analysis_id
            )
            return MultiTurnService._build_completed_response(session_id, final_state, analysis_id)

        # Clarifying question generated -> Persist active session and return question
        save_conversation_session(
            session_id=session_id,
            user_id=user_id,
            status="active",
            turn_count=final_state.turn_count,
            initial_text=text,
            turns_data=turns_payload,
            final_analysis_id=None
        )

        trace_dicts = [t.dict() if hasattr(t, "dict") else t.model_dump() for t in final_state.trace]
        return {
            "session_id": session_id,
            "is_completed": False,
            "turn_count": final_state.turn_count,
            "next_question": final_state.next_question,
            "initial_interpretation": final_state.initial_interpretation,
            "correction_acknowledgment": final_state.correction_acknowledgment,
            "rejected_emotions": final_state.rejected_emotions,
            "preliminary_emotion": final_state.final_primary_emotion,
            "preliminary_confidence": final_state.final_confidence,
            "preliminary_stress": final_state.stress_assessment["level"] if final_state.stress_assessment else "Moderate",
            "uncertainty_score": final_state.current_emotion.get("uncertainty_score", 0.0) if final_state.current_emotion else 0.0,
            "is_ambiguous": final_state.current_emotion.get("is_ambiguous", False) if final_state.current_emotion else False,
            "execution_trace": trace_dicts
        }

    @staticmethod
    def respond_to_session(user_id: int, session_id: str, text: str) -> Dict[str, Any]:
        """
        Accepts user's response to an assistant follow-up question.
        Reconstructs state, performs contextual reassessment, and advances the session.
        """
        session = get_conversation_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found.")
        if session["user_id"] != user_id:
            raise PermissionError("Unauthorized access to conversation session.")
        if session["status"] == "completed":
            raise ValueError("Session is already completed.")

        # Reconstruct Agent State from stored session
        stored_turns = [TurnRecord(**t) for t in session.get("turns_data", [])]
        user_history = get_analyses_for_user(user_id, limit=10)

        # Collect past questions and rejected emotions
        past_questions = [t.assistant_question for t in stored_turns if t.assistant_question]
        past_rejected = []
        for t in stored_turns:
            for r in t.rejected_emotions:
                if r not in past_rejected:
                    past_rejected.append(r)

        next_turn_number = len(stored_turns) + 1
        new_turn = TurnRecord(
            turn_number=next_turn_number,
            user_text=text,
            turn_type="follow_up",
            rejected_emotions=list(past_rejected)
        )
        stored_turns.append(new_turn)

        state = AgentState(
            session_id=session_id,
            user_id=user_id,
            current_text=text,
            turns=stored_turns,
            turn_count=next_turn_number,
            user_history=user_history,
            asked_questions=past_questions,
            rejected_emotions=past_rejected
        )

        # Restore initial turn emotion
        if stored_turns:
            state.initial_emotion = {
                "primary_emotion": stored_turns[0].primary_emotion,
                "confidence": stored_turns[0].confidence,
                "distribution": stored_turns[0].emotion_distribution
            }

        # Reset current_emotion so model reassesses the new input with context
        state.current_emotion = None
        state.stress_assessment = None

        # Execute turn assessment
        final_state = orchestrator.execute_turn_assessment(state, force_finalize=False)
        turns_payload = [t.dict() if hasattr(t, "dict") else t.model_dump() for t in final_state.turns]

        if final_state.is_completed:
            analysis_id = MultiTurnService._persist_final_analysis(user_id, final_state)
            update_conversation_session(
                session_id=session_id,
                status="completed",
                turn_count=final_state.turn_count,
                turns_data=turns_payload,
                final_analysis_id=analysis_id
            )
            return MultiTurnService._build_completed_response(session_id, final_state, analysis_id)

        # Continue with another follow-up question
        update_conversation_session(
            session_id=session_id,
            status="active",
            turn_count=final_state.turn_count,
            turns_data=turns_payload,
            final_analysis_id=None
        )

        trace_dicts = [t.dict() if hasattr(t, "dict") else t.model_dump() for t in final_state.trace]
        return {
            "session_id": session_id,
            "is_completed": False,
            "turn_count": final_state.turn_count,
            "next_question": final_state.next_question,
            "initial_interpretation": final_state.initial_interpretation,
            "correction_acknowledgment": final_state.correction_acknowledgment,
            "rejected_emotions": final_state.rejected_emotions,
            "preliminary_emotion": final_state.final_primary_emotion,
            "preliminary_confidence": final_state.final_confidence,
            "preliminary_stress": final_state.stress_assessment["level"] if final_state.stress_assessment else "Moderate",
            "uncertainty_score": final_state.current_emotion.get("uncertainty_score", 0.0) if final_state.current_emotion else 0.0,
            "is_ambiguous": final_state.current_emotion.get("is_ambiguous", False) if final_state.current_emotion else False,
            "execution_trace": trace_dicts
        }

    @staticmethod
    def finalize_session(user_id: int, session_id: str) -> Dict[str, Any]:
        """
        Forces early finalization when the user explicitly requests 'Finish assessment now'.
        """
        session = get_conversation_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found.")
        if session["user_id"] != user_id:
            raise PermissionError("Unauthorized access to conversation session.")

        if session["status"] == "completed" and session.get("final_analysis_id"):
            from database.models import get_analysis_by_id
            analysis = get_analysis_by_id(session["final_analysis_id"])
            return {
                "session_id": session_id,
                "is_completed": True,
                "analysis_id": session["final_analysis_id"],
                "analysis": analysis
            }

        stored_turns = [TurnRecord(**t) for t in session.get("turns_data", [])]
        user_history = get_analyses_for_user(user_id, limit=10)

        past_questions = [t.assistant_question for t in stored_turns if t.assistant_question]
        past_rejected = []
        for t in stored_turns:
            for r in t.rejected_emotions:
                if r not in past_rejected:
                    past_rejected.append(r)

        state = AgentState(
            session_id=session_id,
            user_id=user_id,
            current_text=stored_turns[-1].user_text if stored_turns else session.get("initial_text", ""),
            turns=stored_turns,
            turn_count=len(stored_turns),
            user_history=user_history,
            asked_questions=past_questions,
            rejected_emotions=past_rejected
        )

        if stored_turns:
            state.initial_emotion = {
                "primary_emotion": stored_turns[0].primary_emotion,
                "confidence": stored_turns[0].confidence,
                "distribution": stored_turns[0].emotion_distribution
            }

        final_state = orchestrator.execute_turn_assessment(state, force_finalize=True)
        turns_payload = [t.dict() if hasattr(t, "dict") else t.model_dump() for t in final_state.turns]

        analysis_id = MultiTurnService._persist_final_analysis(user_id, final_state)
        update_conversation_session(
            session_id=session_id,
            status="completed",
            turn_count=final_state.turn_count,
            turns_data=turns_payload,
            final_analysis_id=analysis_id
        )

        return MultiTurnService._build_completed_response(session_id, final_state, analysis_id)

    @staticmethod
    def _persist_final_analysis(user_id: int, state: AgentState) -> Optional[int]:
        """
        Persists synthesized final analysis to SQLite database if history saving is enabled.
        """
        user = get_user_by_id(user_id)
        if not user or not user.get("save_history", 1):
            return None

        # Build concatenated user narrative across all turns
        all_narrative = " ".join([t.user_text for t in state.turns]) if state.turns else state.current_text

        analysis_id = save_analysis(
            user_id=user_id,
            input_text=all_narrative,
            primary_emotion=state.final_primary_emotion,
            emotion_confidence=state.final_confidence,
            emotion_distribution=state.final_emotion_distribution,
            stress_level=state.stress_assessment.get("level", "Moderate") if state.stress_assessment else "Moderate",
            stress_confidence=state.stress_assessment.get("confidence", 0.5) if state.stress_assessment else 0.5,
            wellness_score=state.wellness_assessment.get("score", 70) if state.wellness_assessment else 70,
            wellness_status=state.wellness_assessment.get("status", "Balanced") if state.wellness_assessment else "Balanced",
            trend_direction=state.trend_assessment.get("direction", "Stable") if state.trend_assessment else "Stable",
            trend_entries=state.trend_assessment.get("based_on_entries", 0) if state.trend_assessment else 0,
            insight=state.insights or "Multi-turn reflection completed.",
            recommendations=state.recommendations,
            context_signals={
                "xai_attributions": state.xai_signals,
                "turns_count": len(state.turns),
                "turns_history": [{"turn": t.turn_number, "emotion": t.primary_emotion, "text": t.user_text} for t in state.turns]
            }
        )
        return analysis_id

    @staticmethod
    def _build_completed_response(session_id: str, state: AgentState, analysis_id: Optional[int]) -> Dict[str, Any]:
        """
        Formats final API response for completed session.
        """
        all_text = " ".join([t.user_text for t in state.turns]) if state.turns else state.current_text
        trace_dicts = [t.dict() if hasattr(t, "dict") else t.model_dump() for t in state.trace]
        turns_summary = [
            {
                "turn": t.turn_number,
                "text": t.user_text,
                "primary_emotion": t.primary_emotion,
                "confidence": t.confidence,
                "assistant_question": t.assistant_question
            }
            for t in state.turns
        ]

        return {
            "session_id": session_id,
            "is_completed": True,
            "analysis_id": analysis_id,
            "saved_to_history": bool(analysis_id),
            "input_text": all_text,
            "turns_count": len(state.turns),
            "turn_count": len(state.turns),
            "turns": turns_summary,
            "emotion": {
                "label": state.final_primary_emotion,
                "confidence": state.final_confidence,
                "distribution": state.final_emotion_distribution
            },
            "stress": {
                "level": state.stress_assessment.get("level", "Moderate") if state.stress_assessment else "Moderate",
                "confidence": state.stress_assessment.get("confidence", 0.5) if state.stress_assessment else 0.5,
                "probability": state.stress_assessment.get("probability", 0.5) if state.stress_assessment else 0.5,
                "explanation": (state.stress_assessment.get("explanation") or state.stress_assessment.get("model_source", "")) if state.stress_assessment else ""
            },
            "wellness": {
                "score": state.wellness_assessment.get("score", 70) if state.wellness_assessment else 70,
                "status": state.wellness_assessment.get("status", "Balanced") if state.wellness_assessment else "Balanced",
                "description": state.wellness_assessment.get("description", "") if state.wellness_assessment else "",
                "disclaimer": "Non-diagnostic wellness indicator derived from application signals and self-reported reflections."
            },
            "trend": state.trend_assessment or {"direction": "Stable", "based_on_entries": 0},
            "insight": state.insights,
            "recommendations": state.recommendations,
            "recommendation_objects": [
                {"title": r.split(":")[0].strip() if ":" in r else r, "description": r.split(":")[1].strip() if ":" in r else r, "category": "Mindfulness"}
                for r in state.recommendations
            ],
            "explanation": {
                "summary": state.conversational_explanation,
                "signals": state.xai_signals
            },
            "conversational_explanation": state.conversational_explanation,
            "xai_signals": state.xai_signals,
            "execution_trace": trace_dicts
        }
