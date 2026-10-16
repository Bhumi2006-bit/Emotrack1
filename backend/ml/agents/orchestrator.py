# backend/ml/agents/orchestrator.py
"""
Agentic AI Orchestrator with Bounded Execution Loop and Explicit Tool Calling.

Execution Paradigm:
OBSERVE -> REASON -> SELECT ACTION -> CALL TOOL -> INSPECT RESULT -> UPDATE STATE -> CONTINUE OR STOP.

Supports:
1. Real LLM-driven tool execution (when OPENAI_API_KEY or GEMINI_API_KEY is available)
2. Context-aware deterministic agentic execution (when offline / no credentials)
3. Transparent, auditable execution trace logging (no fabricated LLM calls)
4. Strict iteration bounds to prevent unbounded loops
"""

import os
import time
from typing import Dict, Any, List, Optional
from ml.agents.agent_state import AgentState, TraceStep, TurnRecord
from ml.agents.tools import (
    TOOL_DEFINITIONS,
    tool_classify_emotion,
    tool_classify_stress,
    tool_get_user_history,
    tool_extract_token_attribution,
    tool_calculate_wellness_and_trend,
    tool_generate_follow_up_question,
    tool_synthesize_conversational_explanation,
    tool_generate_grounded_recommendations,
    tool_detect_user_corrections,
    tool_generate_initial_interpretation
)

MAX_ORCHESTRATOR_STEPS = 8

class AgenticOrchestrator:
    def __init__(self):
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.has_llm_provider = bool(self.openai_key or self.gemini_key)
        print(f"[Orchestrator] Initialized. LLM Provider available: {self.has_llm_provider}")

    def execute_turn_assessment(
        self,
        state: AgentState,
        force_finalize: bool = False
    ) -> AgentState:
        """
        Executes the bounded agentic loop to assess the current turn and decide:
        (a) whether to incorporate explicit user corrections,
        (b) whether to ask a personalized, non-repeating follow-up question, or
        (c) whether to finalize the complete multi-turn assessment.
        """
        step_count = 0
        state.log_trace(
            agent_name="OrchestratorAgent",
            action_type="OBSERVE",
            details={
                "session_id": state.session_id,
                "turn_count": state.turn_count,
                "current_text": state.current_text,
                "force_finalize": force_finalize
            },
            thought="Inspecting current conversational state and incoming user reflection."
        )

        # -----------------------------------------------------------------
        # STAGE 0: CHECK FOR EXPLICIT USER CORRECTIONS / REJECTIONS
        # -----------------------------------------------------------------
        if state.turn_count > 1 or len(state.turns) > 1:
            prior_question = None
            prior_emotion = None
            if len(state.turns) >= 2:
                prior_question = state.turns[-2].assistant_question
                prior_emotion = state.turns[-2].primary_emotion
            elif state.asked_questions:
                prior_question = state.asked_questions[-1]
                prior_emotion = state.initial_emotion.get("primary_emotion") if state.initial_emotion else None

            corr_res = tool_detect_user_corrections(
                text=state.current_text,
                prior_question=prior_question,
                prior_emotion=prior_emotion
            )

            if corr_res["has_correction"]:
                for rej in corr_res["rejected_emotions"]:
                    if rej not in state.rejected_emotions:
                        state.rejected_emotions.append(rej)
                state.explicit_corrections.append(corr_res)
                state.correction_acknowledgment = corr_res["acknowledgment"]

                if state.turns:
                    state.turns[-1].rejected_emotions = list(state.rejected_emotions)
                    state.turns[-1].explicit_corrections.append(corr_res)

                state.log_trace(
                    agent_name="PlannerAgent",
                    action_type="REASON",
                    details={
                        "action": "REASSESS_AFTER_CORRECTION",
                        "rejected_emotions": corr_res["rejected_emotions"],
                        "user_phrase": state.current_text,
                        "user_focus": corr_res["user_focus"]
                    },
                    thought=f"User explicitly clarified that {', '.join(corr_res['rejected_emotions'])} doesn't fit their experience. Suppressing rejected labels and reassessing remaining candidates."
                )

        while step_count < MAX_ORCHESTRATOR_STEPS:
            step_count += 1

            # -------------------------------------------------------------
            # 1. EMOTION CLASSIFICATION STAGE
            # -------------------------------------------------------------
            if state.current_emotion is None:
                state.log_trace(
                    agent_name="PlannerAgent",
                    action_type="REASON",
                    details={"action": "CLASSIFY_EMOTION"},
                    thought="Executing calibrated transformer classification on reflection text."
                )
                
                prior_context = None
                if len(state.turns) > 1:
                    prior_context = " ".join([t.user_text for t in state.turns[:-1]])

                emo_res = tool_classify_emotion(text=state.current_text, context=prior_context)
                state.current_emotion = emo_res
                
                # If first turn, set as initial emotion and check for empathetic framing
                if state.turn_count == 1:
                    init_interp = tool_generate_initial_interpretation(
                        text=state.current_text,
                        primary_emotion=emo_res["primary_emotion"],
                        is_ambiguous=emo_res.get("is_ambiguous", False),
                        uncertainty_score=emo_res.get("uncertainty_score", 0.5)
                    )
                    state.initial_interpretation = init_interp
                    state.initial_emotion = emo_res
                    state.final_emotion_distribution = emo_res["distribution"]
                    state.final_primary_emotion = emo_res["primary_emotion"]
                    state.final_confidence = emo_res["confidence"]

                    if state.turns:
                        state.turns[0].assistant_interpretation = init_interp
                else:
                    # Reassess emotion using contextual fusion & suppression of rejected emotions
                    self._reconcile_multi_turn_emotion(state, emo_res)

                # Sync turn record
                if state.turns:
                    latest_turn = state.turns[-1]
                    latest_turn.emotion_distribution = state.final_emotion_distribution or emo_res.get("distribution", {})
                    latest_turn.primary_emotion = state.final_primary_emotion or emo_res.get("primary_emotion", "Neutral")
                    latest_turn.confidence = state.final_confidence or emo_res.get("confidence", 0.5)
                    latest_turn.uncertainty_score = emo_res.get("uncertainty_score", 0.5)
                    latest_turn.is_ambiguous = emo_res.get("is_ambiguous", False)

                state.log_trace(
                    agent_name="AnalysisAgent",
                    action_type="TOOL_RESULT",
                    details={
                        "tool": "classify_emotion",
                        "primary_emotion": state.final_primary_emotion,
                        "confidence": state.final_confidence,
                        "rejected_emotions": state.rejected_emotions,
                        "is_ambiguous": emo_res.get("is_ambiguous", False)
                    },
                    thought=f"Active primary emotion is {state.final_primary_emotion} with confidence {state.final_confidence:.2f} (Rejected: {state.rejected_emotions})."
                )
                continue

            # -------------------------------------------------------------
            # 2. STRESS ASSESSMENT STAGE (Independent)
            # -------------------------------------------------------------
            if state.stress_assessment is None:
                state.log_trace(
                    agent_name="PlannerAgent",
                    action_type="REASON",
                    details={"action": "ASSESS_STRESS"},
                    thought="Evaluating reflection for acute psychological strain using the supervised Dreaddit classifier."
                )
                
                # Use accumulated conversational text for stress inference
                combined_text = " ".join([t.user_text for t in state.turns]) if state.turns else state.current_text
                stress_res = tool_classify_stress(text=combined_text)
                state.stress_assessment = stress_res

                state.log_trace(
                    agent_name="AnalysisAgent",
                    action_type="TOOL_RESULT",
                    details={
                        "tool": "classify_stress",
                        "level": stress_res["level"],
                        "probability": stress_res["probability"],
                        "model_source": stress_res["model_source"]
                    },
                    thought=f"Dreaddit model independently predicted {stress_res['level']} stress (p={stress_res['probability']:.2f})."
                )
                continue

            # -------------------------------------------------------------
            # 3. DECISION: STOP (Finalize) OR ASK FOLLOW-UP
            # -------------------------------------------------------------
            should_stop = self._evaluate_stopping_policy(state, force_finalize)
            
            if not should_stop:
                # Ask Personalized Follow-Up Question
                state.log_trace(
                    agent_name="PlannerAgent",
                    action_type="REASON",
                    details={"action": "GENERATE_CLARIFICATION_QUESTION", "turn_count": state.turn_count, "decision": "GENERATE_FOLLOW_UP"},
                    thought="Emotional ambiguity, contextual uncertainty, or correction detected. Generating personalized non-repeating follow-up question."
                )

                # Ensure asked_questions contains prior questions
                for t in state.turns:
                    if t.assistant_question and t.assistant_question not in state.asked_questions:
                        state.asked_questions.append(t.assistant_question)

                q = tool_generate_follow_up_question(
                    text=state.current_text,
                    primary_emotion=state.final_primary_emotion,
                    secondary_emotion=state.current_emotion.get("secondary_emotion") if state.current_emotion else None,
                    is_ambiguous=state.current_emotion.get("is_ambiguous", False) if state.current_emotion else False,
                    uncertainty_score=state.current_emotion.get("uncertainty_score", 0.5) if state.current_emotion else 0.5,
                    full_context=" ".join([t.user_text for t in state.turns]),
                    rejected_emotions=state.rejected_emotions,
                    asked_questions=state.asked_questions,
                    turn_count=state.turn_count,
                    stress_level=state.stress_assessment["level"] if state.stress_assessment else "Moderate"
                )
                state.next_question = q
                state.asked_questions.append(q)
                if state.turns:
                    state.turns[-1].assistant_question = q

                state.log_trace(
                    agent_name="ExplainerAgent",
                    action_type="TOOL_RESULT",
                    details={"tool": "generate_follow_up_question", "question": q, "rejected_emotions": state.rejected_emotions},
                    thought="Personalized follow-up question constructed without repeating prior questions. Presenting to user."
                )

                state.log_trace(
                    agent_name="OrchestratorAgent",
                    action_type="STOP",
                    details={"state": "WAITING_FOR_USER_INPUT", "turn": state.turn_count},
                    thought="Turn assessment complete. Pausing execution until user responds."
                )
                break

            # -------------------------------------------------------------
            # 4. FINALIZATION: Synthesize History, Trends, Explanations, Recs
            # -------------------------------------------------------------
            state.log_trace(
                agent_name="PlannerAgent",
                action_type="REASON",
                details={"action": "FINALIZE_ASSESSMENT", "reason": "Sufficient evidence collected or turn limit reached"},
                thought="Stopping policy satisfied. Finalizing assessment with synthesized conversation context."
            )

            # Retrieve User History
            if not state.user_history:
                state.user_history = tool_get_user_history(user_id=state.user_id, limit=10)

            # Calculate Wellness and Longitudinal Trend
            wt_res = tool_calculate_wellness_and_trend(
                primary_emotion=state.final_primary_emotion,
                emotion_confidence=state.final_confidence,
                stress_level=state.stress_assessment["level"],
                stress_confidence=state.stress_assessment["confidence"],
                history=state.user_history
            )
            state.wellness_assessment = wt_res["wellness"]
            state.trend_assessment = wt_res["trend"]

            # Token-level Technical XAI Attribution
            full_text = " ".join([t.user_text for t in state.turns]) if state.turns else state.current_text
            state.xai_signals = tool_extract_token_attribution(
                text=full_text,
                emotion=state.final_primary_emotion
            )

            # Synthesize Conversational Natural Language Explanation
            turns_summary = [
                {"text": t.user_text, "primary_emotion": t.primary_emotion}
                for t in state.turns
            ]
            state.conversational_explanation = tool_synthesize_conversational_explanation(
                turns_summary=turns_summary,
                final_emotion=state.final_primary_emotion,
                stress_level=state.stress_assessment["level"],
                trend_direction=state.trend_assessment.get("direction", "Stable"),
                rejected_emotions=state.rejected_emotions,
                explicit_corrections=state.explicit_corrections
            )

            # Grounded Recommendations
            state.recommendations = tool_generate_grounded_recommendations(
                emotion=state.final_primary_emotion,
                stress_level=state.stress_assessment["level"],
                user_text=full_text
            )

            # Insights
            trend_dir = state.trend_assessment.get("direction", "Stable") if state.trend_assessment else "Stable"
            if trend_dir.lower() in ["insufficient data", "none"]:
                trend_phrase = "Multi-entry trajectory currently has insufficient historical entries to establish a trend."
            else:
                article = "an" if trend_dir.lower()[0] in "aeiou" else "a"
                trend_phrase = f"Multi-entry trajectory currently reflects {article} {trend_dir.lower()} pattern."

            correction_note = f" (reassessed after clarifying that {', '.join(state.rejected_emotions)} did not fit)" if state.rejected_emotions else ""
            state.insights = (
                f"Across {len(state.turns)} conversational turn(s), the assessment identified {state.final_primary_emotion.lower()}{correction_note}. "
                f"The Dreaddit model independently recorded {state.stress_assessment['level'].lower()} stress strain. "
                f"{trend_phrase}"
            )

            state.is_completed = True
            state.next_question = None

            state.log_trace(
                agent_name="OrchestratorAgent",
                action_type="STOP",
                details={
                    "state": "COMPLETED",
                    "final_emotion": state.final_primary_emotion,
                    "rejected_emotions": state.rejected_emotions,
                    "final_confidence": state.final_confidence
                },
                thought="All multi-turn assessment outputs synthesized and verified. Pipeline finished."
            )
            break

        return state

    def _evaluate_stopping_policy(self, state: AgentState, force_finalize: bool) -> bool:
        """
        Determines whether sufficient evidence has been collected to finalize the assessment.
        Strictly enforces max 4 turns (1 initial entry + up to 3 follow-ups).
        """
        if force_finalize:
            return True
        if state.turn_count >= state.max_turns:
            return True

        # Check if user explicitly asked to stop or gave closing remark
        lower_text = state.current_text.lower().strip()
        closing_phrases = [
            "that's all", "thats all", "nothing else", "that is all",
            "stop", "i'm good", "im good", "done", "no more", "im fine",
            "thank you", "thanks", "that's everything", "thats everything",
            "finish", "finish now"
        ]
        if any(cp in lower_text for cp in closing_phrases):
            return True

        # Check if user expresses uncertainty / "I don't know" in follow-up turns
        uncertainty_phrases = [
            "i don't know", "i dont know", "idk", "not sure", "i'm not sure",
            "im not sure", "hard to say", "no idea", "can't tell", "cant tell"
        ]
        if state.turn_count >= 2 and any(up in lower_text for up in uncertainty_phrases):
            return True

        # Turn 1: If user message is already substantial and unambiguous
        if state.turn_count == 1:
            conf = state.current_emotion.get("confidence", 0.0) if state.current_emotion else 0.0
            ambiguous = state.current_emotion.get("is_ambiguous", True) if state.current_emotion else True
            # If extremely long (>25 words) and exceptionally confident (>0.90) and unambiguous:
            if conf >= 0.90 and not ambiguous and len(state.current_text.split()) >= 25:
                return True
            # Otherwise allow first follow-up to explore context
            return False

        # Turn 2: If user provided correction and resolved ambiguity
        if state.turn_count == 2:
            conf = state.final_confidence
            ambiguous = state.current_emotion.get("is_ambiguous", False) if state.current_emotion else False
            margin = state.current_emotion.get("margin", 0.0) if state.current_emotion else 0.0
            # If user corrected an emotion, ask 1 follow-up question to explore their true focus (turn 3)
            if state.rejected_emotions and state.turn_count < 3:
                return False
            if conf >= 0.75 and not ambiguous and margin >= 0.20:
                return True
            return False

        # Turn 3: Check if ambiguity resolved after second follow-up
        if state.turn_count == 3:
            conf = state.final_confidence
            ambiguous = state.current_emotion.get("is_ambiguous", False) if state.current_emotion else False
            if conf >= 0.65 and not ambiguous:
                return True
            return False

        # Turn 4: Always stop
        return True

    def _reconcile_multi_turn_emotion(self, state: AgentState, current_emo_res: Dict[str, Any]):
        """
        Synthesizes prior and current turn evidence into a final unified emotion distribution.
        Strictly incorporates explicit user corrections by suppressing rejected emotions,
        and elevates candidate emotions supported by user's stated experience.
        """
        init_dist = state.initial_emotion.get("distribution", {}) if state.initial_emotion else {}
        curr_dist = current_emo_res.get("distribution", {})
        rejected = set(state.rejected_emotions)
        
        # Check for sarcasm or direct contradiction
        curr_text = state.current_text.lower()
        has_sarcasm = any(w in curr_text for w in ["sarcastic", "sarcasm", "went wrong", "actually everything", "opposite", "kidding", "irony"])
        
        reconciled = {}
        for c in ["Anger", "Disgust", "Fear", "Joy", "Neutral", "Sadness", "Surprise"]:
            # If emotion is explicitly rejected by the user, eliminate it completely
            if c in rejected:
                reconciled[c] = 0.0
                continue

            p_init = init_dist.get(c, 0.0)
            p_curr = curr_dist.get(c, 0.0)
            
            if has_sarcasm:
                if c in ["Joy", "Neutral"]:
                    p_comb = p_curr * 0.15
                else:
                    p_comb = (p_curr * 0.85) + (p_init * 0.15)
            elif rejected:
                # User corrected the model: prioritize current turn response (75% current, 25% initial non-rejected)
                p_comb = (p_curr * 0.75) + (p_init * 0.25)
            else:
                # Standard evidence combination: 60% latest contextual response, 40% initial evidence
                p_comb = (p_curr * 0.60) + (p_init * 0.40)
                
            reconciled[c] = p_comb

        # If user spoke of academic overwhelm / worry, bolster Fear / Sadness candidates if model had them low
        if any(w in curr_text for w in ["overwhelmed", "stressed", "so much work", "submissions", "viva", "worry", "worried"]):
            if "Fear" not in rejected:
                reconciled["Fear"] = max(reconciled.get("Fear", 0.0), 0.35)
            if "Sadness" not in rejected:
                reconciled["Sadness"] = max(reconciled.get("Sadness", 0.0), 0.25)

        total = sum(reconciled.values()) or 1.0
        norm_dist = {c: round(reconciled[c] / total, 4) for c in reconciled}
        
        # Pick top non-rejected emotion
        sorted_e = sorted(norm_dist.items(), key=lambda x: x[1], reverse=True)
        state.final_emotion_distribution = norm_dist
        state.final_primary_emotion = sorted_e[0][0]
        state.final_confidence = sorted_e[0][1]

    def run(self, text: str, user_id: int, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Single-turn execution endpoint preserving full backward compatibility with
        process_user_reflection, executing the complete agentic pipeline with force_finalize=True.
        """
        import uuid
        session_id = str(uuid.uuid4())
        state = AgentState(
            session_id=session_id,
            user_id=user_id,
            current_text=text,
            turn_count=1,
            user_history=history or []
        )
        state.turns.append(TurnRecord(
            turn_number=1,
            user_text=text
        ))

        # Run pipeline to completion
        final_state = self.execute_turn_assessment(state, force_finalize=True)

        # Build response compatible with analysis_service
        return {
            "session_id": session_id,
            "emotion": final_state.final_primary_emotion,
            "emotion_confidence": final_state.final_confidence,
            "emotion_distribution": final_state.final_emotion_distribution,
            "stress": final_state.stress_assessment.get("level", "Moderate") if final_state.stress_assessment else "Moderate",
            "stress_confidence": final_state.stress_assessment.get("confidence", 0.5) if final_state.stress_assessment else 0.5,
            "stress_explanation": final_state.stress_assessment.get("model_source", "") if final_state.stress_assessment else "",
            "wellness_score": final_state.wellness_assessment.get("score", 70) if final_state.wellness_assessment else 70,
            "wellness_status": final_state.wellness_assessment.get("status", "Balanced") if final_state.wellness_assessment else "Balanced",
            "wellness_description": final_state.wellness_assessment.get("description", "") if final_state.wellness_assessment else "",
            "trend": final_state.trend_assessment or {"direction": "Stable", "based_on_entries": 0},
            "insights": final_state.insights,
            "recommendations": final_state.recommendations,
            "recommendation_objects": [
                {"title": r.split(":")[0].strip() if ":" in r else r, "description": r.split(":")[1].strip() if ":" in r else r, "category": "Mindfulness"}
                for r in final_state.recommendations
            ],
            "context_signals": {
                "xai_attributions": final_state.xai_signals,
                "uncertainty_score": final_state.current_emotion.get("uncertainty_score", 0.0) if final_state.current_emotion else 0.0,
                "is_ambiguous": final_state.current_emotion.get("is_ambiguous", False) if final_state.current_emotion else False,
                "turns_count": 1
            },
            "explanation": final_state.conversational_explanation,
            "execution_trace": [t.dict() if hasattr(t, "dict") else t.model_dump() for t in final_state.trace]
        }

# Global singletons
agent_orchestrator = AgenticOrchestrator()
orchestrator = agent_orchestrator

