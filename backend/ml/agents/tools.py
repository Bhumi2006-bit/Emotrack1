# backend/ml/agents/tools.py
"""
Concrete Typed Tool Implementations and Tool Schemas for Agentic AI.
Every tool performs a real, auditable operation and returns typed, structured data.
Zero placeholder responses.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from ml.models.emotion_model import emotion_classifier
from ml.models.stress_model import stress_classifier
from ml.explainability.explainer import extract_contextual_signals
from database.models import get_analyses_for_user
from services.wellness_service import calculate_wellness_indicator
from services.trend_service import calculate_longitudinal_trend

# -----------------------------------------------------------------------------
# Tool Schemas for LLM Function Calling (OpenAI / Gemini compatible format)
# -----------------------------------------------------------------------------
TOOL_DEFINITIONS = [
    {
        "name": "classify_emotion",
        "description": "Runs the calibrated transformer model to classify 7-class emotion probabilities and quantify uncertainty on input text with optional conversational context.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The current user text or response."},
                "context": {"type": "string", "description": "Optional prior conversational context for joint inference."}
            },
            "required": ["text"]
        }
    },
    {
        "name": "classify_stress",
        "description": "Runs the Dreaddit-trained supervised classifier to predict probability of acute stress and categorical risk tier on user reflection text.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The user reflection text to evaluate for psychological strain."}
            },
            "required": ["text"]
        }
    },
    {
        "name": "get_user_history",
        "description": "Retrieves the user's recent chronological emotion and stress entries from the local database.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "User identifier."},
                "limit": {"type": "integer", "description": "Maximum number of past reflections to retrieve."}
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "extract_token_attribution",
        "description": "Performs feature occlusion attribution on the transformer model to identify words with highest sensitivity impact on the predicted emotion.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The user input text."},
                "emotion": {"type": "string", "description": "The target emotion class."}
            },
            "required": ["text", "emotion"]
        }
    },
    {
        "name": "generate_follow_up_question",
        "description": "Formulates a personalized, empathetic follow-up question to clarify emotional ambiguity or uncover context.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "User message."},
                "primary_emotion": {"type": "string", "description": "Leading predicted emotion."},
                "secondary_emotion": {"type": "string", "description": "Runner-up emotion."},
                "is_ambiguous": {"type": "boolean", "description": "Whether prediction is ambiguous or sarcastic."}
            },
            "required": ["text", "primary_emotion"]
        }
    },
    {
        "name": "synthesize_conversational_explanation",
        "description": "Synthesizes multi-turn dialogue shifts, stress assessment, and model outputs into a natural-language contextual explanation.",
        "parameters": {
            "type": "object",
            "properties": {
                "initial_text": {"type": "string", "description": "First message."},
                "followup_text": {"type": "string", "description": "Follow-up answers."},
                "initial_emotion": {"type": "string", "description": "Initial emotion."},
                "final_emotion": {"type": "string", "description": "Final reassessed emotion."},
                "stress_level": {"type": "string", "description": "Predicted stress tier."}
            },
            "required": ["initial_text", "final_emotion"]
        }
    }
]

# -----------------------------------------------------------------------------
# Concrete Tool Implementations
# -----------------------------------------------------------------------------

def tool_classify_emotion(text: str, context: Optional[str] = None) -> Dict[str, Any]:
    return emotion_classifier.predict(text=text, context=context)

def tool_classify_stress(text: str) -> Dict[str, Any]:
    return stress_classifier.predict(text=text)

def tool_get_user_history(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    return get_analyses_for_user(user_id, limit=limit)

def tool_extract_token_attribution(text: str, emotion: str) -> List[Dict[str, Any]]:
    return extract_contextual_signals(text=text, detected_emotion=emotion)

def tool_calculate_wellness_and_trend(
    primary_emotion: str,
    emotion_confidence: float,
    stress_level: str,
    stress_confidence: float,
    history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    wellness_res = calculate_wellness_indicator(
        primary_emotion=primary_emotion,
        emotion_confidence=emotion_confidence,
        stress_level=stress_level,
        stress_confidence=stress_confidence,
        history=history
    )
    trend_res = calculate_longitudinal_trend(
        current_score=wellness_res["score"],
        history=history
    )
    return {
        "wellness": wellness_res,
        "trend": trend_res
    }

EMOTION_SYNONYMS = {
    "Surprise": ["surprise", "surprised", "shock", "shocked", "caught off guard", "caught off-guard"],
    "Anger": ["anger", "angry", "mad", "furious", "pissed", "irritated", "annoyed"],
    "Disgust": ["disgust", "disgusted", "repulsed", "grossed out", "revolted"],
    "Fear": ["fear", "scared", "afraid", "frightened", "terrified", "anxious", "anxiety", "panic", "worried", "worry"],
    "Joy": ["joy", "happy", "happiness", "excited", "glad", "pleased", "content"],
    "Sadness": ["sadness", "sad", "depressed", "unhappy", "sorrow", "down", "gloomy"],
    "Neutral": ["neutral", "indifferent", "unbothered", "okay", "fine"]
}

def tool_detect_user_corrections(
    text: str,
    prior_question: Optional[str] = None,
    prior_emotion: Optional[str] = None
) -> Dict[str, Any]:
    """
    Detects whether the user is explicitly negating, rejecting, or correcting an emotion.
    General pattern matching supporting all 7 emotion classes.
    """
    import re
    clean_text = text.lower().strip()
    rejected_emotions = []
    user_focus = ""

    # 1. Direct regex negations: "not surprise", "it's not surprise", "im not angry", etc.
    for emo, syns in EMOTION_SYNONYMS.items():
        for syn in syns:
            pattern = rf"\b(?:it'?s\s+not|it\s+is\s+not|i'?m\s+not|i\s+am\s+not|that'?s\s+not|that\s+is\s+not|not\s+really|definitely\s+not|no\s*,\s*not|not)\s+(?:a\s+|an\s+|the\s+)?{re.escape(syn)}\b"
            if re.search(pattern, clean_text):
                if emo not in rejected_emotions:
                    rejected_emotions.append(emo)
            # Reversal: "surprise isn't it", "surprise does not fit"
            rev_pattern = rf"\b{re.escape(syn)}\s+(?:is\s+not|isn'?t|does\s+not\s+fit|doesn'?t\s+fit|is\s+wrong|doesn'?t\s+make\s+sense)\b"
            if re.search(rev_pattern, clean_text):
                if emo not in rejected_emotions:
                    rejected_emotions.append(emo)

    # 2. Contextual rejection of prior question target:
    # If the assistant asked about a specific emotion and user answered "no" or "not really"
    if prior_question and not rejected_emotions:
        pq_lower = prior_question.lower()
        starts_with_negation = bool(re.match(r"^(?:no\b|nope\b|not\s+really|that'?s\s+not\s+it|doesn'?t\s+fit)", clean_text))
        if starts_with_negation:
            for emo, syns in EMOTION_SYNONYMS.items():
                if any(syn in pq_lower for syn in syns):
                    if emo not in rejected_emotions:
                        rejected_emotions.append(emo)

    has_correction = len(rejected_emotions) > 0

    # Extract user's stated focus
    if has_correction:
        clean_corr = clean_text
        has_pt = any(w in clean_corr for w in ["self time", "personal time", "me time", "time for myself", "free time", "rest"])
        has_int = any(w in clean_corr for w in ["internship", "intern"])
        has_viv = "viva" in clean_corr
        has_sub = any(w in clean_corr for w in ["submission", "submissions"])
        has_asg = any(w in clean_corr for w in ["assignment", "assignments"])
        has_exm = any(w in clean_corr for w in ["exam", "exams", "midterm", "finals", "quiz"])
        has_job_cue = any(w in clean_corr for w in ["boss", "manager", "job", "office", "shift", "coworker", "workplace"])
        has_exh = any(w in clean_corr for w in ["exhausted", "tired", "drained", "no energy", "fatigued", "burnout", "burned out"])
        has_ow = any(w in clean_corr for w in ["overwhelmed", "drowning", "too much", "swamped", "so much work", "pressure", "stressed", "stress"])
        has_rel = any(w in clean_corr for w in ["mixed signals", "mixed signal", "feelings", "like him", "like her", "like them", "crush", "how he feels", "how she feels", "care about", "relationship", "not knowing"])

        focus_parts = []
        if has_pt:
            focus_parts.append("protecting your personal time")
        if has_int:
            focus_parts.append("your internship demands")
        if has_viv:
            focus_parts.append("your viva preparation")
        if has_sub or has_asg:
            focus_parts.append("your submissions and assignments")
        if has_exm:
            focus_parts.append("your upcoming exams")
        if has_job_cue:
            focus_parts.append("workplace pressures")
        if has_rel:
            focus_parts.append("the uncertainty in how they feel and what these signals mean")
        if has_exh and not focus_parts:
            focus_parts.append("exhaustion and fatigue")
        if has_ow and not focus_parts:
            focus_parts.append("feeling overwhelmed by what you are carrying")

        if focus_parts:
            user_focus = " and ".join(focus_parts)
        elif any(w in clean_corr for w in ["sad", "down", "hurt", "grief", "negative", "heavy"]):
            user_focus = "feeling down and the emotional weight of this situation"
        elif any(w in clean_corr for w in ["angry", "frustrated", "unfair", "annoyed"]):
            user_focus = "frustration with what is happening"
        else:
            user_focus = "the specific feelings you described"

    ack = None
    if has_correction:
        rej_str = ", ".join(rejected_emotions)
        ack = f"Understood — {rej_str} doesn't fit what you're describing. Let's focus on {user_focus}."

    return {
        "has_correction": has_correction,
        "rejected_emotions": rejected_emotions,
        "user_focus": user_focus,
        "acknowledgment": ack
    }

def extract_grounded_topics(text: str) -> Dict[str, Any]:
    """
    Extracts explicitly mentioned situational topics from user reflection text.
    Zero hallucination: only flags True if corresponding words appear in the text.
    """
    clean = text.lower()
    has_romantic_feelings = any(w in clean for w in ["like him", "like her", "like them", "like this guy", "like that guy", "like a guy", "like a girl", "like this girl", "like someone", "liking him", "liking her", "feelings for", "have feelings", "feelings toward", "crush", "crushing", "fall for", "falling for", "attracted to", "romantic", "in love", "dating"])
    has_unreciprocated_uncertainty = any(w in clean for w in ["feel the same", "feels the same", "does he like", "does she like", "how he feels", "how she feels", "how they feel", "his feelings", "her feelings", "their feelings", "unsure of his", "unsure of her", "whether he likes", "whether she likes", "reciprocate", "unreciprocated", "wonder if he", "wonder if she", "wonder if they", "does he care", "does she care", "if he cares", "if she cares", "just being friendly", "just friendly", "only being friendly", "might just be friendly", "just a friend", "just friends", "as a friend"])
    has_mixed_signals = any(w in clean for w in ["mixed signal", "mixed signals", "mixed message", "mixed messages", "interpreting conversation", "interpreting conversations", "interpret conversation", "interpret conversations", "overthinking conversation", "reading into", "interpreting what he", "interpreting what she", "interpreting what they", "hot and cold", "confusing signal", "confusing behavior", "decoding"])
    has_uncertainty_or_idk = any(w in clean for w in ["i don't know", "i dont know", "idk", "not sure", "i'm not sure", "im not sure", "hard to say", "no idea", "can't tell", "cant tell", "confused about what to think"])

    has_relationship_uncertainty = has_romantic_feelings or has_unreciprocated_uncertainty or has_mixed_signals or (
        any(w in clean for w in ["boyfriend", "girlfriend", "partner", "crush", "guy", "girl", "him", "her"]) and
        any(w in clean for w in ["unsure", "confusing", "confused", "feelings", "mixed", "signals", "just being friendly", "just friendly"])
    )

    has_work_or_tasks = any(w in clean for w in ["work", "study", "job", "assignment", "submission", "viva", "exam", "tasks", "deadlines", "office", "boss", "project", "homework", "midterm", "finals", "shift", "coworker", "internship"])

    return {
        "has_viva": "viva" in clean,
        "has_submissions": any(w in clean for w in ["submission", "submissions"]),
        "has_assignments": any(w in clean for w in ["assignment", "assignments"]),
        "has_exams": any(w in clean for w in ["exam", "exams", "midterm", "finals", "quiz"]),
        "has_internship": any(w in clean for w in ["internship", "intern"]),
        "has_job": any(w in clean for w in ["boss", "manager", "job", "coworker", "shift", "office", "workplace"]),
        "has_personal_time": any(w in clean for w in ["self time", "personal time", "me time", "time for myself", "time to myself", "free time", "rest", "break for myself", "alone time", "time for me"]),
        "has_relationships": any(w in clean for w in ["family", "parents", "partner", "boyfriend", "girlfriend", "friend", "friends"]),
        "has_deadlines": any(w in clean for w in ["deadline", "deadlines", "due date"]),
        "has_tomorrow": "tomorrow" in clean,
        "has_overwhelm": any(w in clean for w in ["overwhelmed", "overwhelm", "drowning", "too much", "swamped", "burned out", "burnout"]),
        "has_exhaustion": any(w in clean for w in ["exhausted", "tired", "drained", "no energy", "fatigued", "weary", "spent", "worn out"]),
        "has_completion": any(w in clean for w in ["completed", "finished", "done with", "got through", "wrapped up", "submitted all", "turned in", "completed all", "completed my", "finished my", "got all my", "finish my", "complete my"]),
        "has_satisfaction": any(w in clean for w in ["feel good", "feeling good", "happy", "relieved", "satisfying", "proud", "glad", "relief", "content", "great", "satisfied"]),
        "has_work_remaining": any(w in clean for w in ["more work", "still work", "work left", "more left", "more to do", "still more", "not done yet", "remaining work", "other tasks", "remaining", "work still", "yet to do"]),
        "has_romantic_feelings": has_romantic_feelings,
        "has_unreciprocated_uncertainty": has_unreciprocated_uncertainty,
        "has_mixed_signals": has_mixed_signals,
        "has_relationship_uncertainty": has_relationship_uncertainty,
        "has_uncertainty_or_idk": has_uncertainty_or_idk,
        "has_work_or_tasks": has_work_or_tasks,
    }

def tool_generate_initial_interpretation(
    text: str,
    primary_emotion: str,
    is_ambiguous: bool = False,
    uncertainty_score: float = 0.5,
    stress_level: str = "Moderate"
) -> Optional[str]:
    """
    Produces an empathetic, non-presumptive initial interpretation when an entry reflects
    high uncertainty or specific situational pressures grounded in actual user words.
    """
    clean = text.lower()
    topics = extract_grounded_topics(clean)

    academic_elements = []
    if topics["has_viva"]:
        academic_elements.append("viva preparation")
    if topics["has_submissions"] or topics["has_assignments"]:
        academic_elements.append("submissions and assignments")
    if topics["has_exams"]:
        academic_elements.append("exam pressure")
    if topics["has_internship"]:
        academic_elements.append("internship responsibilities")

    if academic_elements:
        elements_str = " and ".join(academic_elements)
        return f"Your entry suggests stress and worry connected to {elements_str}. I'll clarify what's weighing on you most rather than assuming a single emotion."
    elif topics["has_job"]:
        return "Your entry reflects notable cognitive strain and pressure connected to workplace demands. I'll explore what's most pressing before concluding on an emotion."
    elif topics["has_personal_time"]:
        return "Your entry reflects the struggle to find and protect personal time. Let's explore what feels most demanding right now."
    elif topics["has_relationship_uncertainty"]:
        return "Your reflection touches on navigating uncertainty and mixed signals with someone you care about. I'll explore what feels hardest to interpret rather than assuming how you feel."
    elif is_ambiguous or uncertainty_score > 0.40:
        return f"Your reflection carries nuanced feelings where {primary_emotion.lower()} is present, but other factors may be at play. Let's clarify together."

    return None

def tool_generate_follow_up_question(
    text: str,
    primary_emotion: str,
    secondary_emotion: Optional[str] = None,
    is_ambiguous: bool = False,
    uncertainty_score: float = 0.5,
    full_context: Optional[str] = None,
    rejected_emotions: Optional[List[str]] = None,
    asked_questions: Optional[List[str]] = None,
    turn_count: int = 1,
    stress_level: str = "Moderate"
) -> str:
    """
    Constructs a personalized, empathetic follow-up question grounded strictly in conversation history,
    remaining emotional uncertainty, and situational context.
    NEVER references unmentioned entities (e.g. viva, exams, tomorrow, submissions) unless present in text.
    Strictly prevents repeating previously asked questions.
    """
    clean_context = ((full_context or "") + " " + text).lower()
    clean_latest = text.lower().strip()
    rejected = set(rejected_emotions or [])
    asked = [q.lower().strip() for q in (asked_questions or [])]

    # Grounded topic extraction
    ctx_topics = extract_grounded_topics(clean_context)
    latest_topics = extract_grounded_topics(clean_latest)

    candidate_questions: List[str] = []

    # Priority 0: Completion and satisfaction (positive or mixed reflection)
    if (latest_topics["has_completion"] and (latest_topics["has_satisfaction"] or primary_emotion == "Joy")) or \
       (latest_topics["has_satisfaction"] and primary_emotion == "Joy"):
        if latest_topics["has_work_remaining"] or ctx_topics["has_work_remaining"]:
            candidate_questions.append(
                "It sounds like getting that work done gave you a real sense of accomplishment. What part of completing it felt most satisfying, even with more work ahead?"
            )
            candidate_questions.append(
                "Celebrating this milestone is important — what felt like the biggest relief about finishing this portion on time?"
            )
            candidate_questions.append(
                "How does it feel to have this milestone behind you as you pace yourself for what's still ahead?"
            )
        else:
            candidate_questions.append(
                "What part of completing this gave you the strongest sense of satisfaction or relief?"
            )
            candidate_questions.append(
                "It's great to acknowledge these wins. What made this go well for you today?"
            )
            candidate_questions.append(
                "How does it feel right now to have that finished and off your shoulders?"
            )

    # Priority 1: User explicitly rejected an emotion (e.g. Surprise) or corrected the model
    if rejected:
        rej_str = ", ".join(rejected)
        if ctx_topics["has_relationship_uncertainty"]:
            candidate_questions.append(
                "Since that earlier interpretation didn't fit, does this feel more like quiet sadness about the uncertainty between you, or the exhaustion of overanalyzing every interaction?"
            )
            candidate_questions.append(
                "Thank you for clarifying. When you think about this connection and the mixed signals, what feeling feels most present underneath?"
            )
        elif ctx_topics["has_viva"] and ctx_topics["has_submissions"]:
            candidate_questions.append(
                "What's weighing on you more right now — preparation for your viva, the volume of submissions, or feeling like you don't have enough time for both?"
            )
            time_frame = "tomorrow" if ctx_topics["has_tomorrow"] else "coming up"
            candidate_questions.append(
                f"With your viva {time_frame} alongside submissions, does the pressure feel more like nervousness about performance, or exhaustion from the workload?"
            )
            candidate_questions.append(
                "Between the viva and getting through the submissions, which part feels like the most urgent obstacle right now?"
            )
        elif ctx_topics["has_viva"]:
            time_frame = "tomorrow" if ctx_topics["has_tomorrow"] else "coming up"
            candidate_questions.append(
                f"What feels like the most intimidating or uncertain part of your viva {time_frame}?"
            )
            candidate_questions.append(
                "Does the worry feel more like anxiety about unexpected questions, or pressure to present everything thoroughly?"
            )
        elif ctx_topics["has_internship"] and (ctx_topics["has_assignments"] or ctx_topics["has_submissions"]):
            candidate_questions.append(
                "Between your internship responsibilities and college assignments, which one is consuming more of your mental bandwidth right now?"
            )
            candidate_questions.append(
                "Does the pressure feel more like meeting immediate assignment deadlines, or keeping up with expectations at your internship?"
            )
        elif ctx_topics["has_internship"]:
            candidate_questions.append(
                "What aspect of your internship feels most demanding or stressful as you look at your workload?"
            )
        elif ctx_topics["has_submissions"] or ctx_topics["has_assignments"]:
            candidate_questions.append(
                "Which specific assignment or submission feels like the heaviest hurdle to get past right now?"
            )
            candidate_questions.append(
                "Does this pressure feel primarily like urgency to meet the deadline, or exhaustion from carrying too many tasks at once?"
            )
        elif ctx_topics["has_exams"]:
            candidate_questions.append(
                "Does the pressure feel more like anxiety about upcoming exam material, or exhaustion from studying non-stop?"
            )
        elif ctx_topics["has_job"]:
            candidate_questions.append(
                "Which part of your workplace demands or workload feels hardest to manage right now?"
            )
        elif ctx_topics["has_personal_time"]:
            candidate_questions.append(
                "Since that earlier interpretation didn't fit, does this feel more like sheer exhaustion from non-stop demands, or longing for quiet personal time to recharge?"
            )
        else:
            if ctx_topics["has_work_or_tasks"]:
                candidate_questions.append(
                    "Since that earlier interpretation didn't match, what feels most pressing right now — anxiety about upcoming tasks, or feeling weighed down by everything already on your plate?"
                )
            else:
                candidate_questions.append(
                    "Since that earlier interpretation didn't match, could you share a little more about what feels most true to your experience right now?"
                )
                candidate_questions.append(
                    "Thank you for clarifying that. What aspect of this situation feels most important to acknowledge right now?"
                )
            candidate_questions.append(
                "Could you tell me a little more about what part of this situation feels hardest to manage?"
            )

    # Priority 2: User expressed uncertainty / "I don't know"
    if latest_topics["has_uncertainty_or_idk"]:
        candidate_questions.append(
            "It makes complete sense not to have a clear label or answer for this right now. Does sitting with that uncertainty feel frustrating, or just emotionally tiring?"
        )
        candidate_questions.append(
            "Not knowing how to feel or make sense of things can be exhausting. When you notice that uncertainty, what feels most heavy or tender?"
        )
        candidate_questions.append(
            "It's completely okay not to know. Would it feel more helpful to give yourself space from trying to figure it out, or is there a specific thought circling in your mind?"
        )

    # Priority 3: Relationship / romantic feelings and mixed signals uncertainty
    if latest_topics["has_relationship_uncertainty"] or (ctx_topics["has_relationship_uncertainty"] and not ctx_topics["has_work_or_tasks"]):
        if ctx_topics["has_mixed_signals"]:
            candidate_questions.append(
                "Trying to read between the lines and decode someone else's signals can be mentally exhausting. Does the hardest part feel like second-guessing their actions, or second-guessing your own reactions?"
            )
            candidate_questions.append(
                "When signals feel mixed or contradictory, does that uncertainty make you feel more anxious about where you stand, or drained from constantly trying to make sense of it?"
            )
        if ctx_topics["has_unreciprocated_uncertainty"] or ctx_topics["has_romantic_feelings"]:
            candidate_questions.append(
                "Holding feelings for someone while not knowing where they stand is really difficult. Does it feel more like a quiet sadness about the distance, or the restless anxiety of not knowing?"
            )
            candidate_questions.append(
                "When you're trying to figure out how they feel, what part of the uncertainty feels hardest to sit with?"
            )

    # Priority 4: Latest turn explicitly focused on personal time / self time / exhaustion
    if latest_topics["has_personal_time"] or (latest_topics["has_exhaustion"] and not (latest_topics["has_viva"] or latest_topics["has_exams"] or latest_topics["has_relationship_uncertainty"] or ctx_topics["has_relationship_uncertainty"])):
        candidate_questions.append(
            "When you think about taking personal time for yourself to recharge right now, what kind of rest or quiet pause would feel most restorative?"
        )
        candidate_questions.append(
            "Between keeping up with external tasks and making room for yourself, what would give you the most breathing room today?"
        )
        candidate_questions.append(
            "When you don't get that personal time to recharge, does it feel more like sheer exhaustion from non-stop demands, or frustration that your own needs keep getting postponed?"
        )
        candidate_questions.append(
            "What is currently taking up the space that you would normally protect for yourself?"
        )

    # Priority 2: Grounded academic / work context (when not already added via rejection)
    if ctx_topics["has_viva"] and ctx_topics["has_submissions"]:
        candidate_questions.append(
            "What's weighing on you more right now — preparation for your viva, the volume of submissions, or feeling like you don't have enough time for both?"
        )
        time_frame = "tomorrow" if ctx_topics["has_tomorrow"] else "coming up"
        candidate_questions.append(
            f"With your viva {time_frame} and submissions piling up, does the pressure feel more like anxiety about performing well, or sheer exhaustion from the workload?"
        )
        candidate_questions.append(
            "Between preparing for your viva and completing the submissions, which part feels like the most urgent obstacle right now?"
        )
    elif ctx_topics["has_viva"]:
        time_frame = "tomorrow" if ctx_topics["has_tomorrow"] else "coming up"
        candidate_questions.append(
            f"What feels like the most intimidating part of your viva {time_frame}?"
        )
        candidate_questions.append(
            "Does the worry feel more like nervousness about unexpected questions, or fatigue from preparing?"
        )
    elif ctx_topics["has_internship"] and (ctx_topics["has_assignments"] or ctx_topics["has_submissions"]):
        candidate_questions.append(
            "Between your internship responsibilities and college assignments, which one is consuming more of your mental energy right now?"
        )
        candidate_questions.append(
            "Does the pressure feel more like meeting immediate assignment deadlines, or keeping up with expectations at your internship?"
        )
        candidate_questions.append(
            "How is the balance between your internship and coursework affecting your personal energy day-to-day?"
        )
    elif ctx_topics["has_internship"]:
        candidate_questions.append(
            "What aspect of your internship feels most demanding or stressful right now?"
        )
    elif ctx_topics["has_assignments"] or ctx_topics["has_submissions"]:
        candidate_questions.append(
            "Which specific assignment or submission feels like the heaviest hurdle to get past right now?"
        )
        candidate_questions.append(
            "Does the pressure feel more like anxiety about meeting upcoming deadlines, or feeling drained from the constant effort needed to keep up?"
        )
    elif ctx_topics["has_exams"]:
        candidate_questions.append(
            "Does the pressure feel more like anxiety about exam performance, or feeling drained from studying continuously?"
        )
    elif ctx_topics["has_job"]:
        candidate_questions.append(
            "Does the workplace pressure feel primarily like unrealistic expectations, or exhaustion from the daily pace?"
        )

    # Priority 3: Sarcasm / Irony cues
    if primary_emotion == "Joy" and any(w in clean_context for w in ["great", "wonderful", "amazing", "super", "fantastic", "best", "perfect"]):
        if is_ambiguous or uncertainty_score > 0.40 or any(w in clean_context for w in ["yeah", "sure", "totally", "right", "..."]):
            candidate_questions.append(
                "When you say it was a great day, do you mean that genuinely, or is there something frustrating or stressful behind it?"
            )

    # Priority 4: Disentangling competing negative states
    if primary_emotion in ["Sadness", "Fear"] and secondary_emotion in ["Sadness", "Fear"] and "Fear" not in rejected and "Sadness" not in rejected:
        if ctx_topics["has_relationship_uncertainty"]:
            candidate_questions.append(
                "Does this feel more like anxiety about the uncertainty of where you stand, or quiet sadness about the distance?"
            )
        else:
            candidate_questions.append(
                "Does this feel more like anxiety about what might happen next, or feeling worn down and exhausted by everything that has accumulated?"
            )
            if ctx_topics["has_work_or_tasks"]:
                candidate_questions.append(
                    "Are you feeling mostly worried about upcoming uncertainties, or discouraged by how much has been placed on you?"
                )

    if primary_emotion in ["Anger", "Disgust"] and secondary_emotion in ["Anger", "Disgust"] and "Anger" not in rejected and "Disgust" not in rejected:
        candidate_questions.append(
            "Is this feeling primarily frustration with a specific obstacle or person, or does it feel more like deep disapproval of how things were handled?"
        )

    # Priority 5: Emotion-specific exploration (skipping rejected emotions)
    effective_emotion = primary_emotion if primary_emotion not in rejected else (secondary_emotion or "Neutral")

    if effective_emotion == "Fear" and "Fear" not in rejected:
        candidate_questions.append(
            "It sounds like there's some uncertainty ahead. What is the main outcome or expectation you're most concerned about?"
        )
        candidate_questions.append(
            "What feels like the most intimidating part of what you're facing right now?"
        )
    elif effective_emotion == "Sadness" and "Sadness" not in rejected:
        candidate_questions.append(
            "It sounds like this has been weighing on you. What feels like the hardest part to carry right now?"
        )
        candidate_questions.append(
            "Has this heaviness been building up over time, or did a specific event make it feel especially strong today?"
        )
    elif effective_emotion == "Anger" and "Anger" not in rejected:
        candidate_questions.append(
            "What was the tipping point in this situation that made you feel so frustrated?"
        )
    elif effective_emotion == "Surprise" and "Surprise" not in rejected:
        candidate_questions.append(
            "Did this unexpected turn feel like a welcome surprise, or was it jarring and unsettling?"
        )
        candidate_questions.append(
            "When things unfolded unexpectedly, did it leave you feeling pleasantly surprised or off balance?"
        )
    elif effective_emotion == "Disgust" and "Disgust" not in rejected:
        candidate_questions.append(
            "What specifically happened that felt so uncomfortable or out of line with your expectations?"
        )
    elif effective_emotion == "Neutral" and "Neutral" not in rejected:
        candidate_questions.append(
            "You describe this quite calmly, but is there a part of this situation that feels heavy or unresolved underneath?"
        )
        candidate_questions.append(
            "What aspect of this situation has stayed on your mind the most since it happened?"
        )
    elif effective_emotion == "Joy" and "Joy" not in rejected:
        candidate_questions.append(
            "What happened that made you feel that way, and what part of it brought you the most satisfaction?"
        )

    # Universal backup questions (adaptive to tone)
    if primary_emotion == "Joy" or latest_topics.get("has_satisfaction"):
        candidate_questions.append(
            "Looking back on what you've shared, what stands out most about how you're feeling right now?"
        )
        candidate_questions.append(
            "What would help you preserve this positive momentum through the rest of your day?"
        )
    else:
        candidate_questions.append(
            "Could you tell me a little more about what is weighing on your mind the most right now?"
        )
        if ctx_topics["has_work_or_tasks"]:
            candidate_questions.append(
                "Looking at everything you're dealing with, what feels like the very next hurdle you need to get past?"
            )
        else:
            candidate_questions.append(
                "Looking back on what you've shared, what part of this situation feels most important to honor right now?"
            )

    # DEDUPLICATION: Select the first candidate question that has NOT already been asked
    for q in candidate_questions:
        q_norm = q.lower().strip()
        # Check exact and high-similarity match against asked questions
        already_asked = any(
            q_norm == past or (len(set(q_norm.split()) & set(past.split())) / max(len(q_norm.split()), 1) > 0.70)
            for past in asked
        )
        if not already_asked:
            return q

    # If all candidates somehow overlapped, return a fresh contextual question
    if primary_emotion == "Joy" or latest_topics.get("has_satisfaction"):
        return "Reflecting on your entry, what would feel most fulfilling or restorative as you look forward?"
    return "Reflecting on what you've shared so far, what would bring you the most clarity or relief as you take the next step?"

def tool_synthesize_conversational_explanation(
    turns_summary: List[Dict[str, Any]],
    final_emotion: str,
    stress_level: str,
    trend_direction: str = "Stable",
    rejected_emotions: Optional[List[str]] = None,
    context_themes: Optional[List[str]] = None,
    explicit_corrections: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Synthesizes multi-turn dialogue shifts, user corrections, situational stress,
    and model outputs into a natural, contextual, human-understandable explanation.
    Strictly grounds in user-mentioned entities without hallucinating unmentioned events.
    Distinguishes what the user directly stated from what the system tentatively infers.
    Never uses generic dismissive phrases like 'cognitive strain about performance and workload'.
    """
    rejected = list(rejected_emotions or [])
    all_text = " ".join([t.get("text", "") for t in turns_summary]).lower() if turns_summary else ""
    topics = extract_grounded_topics(all_text)
    num_turns = len(turns_summary)
    has_rejection = len(rejected) > 0

    # 1. Grounded statement of what the user directly stated
    if topics["has_completion"] and topics["has_satisfaction"] and topics["has_work_remaining"]:
        user_stated = "You shared a clear sense of satisfaction and relief after completing your work on time, while also remaining conscious of the additional work that is still ahead."
    elif topics["has_completion"] and (topics["has_satisfaction"] or final_emotion == "Joy"):
        user_stated = "You expressed a genuine sense of accomplishment, satisfaction, and relief from finishing your work on time."
    elif topics["has_relationship_uncertainty"]:
        if topics["has_mixed_signals"] and (topics["has_romantic_feelings"] or topics["has_unreciprocated_uncertainty"]):
            user_stated = "You shared feelings of affection for someone alongside the confusion of mixed signals and repeatedly trying to interpret conversations."
        elif topics["has_mixed_signals"]:
            user_stated = "You described the confusion and mental exhaustion of trying to decipher mixed signals in your interactions."
        else:
            user_stated = "You reflected on feelings of affection and the difficult uncertainty of not knowing where you stand with someone."
    elif topics["has_personal_time"] and topics["has_exhaustion"]:
        user_stated = "You shared that you are feeling exhausted and longing for personal time and quiet space to recharge away from continuous demands."
    elif topics["has_personal_time"]:
        user_stated = "You described the difficulty of finding and protecting personal time for yourself amidst ongoing daily commitments."
    elif topics["has_exhaustion"]:
        user_stated = "You expressed deep fatigue and feeling worn out by the continuous energy you have had to put in."
    elif topics["has_viva"] and topics["has_submissions"]:
        user_stated = "You described feeling the dual weight of preparing for your viva while managing a heavy volume of submissions."
    elif topics["has_viva"]:
        user_stated = "You shared feeling nervous and uncertain about your upcoming viva preparation and evaluation."
    elif topics["has_internship"] and (topics["has_assignments"] or topics["has_submissions"]):
        user_stated = "You highlighted the challenge of balancing professional expectations at your internship alongside college assignments."
    elif topics["has_internship"]:
        user_stated = "You described the pressure and learning curve connected to your internship responsibilities."
    elif topics["has_submissions"] or topics["has_assignments"]:
        user_stated = "You noted the pressure and urgency of managing upcoming submissions and academic deadlines."
    elif topics["has_exams"]:
        user_stated = "You described feeling pressure and anxiety surrounding upcoming exam preparation."
    elif topics["has_job"]:
        user_stated = "You expressed feeling the burden of workplace responsibilities and professional expectations."
    else:
        user_stated = "You reflected on the situational pressures and emotional weight described in your entry."

    # 2. User correction acknowledgment if an emotion was rejected
    correction_ack = ""
    if has_rejection:
        rej_names = ", ".join(rejected)
        correction_ack = f" You explicitly clarified that {rej_names} does not match what you are feeling, so the system suppressed that category and aligned with your stated experience."

    # 3. Grounding notes: explicitly distinguish stated facts vs. unknown aspects vs. uncertainty
    uncertainty_note = ""
    if topics["has_uncertainty_or_idk"]:
        uncertainty_note = " You also expressed that it's difficult to know or define what you are feeling, which is a very natural response to ambiguous emotional situations."

    unknown_note = ""
    if topics["has_relationship_uncertainty"]:
        unknown_note = " While the other person's true thoughts and feelings remain unknown from these interactions alone, your own experience of ambiguity, hope, and vulnerability is completely valid."

    # 4. Tentative algorithmic model inference (clearly separated, non-dogmatic)
    if final_emotion == "Joy":
        inference_note = (
            f"Based on your words, EmoTrack tentatively registers a primary pattern of joy, "
            f"while the independent stress model independently identified {stress_level.lower()} acute stress. "
            f"This algorithmic estimate reflects phrasing patterns rather than an objective verdict on your emotional reality."
        )
    elif topics["has_personal_time"] or topics["has_exhaustion"]:
        inference_note = (
            f"From these reflections of fatigue, EmoTrack tentatively identifies a primary signal of {final_emotion.lower()}, "
            f"while the independent stress model independently identified {stress_level.lower()} acute stress. "
            f"This reflects a natural need for rest and personal recovery rather than a performance shortcoming."
        )
    elif topics["has_relationship_uncertainty"]:
        inference_note = (
            f"EmoTrack tentatively detects an emotional signature of {final_emotion.lower()} alongside {stress_level.lower()} acute stress indicators. "
            f"This reflects the emotional weight of caring deeply in the presence of ambiguity, rather than a definitive conclusion about the other person's feelings or the relationship itself."
        )
    else:
        inference_note = (
            f"Based on your phrasing, EmoTrack tentatively registers a primary pattern of {final_emotion.lower()}, "
            f"while the independent stress model independently identified {stress_level.lower()} acute stress indicators. "
            f"This algorithmic estimate is intended to support your self-reflection."
        )

    prefix = "What EmoTrack understood from your reflection: "
    body_elements = [user_stated]
    if correction_ack:
        body_elements.append(correction_ack.strip())
    if uncertainty_note:
        body_elements.append(uncertainty_note.strip())
    if unknown_note:
        body_elements.append(unknown_note.strip())
    body = " ".join(body_elements)

    if num_turns > 1:
        return f"{prefix}{body} Across {num_turns} conversational turns, {inference_note}"

    return f"{prefix}{body} {inference_note}"


def tool_generate_grounded_recommendations(
    emotion: str,
    stress_level: str,
    user_text: str
) -> List[str]:
    """
    Produces proportionate, personalized suggestions grounded in the user's specific state.
    Acknowledges feelings first before suggesting actions.
    Tailors to actual expressed need without commanding the user or prescribing generic productivity hacks.
    """
    clean = user_text.lower()
    topics = extract_grounded_topics(clean)

    # 0. Interpersonal / Relationship uncertainty
    if topics["has_relationship_uncertainty"]:
        return [
            "Observe patterns over time: Rather than decoding every single conversation or message for hidden meaning, step back and look at overall consistency over weeks. Mixed signals often become clearer when given time to breathe.",
            "Release the urgency to decide right now: You do not have to figure out their intentions or force an immediate conclusion today. Allowing yourself not to know right now can relieve the immediate pressure to resolve the ambiguity.",
            "Ground yourself in your own worth: Your value and self-worth exist independently of whether someone else can clearly communicate or reciprocate their feelings. Dedicate time today to people and activities where you feel unambiguously appreciated."
        ]

    # 1. Exhaustion / Needing personal time
    if topics["has_personal_time"] or topics["has_exhaustion"]:
        return [
            "Give yourself permission to pause: You do not need to earn your rest. Allow yourself to step completely away from tasks today without feeling guilty.",
            "Create a low-stimulation pocket: Spend 10-15 minutes away from screens and obligations—close your eyes, listen to calming sound, or just sit quietly.",
            "Protect your boundaries: If non-essential requests come in, practice deferring them to tomorrow so you can preserve your remaining energy for yourself."
        ]

    # 2. Completion and satisfaction (positive or mixed reflection)
    if topics["has_completion"] and (topics["has_satisfaction"] or emotion == "Joy"):
        if topics["has_work_remaining"]:
            return [
                "Savor the milestone: Take a moment to genuinely celebrate what you just finished before looking ahead at the next task.",
                "Pace the next stretch: You've already proven you can deliver. Give yourself a brief buffer break before easing into what remains.",
                "Carry the quiet confidence forward: Remind yourself of the relief of completing this step whenever remaining tasks feel heavy."
            ]
        else:
            return [
                "Savor what you achieved: Take a mental breath and enjoy the feeling of having completed this commitment.",
                "Reward your effort: Treat yourself to something simple you enjoy today—a favorite snack, a walk, or doing nothing for a while.",
                "Carry this positive momentum: Remember how capable you were in getting this across the finish line."
            ]

    # 3. Joy / positive reflection without explicit task completion
    if emotion == "Joy":
        return [
            "Savor the moment: Take a mental snapshot of what went well so you can remember it later.",
            "Share the good news: Tell someone you care about what brought you satisfaction today.",
            "Acknowledge your progress: Recognize your own contribution to making things turn out well."
        ]

    # 4. Viva or exam preparation
    if topics["has_viva"] or topics["has_exams"]:
        return [
            "Focus on the immediate next concept: When the entire syllabus feels daunting, narrow your focus to one single topic for the next 20 minutes.",
            "Slow exhale breathing: If anxiety spikes, take a 4-second inhale followed by a 6-second slow exhale to regulate your nervous system.",
            "Protect a firm stopping time: Decide right now when you will stop studying tonight so your brain has adequate sleep to consolidate knowledge."
        ]

    # 5. Submissions or assignments
    if topics["has_submissions"] or topics["has_assignments"]:
        return [
            "Tackle the smallest hurdle first: Pick one small section or citation to finish, letting the completion give you traction.",
            "Work in short, gentle intervals: Use a 25-minute focus window followed by a 5-minute break away from your keyboard.",
            "Acknowledge what is already done: Check off any finished pieces so you can see your concrete progress."
        ]

    # 6. Anger or Disgust
    if emotion in ["Anger", "Disgust"]:
        return [
            "Acknowledge the boundary: Give yourself permission to feel irritated without judging yourself for the reaction.",
            "Physically step back: Step away from screens or the source of tension for 10 minutes to let your nervous system decompress.",
            "Focus on your circle of control: Channel your energy toward what you can influence directly, and release what isn't in your hands."
        ]

    # 7. Fear or Sadness
    if emotion in ["Fear", "Sadness"]:
        return [
            "Give yourself space to feel this: Be gentle with yourself—overwhelm is a natural response to high demands, not personal inadequacy.",
            "Reach out or write it out: Sharing your feelings with a friend or writing them down can help unpack the emotional weight.",
            "A comforting sensory ritual: A warm drink, gentle music, or a brief walk outside can help ground your body in the present."
        ]

    # 8. Neutral / default
    return [
        "Check in with your energy: Notice whether feeling neutral reflects steady calm or slight fatigue.",
        "A mindful pause: Take three deep breaths and tune into what your body and mind need most right now.",
        "Set an intentional small wish: Pick one gentle, enjoyable thing for yourself today."
    ]
