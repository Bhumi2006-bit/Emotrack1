# backend/ml/agents/agent_state.py
"""
Typed Conversation & Analysis State for Agentic AI Pipeline.
Enables structured state sharing, tool logging, and transparent execution traces.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import time

class TraceStep(BaseModel):
    timestamp: float = Field(default_factory=time.time)
    agent_name: str
    action_type: str # 'REASON', 'SELECT_TOOL', 'TOOL_RESULT', 'STATE_UPDATE', 'STOP'
    details: Dict[str, Any]
    thought: Optional[str] = None

class TurnRecord(BaseModel):
    turn_number: int
    user_text: str
    turn_type: str = "initial" # 'initial', 'follow_up'
    emotion_distribution: Dict[str, float] = Field(default_factory=dict)
    primary_emotion: str = "Neutral"
    confidence: float = 0.50
    uncertainty_score: float = 0.50
    is_ambiguous: bool = False
    assistant_question: Optional[str] = None
    assistant_interpretation: Optional[str] = None
    rejected_emotions: List[str] = Field(default_factory=list)
    explicit_corrections: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)

class AgentState(BaseModel):
    session_id: str
    user_id: int
    current_text: str
    turns: List[TurnRecord] = Field(default_factory=list)
    turn_count: int = 1
    max_turns: int = 4
    is_completed: bool = False
    
    # Model Inferences
    initial_emotion: Optional[Dict[str, Any]] = None
    current_emotion: Optional[Dict[str, Any]] = None
    final_emotion_distribution: Dict[str, float] = Field(default_factory=dict)
    final_primary_emotion: str = "Neutral"
    final_confidence: float = 0.50
    prior_predictions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Conversation State & Explicit Corrections
    asked_questions: List[str] = Field(default_factory=list)
    rejected_emotions: List[str] = Field(default_factory=list)
    explicit_corrections: List[Dict[str, Any]] = Field(default_factory=list)
    correction_acknowledgment: Optional[str] = None
    initial_interpretation: Optional[str] = None
    contextual_themes: List[str] = Field(default_factory=list)
    
    # Stress
    stress_assessment: Optional[Dict[str, Any]] = None
    
    # Wellness & Trend
    wellness_assessment: Optional[Dict[str, Any]] = None
    trend_assessment: Optional[Dict[str, Any]] = None
    user_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Explanations & Recommendations
    xai_signals: List[Dict[str, Any]] = Field(default_factory=list)
    conversational_explanation: Optional[str] = None
    insights: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)
    next_question: Optional[str] = None
    
    # Execution Trace (for auditable Agentic AI)
    trace: List[TraceStep] = Field(default_factory=list)

    def log_trace(self, agent_name: str, action_type: str, details: Dict[str, Any], thought: Optional[str] = None):
        step = TraceStep(
            agent_name=agent_name,
            action_type=action_type,
            details=details,
            thought=thought
        )
        self.trace.append(step)
