# backend/database/models.py
import json
import sqlite3
from typing import List, Dict, Any, Optional
from database.connection import get_db_connection

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def create_user(
    username: str,
    name: str,
    email: str,
    password_hash: str,
    age: int = 18,
    date_of_birth: Optional[str] = None,
    is_email_verified: int = 0,
    email_verification_token: Optional[str] = None
) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO users (username, name, email, password_hash, streak_days, age, date_of_birth, is_email_verified, email_verification_token)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (username, name.strip(), email.lower().strip(), password_hash, 0, age, date_of_birth, is_email_verified, email_verification_token)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_user_by_id(user_id)

def update_user_profile(user_id: int, name: Optional[str] = None, age: Optional[int] = None, date_of_birth: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    fields = []
    vals = []
    if name is not None:
        fields.append("name = ?")
        vals.append(name.strip())
    if age is not None:
        fields.append("age = ?")
        vals.append(age)
    if date_of_birth is not None:
        fields.append("date_of_birth = ?")
        vals.append(date_of_birth)
    if not fields:
        conn.close()
        return get_user_by_id(user_id)
    vals.append(user_id)
    cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", tuple(vals))
    conn.commit()
    conn.close()
    return get_user_by_id(user_id)

def update_user_password(user_id: int, new_password_hash: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return bool(affected > 0)

def set_email_verification_token(user_id: int, token: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email_verification_token = ?, is_email_verified = 0 WHERE id = ?", (token, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return bool(affected > 0)

def verify_user_email_token(token: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email_verification_token = ?", (token,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    user_id = row["id"]
    cursor.execute("UPDATE users SET is_email_verified = 1, email_verification_token = NULL WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return get_user_by_id(user_id)

def save_analysis_feedback(analysis_id: int, user_id: int, feedback: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE analyses SET user_feedback = ? WHERE id = ? AND user_id = ?", (feedback, analysis_id, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return bool(affected > 0)

def save_analysis(
    user_id: int,
    input_text: str,
    primary_emotion: str,
    emotion_confidence: float,
    emotion_distribution: Dict[str, float],
    stress_level: str,
    stress_confidence: float,
    wellness_score: int,
    wellness_status: str,
    trend_direction: str,
    trend_entries: int,
    insight: str,
    recommendations: List[str],
    context_signals: List[Dict[str, Any]],
    created_at: Optional[str] = None
) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    if created_at:
        cursor.execute("""
            INSERT INTO analyses (
                user_id, input_text, primary_emotion, emotion_confidence,
                emotion_distribution, stress_level, stress_confidence,
                wellness_score, wellness_status, trend_direction,
                trend_entries, insight, recommendations, context_signals, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, input_text, primary_emotion, emotion_confidence,
            json.dumps(emotion_distribution), stress_level, stress_confidence,
            wellness_score, wellness_status, trend_direction,
            trend_entries, insight, json.dumps(recommendations),
            json.dumps(context_signals), created_at
        ))
    else:
        cursor.execute("""
            INSERT INTO analyses (
                user_id, input_text, primary_emotion, emotion_confidence,
                emotion_distribution, stress_level, stress_confidence,
                wellness_score, wellness_status, trend_direction,
                trend_entries, insight, recommendations, context_signals
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, input_text, primary_emotion, emotion_confidence,
            json.dumps(emotion_distribution), stress_level, stress_confidence,
            wellness_score, wellness_status, trend_direction,
            trend_entries, insight, json.dumps(recommendations),
            json.dumps(context_signals)
        ))
    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return analysis_id

def get_analyses_for_user(user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (user_id, limit, offset)
    )
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        d = dict(r)
        d["emotion_distribution"] = json.loads(d["emotion_distribution"])
        d["recommendations"] = json.loads(d["recommendations"])
        d["context_signals"] = json.loads(d["context_signals"])
        results.append(d)
    return results

def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["emotion_distribution"] = json.loads(d["emotion_distribution"])
        d["recommendations"] = json.loads(d["recommendations"])
        d["context_signals"] = json.loads(d["context_signals"])
        return d
    return None

def count_analyses_for_user(user_id: int) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM analyses WHERE user_id = ?", (user_id,))
    cnt = cursor.fetchone()[0]
    conn.close()
    return cnt

def get_current_streak_for_user(user_id: int) -> int:
    """Count consecutive calendar days with at least one reflection.

    Multiple entries on the same day count once.  The streak is intentionally
    calculated from the user's own records instead of being a seeded profile
    field, so it remains correct after a new analysis is saved.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT date(created_at) AS entry_date FROM analyses "
        "WHERE user_id = ? ORDER BY entry_date DESC",
        (user_id,)
    )
    dates = [row["entry_date"] for row in cursor.fetchall()]
    conn.close()
    if not dates:
        return 0

    from datetime import date, timedelta
    today = date.today()
    try:
        most_recent = date.fromisoformat(dates[0])
    except Exception:
        return 0

    # Streak is active only if reflection was recorded today or yesterday
    if (today - most_recent).days > 1:
        return 0

    streak = 1
    expected = most_recent - timedelta(days=1)
    for value in dates[1:]:
        try:
            current = date.fromisoformat(value)
        except Exception:
            break
        if current != expected:
            break
        streak += 1
        expected -= timedelta(days=1)
    return streak

def delete_analyses_for_user(user_id: int) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def set_history_saving_for_user(user_id: int, enabled: bool) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET save_history = ? WHERE id = ?", (1 if enabled else 0, user_id))
    conn.commit()
    conn.close()

def save_conversation_session(
    session_id: str,
    user_id: int,
    status: str,
    turn_count: int,
    initial_text: str,
    turns_data: List[Dict[str, Any]],
    final_analysis_id: Optional[int] = None
) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO conversation_sessions (
            id, user_id, status, turn_count, initial_text, turns_data, final_analysis_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id, user_id, status, turn_count, initial_text, json.dumps(turns_data), final_analysis_id
    ))
    conn.commit()
    conn.close()

def get_conversation_session(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversation_sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data["turns_data"] = json.loads(data["turns_data"]) if data.get("turns_data") else []
    return data

def update_conversation_session(
    session_id: str,
    status: str,
    turn_count: int,
    turns_data: List[Dict[str, Any]],
    final_analysis_id: Optional[int] = None
) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE conversation_sessions
        SET status = ?, turn_count = ?, turns_data = ?, final_analysis_id = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        status, turn_count, json.dumps(turns_data), final_analysis_id, session_id
    ))
    conn.commit()
    conn.close()

def save_recommendation(
    user_id: int,
    category: str,
    title: str,
    description: str,
    analysis_id: Optional[int] = None
) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO saved_recommendations (user_id, analysis_id, category, title, description, is_completed)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (user_id, analysis_id, category.strip(), title.strip(), description.strip()))
    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id

def get_saved_recommendations(user_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM saved_recommendations
        WHERE user_id = ?
        ORDER BY saved_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_saved_recommendation(user_id: int, rec_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_recommendations WHERE id = ? AND user_id = ?", (rec_id, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return bool(affected > 0)

def toggle_recommendation_status(user_id: int, rec_id: int, is_completed: Optional[bool] = None) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_recommendations WHERE id = ? AND user_id = ?", (rec_id, user_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    curr_status = row["is_completed"]
    new_status = 1 if (is_completed if is_completed is not None else not curr_status) else 0
    cursor.execute("UPDATE saved_recommendations SET is_completed = ? WHERE id = ? AND user_id = ?", (new_status, rec_id, user_id))
    conn.commit()
    cursor.execute("SELECT * FROM saved_recommendations WHERE id = ? AND user_id = ?", (rec_id, user_id))
    updated = cursor.fetchone()
    conn.close()
    return dict(updated) if updated else None

