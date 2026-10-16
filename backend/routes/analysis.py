# backend/routes/analysis.py
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from database.models import (
    get_analyses_for_user,
    get_analysis_by_id,
    count_analyses_for_user,
    delete_analyses_for_user,
    save_recommendation,
    get_saved_recommendations,
    delete_saved_recommendation,
    toggle_recommendation_status
)
from services.analysis_service import process_user_reflection
from services.multi_turn_service import MultiTurnService
from routes.dependencies import get_current_user_id
from datetime import datetime, timedelta
from collections import Counter, defaultdict

router = APIRouter(prefix="/analysis", tags=["Analysis"])

class AnalysisRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=2500)

class SessionStartRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=2500)

class SessionRespondRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2500)

@router.post("")
def create_analysis(req: AnalysisRequest, user_id: int = Depends(get_current_user_id)):
    """
    Submits a user reflection for NLP, stress evaluation, wellness scoring,
    and agentic multi-stage reasoning (Single-Turn).
    """
    try:
        result = process_user_reflection(user_id=user_id, text=req.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")

@router.post("/session/start")
def start_analysis_session(req: SessionStartRequest, user_id: int = Depends(get_current_user_id)):
    """
    Initiates a multi-turn conversational reflection session.
    Determines if follow-up clarification is needed or if assessment can finalize immediately.
    """
    try:
        return MultiTurnService.start_session(user_id=user_id, text=req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@router.post("/session/{session_id}/respond")
def respond_to_analysis_session(session_id: str, req: SessionRespondRequest, user_id: int = Depends(get_current_user_id)):
    """
    Submits user response to an assistant clarifying question in an active multi-turn session.
    """
    try:
        return MultiTurnService.respond_to_session(user_id=user_id, session_id=session_id, text=req.text)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process session turn: {str(e)}")

@router.post("/session/{session_id}/finalize")
def finalize_analysis_session(session_id: str, user_id: int = Depends(get_current_user_id)):
    """
    Forces completion of an active session, persisting the synthesized multi-turn assessment.
    """
    try:
        return MultiTurnService.finalize_session(user_id=user_id, session_id=session_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to finalize session: {str(e)}")

@router.get("/history")
def get_history(
    emotion: Optional[str] = None,
    stress: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: int = Depends(get_current_user_id)
):
    """
    Retrieves chronological past analyses with optional filtering.
    """
    # Filtering before pagination makes the returned total accurate and keeps
    # pagination usable even with a thousand or more local records.
    all_analyses = get_analyses_for_user(user_id, limit=10000)
    if emotion and emotion != "All":
        all_analyses = [a for a in all_analyses if a["primary_emotion"].lower() == emotion.lower()]
    if stress and stress != "All":
        all_analyses = [a for a in all_analyses if a["stress_level"].lower() == stress.lower()]
    total = len(all_analyses)
    analyses = all_analyses[offset: offset + limit]
        
    return {
        "total": total,
        "items": analyses
    }

@router.get("/trends")
def get_trends(
    period: str = Query("30d", pattern="^(7d|30d|3m|6m|1y)$"),
    user_id: int = Depends(get_current_user_id)
):
    """
    Retrieves time series aggregations for longitudinal wellness, stress, and emotion patterns.
    """
    analyses = get_analyses_for_user(user_id, limit=10000)
    if not analyses:
        return {
            "wellness_trend": [],
            "stress_trend": [],
            "emotion_distribution": {}
        }
    
    days = {"7d": 7, "30d": 30, "3m": 92, "6m": 183, "1y": 366}[period]
    cutoff = (datetime.now() - timedelta(days=days)).date()
    chronological = [a for a in reversed(analyses) if datetime.fromisoformat(a["created_at"]).date() >= cutoff]
    buckets = defaultdict(list)
    for a in chronological:
        date_value = datetime.fromisoformat(a["created_at"]).date()
        if period in ("3m", "6m"):
            key = f"{date_value.isocalendar().year}-W{date_value.isocalendar().week:02d}"
        elif period == "1y":
            key = date_value.strftime("%Y-%m")
        else:
            key = date_value.isoformat()
        buckets[key].append(a)

    wellness_trend, stress_trend = [], []
    for key, entries in buckets.items():
        average_score = round(sum(a["wellness_score"] for a in entries) / len(entries))
        average_stress = round(sum(3 if a["stress_level"] == "High" else 2 if a["stress_level"] == "Moderate" else 1 for a in entries) / len(entries))
        stress_label = {1: "Low", 2: "Moderate", 3: "High"}[average_stress]
        label = key[5:] if period in ("7d", "30d") else key
        wellness_trend.append({"date": label, "score": average_score, "status": entries[-1]["wellness_status"]})
        stress_trend.append({"date": label, "level": stress_label, "numeric": average_stress})
    
    # Distribution calculation
    counts = {}
    for a in chronological:
        emo = a["primary_emotion"]
        counts[emo] = counts.get(emo, 0) + 1
    
    total = len(chronological)
    emotion_dist = {k: round((v / total) * 100, 1) for k, v in counts.items()}
    
    return {
        "wellness_trend": wellness_trend,
        "stress_trend": stress_trend,
        "emotion_distribution": emotion_dist,
        "entries_analyzed": total
    }

class SaveRecommendationRequest(BaseModel):
    category: Optional[str] = "Mindfulness"
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    analysis_id: Optional[int] = None

class BatchSaveRecommendationsRequest(BaseModel):
    items: List[SaveRecommendationRequest]

@router.post("/recommendations/save")
def save_user_recommendations(req: BatchSaveRecommendationsRequest, user_id: int = Depends(get_current_user_id)):
    """
    Persists one or more personalized recommendations to the authenticated user's profile.
    """
    saved_ids = []
    for item in req.items:
        rec_id = save_recommendation(
            user_id=user_id,
            category=item.category or "Mindfulness",
            title=item.title,
            description=item.description,
            analysis_id=item.analysis_id
        )
        saved_ids.append(rec_id)
    return {"saved": True, "saved_ids": saved_ids, "count": len(saved_ids)}

@router.get("/recommendations")
def get_user_recommendations(user_id: int = Depends(get_current_user_id)):
    """
    Retrieves all saved recommendations for the authenticated user.
    """
    recs = get_saved_recommendations(user_id)
    return {"items": recs, "total": len(recs)}

@router.delete("/recommendations/{rec_id}")
def delete_user_recommendation(rec_id: int, user_id: int = Depends(get_current_user_id)):
    """
    Deletes a saved recommendation owned by the authenticated user.
    """
    success = delete_saved_recommendation(user_id=user_id, rec_id=rec_id)
    if not success:
        raise HTTPException(status_code=404, detail="Saved recommendation not found or unauthorized.")
    return {"deleted": True, "id": rec_id}

@router.patch("/recommendations/{rec_id}/toggle")
def toggle_user_recommendation(rec_id: int, user_id: int = Depends(get_current_user_id)):
    """
    Toggles completion status for a saved recommendation.
    """
    updated = toggle_recommendation_status(user_id=user_id, rec_id=rec_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Saved recommendation not found or unauthorized.")
    return {"updated": True, "item": updated}

@router.get("/{analysis_id}")
def get_single_analysis(analysis_id: int, user_id: int = Depends(get_current_user_id)):
    """
    Fetches full breakdown for a specific historical entry.
    """
    analysis = get_analysis_by_id(analysis_id)
    if not analysis or analysis["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    return analysis

class AnalysisFeedbackRequest(BaseModel):
    feedback: str

@router.post("/{analysis_id}/feedback")
def submit_analysis_feedback(analysis_id: int, req: AnalysisFeedbackRequest, user_id: int = Depends(get_current_user_id)):
    """
    Records whether user agreed with reflection assessment ('feels_right', 'partly_right', 'wrong').
    """
    from database.models import save_analysis_feedback
    success = save_analysis_feedback(analysis_id=analysis_id, user_id=user_id, feedback=req.feedback)
    if not success:
        raise HTTPException(status_code=404, detail="Analysis record not found or unauthorized.")
    return {"success": True, "feedback": req.feedback}

@router.delete("/history")
def delete_history(user_id: int = Depends(get_current_user_id)):
    delete_analyses_for_user(user_id)
    return {"deleted": True}
