# backend/routes/dashboard.py
from fastapi import APIRouter, Depends
from collections import Counter
from database.models import get_analyses_for_user, count_analyses_for_user, get_user_by_id, get_current_streak_for_user
from routes.dependencies import get_current_user_id

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("")
def get_dashboard_summary(user_id: int = Depends(get_current_user_id)):
    """
    Returns aggregated metrics and charts for the main dashboard screen.
    """
    user = get_user_by_id(user_id)
    analyses = get_analyses_for_user(user_id, limit=30)
    total_entries = count_analyses_for_user(user_id)

    # Latest analysis
    latest = analyses[0] if analyses else None

    colors = {"Joy": "#10B981", "Neutral": "#64748B", "Sadness": "#3B82F6", "Fear": "#F59E0B", "Anger": "#EF4444", "Surprise": "#8B5CF6", "Disgust": "#0D9488"}
    chronological = list(reversed(analyses))
    daily = {}
    for entry in chronological:
        day = entry["created_at"][:10]
        daily.setdefault(day, []).append(entry["wellness_score"])
    weekly_trend = [{"day": day[5:], "score": round(sum(scores) / len(scores))} for day, scores in list(daily.items())[-7:]]
    counts = Counter(a["primary_emotion"] for a in analyses)
    total_analyses = len(analyses)
    emotion_distribution = [
        {
            "emotion": emotion,
            "count": count,
            "percentage": round(count / total_analyses * 100),
            "color": colors.get(emotion, "#64748B")
        }
        for emotion, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)
    ] if total_analyses > 0 else []
    change = latest["wellness_score"] - analyses[1]["wellness_score"] if len(analyses) > 1 else None

    return {
        "user_name": user["name"] if user else "Friend",
        "streak_days": get_current_streak_for_user(user_id),
        "total_entries": total_entries,
        "wellness": {
            "score": latest["wellness_score"] if latest else None,
            "status": latest["wellness_status"] if latest else None,
            "change": change,
            "message": "Complete your first reflection to see your non-diagnostic wellness indicator." if not latest else "Based on your most recent reflection."
        },
        "emotion": {
            "label": latest["primary_emotion"] if latest else None,
            "confidence": round(latest["emotion_confidence"] * 100) if latest else None
        },
        "stress": {
            "level": latest["stress_level"] if latest else None,
            "confidence": round(latest["stress_confidence"] * 100) if latest else None
        },
        "weekly_trend": weekly_trend,
        "emotion_distribution": emotion_distribution,
        "recent_analyses": analyses[:5]
    }
