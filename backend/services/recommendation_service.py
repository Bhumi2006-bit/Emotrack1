# backend/services/recommendation_service.py
"""
Context-Aware Recommendation Engine
Modular candidate filtering across Calm & Grounding, Academic Pressure, and Rest & Routine.
Frames suggestions gently without diagnostic certainty.
"""

from typing import List, Dict, Any

RECOMMENDATION_CATALOG = [
    {
        "id": "rec_pause",
        "category": "Calm & Grounding",
        "title": "Take a short pause",
        "description": "Step away from the current workspace for 5–10 minutes to reset your attention.",
        "tags": ["high_stress", "fear", "anger", "overwhelm"]
    },
    {
        "id": "rec_grounding",
        "category": "Calm & Grounding",
        "title": "Try a sensory grounding exercise",
        "description": "Bring attention to your immediate physical space: identify 3 things you see, 2 you hear, and 1 you can touch.",
        "tags": ["fear", "anxiety", "high_stress"]
    },
    {
        "id": "rec_box_breathing",
        "category": "Calm & Grounding",
        "title": "Try gentle box breathing",
        "description": "Inhale for 4 seconds, hold for 4, exhale for 4, hold for 4. Repeat for 3 cycles.",
        "tags": ["high_stress", "fear", "panic"]
    },
    {
        "id": "rec_break_down",
        "category": "Workload & Deadlines",
        "title": "Break the workload down",
        "description": "Select one tiny next step you can complete in the next 20 minutes rather than carrying the whole workload at once.",
        "tags": ["academic", "work", "exam", "deadline", "high_stress", "workload"]
    },
    {
        "id": "rec_priority_triage",
        "category": "Workload & Deadlines",
        "title": "Pick a single top priority",
        "description": "Write down everything pending, then star the one task that gives you the highest relief if completed today.",
        "tags": ["academic", "work", "workload", "deadline"]
    },
    {
        "id": "rec_reach_out",
        "category": "Connection & Support",
        "title": "Plan a low-pressure connection",
        "description": "Consider sending a short message to someone you trust or scheduling a small social activity that feels manageable.",
        "tags": ["loneliness", "social", "sadness"]
    },
    {
        "id": "rec_health_checkin",
        "category": "Health & Care",
        "title": "Make space for a practical health check-in",
        "description": "Notice one supportive next step for your body today, such as rest, hydration, a meal, or contacting an appropriate professional for persistent concerns.",
        "tags": ["health", "pain", "illness", "fatigue"]
    },
    {
        "id": "rec_screen_break",
        "category": "Rest & Routine",
        "title": "Step away from screens",
        "description": "Give your eyes and mental focus a restorative 15-minute break without your phone or laptop.",
        "tags": ["fatigue", "drained", "sluggish", "rest"]
    },
    {
        "id": "rec_routine_rest",
        "category": "Rest & Routine",
        "title": "Maintain an early wind-down routine",
        "description": "Plan for 30 minutes of low-stimulation wind-down before sleeping tonight.",
        "tags": ["fatigue", "sadness", "moderate_stress"]
    },
    {
        "id": "rec_celebrate_win",
        "category": "Rest & Routine",
        "title": "Acknowledge your progress",
        "description": "Take a moment to write down what went well today and allow yourself to savor this positive milestone.",
        "tags": ["joy", "relief", "low_stress"]
    }
]

def generate_recommendations(
    text: str,
    emotion: str,
    stress_level: str,
    limit: int = 3
) -> List[Dict[str, str]]:
    """
    Selects, filters, and deduplicates relevant recommendations.
    Returns list of recommendation objects (title, description, category).
    """
    lower = text.lower()
    selected = []
    seen_ids = set()

    # Rule-based tag matching
    matched_tags = set()
    if stress_level == "High":
        matched_tags.add("high_stress")
    elif stress_level == "Moderate":
        matched_tags.add("moderate_stress")
    else:
        matched_tags.add("low_stress")

    if emotion in ["Fear", "Anger"]:
        matched_tags.add(emotion.lower())
    elif emotion == "Joy":
        matched_tags.add("joy")
    elif emotion == "Sadness":
        matched_tags.add("sadness")

    if any(k in lower for k in ["exam", "assignment", "thesis", "lecture", "class", "semester"]):
        matched_tags.add("academic")
        matched_tags.add("workload")
    if any(k in lower for k in ["manager", "job", "office", "client", "meeting", "work", "deadline"]):
        matched_tags.add("work")
        matched_tags.add("workload")
        matched_tags.add("deadline")
    if any(k in lower for k in ["lonely", "alone", "isolated", "friends", "family", "relationship"]):
        matched_tags.update(["loneliness", "social"])
    if any(k in lower for k in ["health", "sick", "ill", "pain", "doctor", "medication"]):
        matched_tags.add("health")
        matched_tags.add("illness")

    if any(k in lower for k in ["tired", "drained", "sleep", "sluggish", "fatigued"]):
        matched_tags.add("fatigue")
        matched_tags.add("rest")

    # Score candidates
    scored = []
    for item in RECOMMENDATION_CATALOG:
        score = sum(1 for tag in item["tags"] if tag in matched_tags)
        scored.append((score, item))

    # Sort descending by relevance score
    scored.sort(key=lambda x: x[0], reverse=True)

    for _, item in scored:
        if item["id"] not in seen_ids:
            selected.append(item)
            seen_ids.add(item["id"])
        if len(selected) >= limit:
            break

    # If fewer than limit, add general grounding recommendations
    if len(selected) < limit:
        for item in RECOMMENDATION_CATALOG:
            if item["id"] not in seen_ids:
                selected.append(item)
                seen_ids.add(item["id"])
            if len(selected) >= limit:
                break

    return selected
