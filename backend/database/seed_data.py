# backend/database/seed_data.py
import hashlib
from datetime import datetime, timedelta
from database.connection import get_db_connection
from database.models import get_user_by_email, create_user, save_analysis

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

SAMPLE_ENTRIES = [
    {
        "text": "I finally finished my major project submission and feel really relieved and happy with the result.",
        "emotion": "Joy",
        "emotion_conf": 0.94,
        "dist": {"Joy": 0.94, "Neutral": 0.03, "Surprise": 0.015, "Sadness": 0.005, "Fear": 0.004, "Anger": 0.003, "Disgust": 0.003},
        "stress": "Low",
        "stress_conf": 0.88,
        "wellness": 78,
        "status": "Positive Pattern",
        "trend": "Improving",
        "entries": 24,
        "insight": "Completion of high-effort milestones consistently correlates with marked elevation in your wellness indicator.",
        "recs": ["Celebrate this milestone with an intentional rest period.", "Take a walk to let your body unwind after intense focus.", "Acknowledge the effort you put in."],
        "signals": [{"word": "finally finished", "weight": 0.92}, {"word": "relieved", "weight": 0.88}, {"word": "happy", "weight": 0.85}],
        "days_ago": 0, "hours_ago": 2
    },
    {
        "text": "Had a quiet, productive morning reviewing research papers and organizing notes.",
        "emotion": "Neutral",
        "emotion_conf": 0.85,
        "dist": {"Neutral": 0.85, "Joy": 0.08, "Sadness": 0.03, "Fear": 0.02, "Surprise": 0.01, "Anger": 0.005, "Disgust": 0.005},
        "stress": "Low",
        "stress_conf": 0.82,
        "wellness": 72,
        "status": "Balanced",
        "trend": "Stable",
        "entries": 23,
        "insight": "Quiet, structured mornings serve as a stabilizing anchor across your weekly reflections.",
        "recs": ["Maintain this calm pacing throughout the rest of your day.", "Hydrate and stretch before your next task."],
        "signals": [{"word": "quiet", "weight": 0.82}, {"word": "productive", "weight": 0.79}, {"word": "organizing", "weight": 0.65}],
        "days_ago": 1, "hours_ago": 4
    },
    {
        "text": "I have so much work left and I'm worried about tomorrow's presentation. Feeling the pressure build up.",
        "emotion": "Fear",
        "emotion_conf": 0.89,
        "dist": {"Fear": 0.89, "Sadness": 0.05, "Neutral": 0.03, "Anger": 0.015, "Joy": 0.008, "Surprise": 0.004, "Disgust": 0.003},
        "stress": "High",
        "stress_conf": 0.91,
        "wellness": 42,
        "status": "Needs Attention",
        "trend": "Needs Attention",
        "entries": 22,
        "insight": "Upcoming public speaking and evaluative deadlines repeatedly trigger transient spikes in perceived urgency.",
        "recs": ["Practice a 5-minute box breathing cycle to steady your autonomic response.", "Rehearse only the first 2 minutes of your talk.", "Remind yourself of past successful presentations."],
        "signals": [{"word": "worried", "weight": 0.91}, {"word": "pressure build up", "weight": 0.87}, {"word": "so much work", "weight": 0.74}],
        "days_ago": 2, "hours_ago": 6
    },
    {
        "text": "Spent a relaxing evening talking with close friends over chai. It was just what I needed.",
        "emotion": "Joy",
        "emotion_conf": 0.91,
        "dist": {"Joy": 0.91, "Neutral": 0.05, "Surprise": 0.02, "Sadness": 0.01, "Fear": 0.005, "Anger": 0.003, "Disgust": 0.002},
        "stress": "Low",
        "stress_conf": 0.89,
        "wellness": 76,
        "status": "Positive Pattern",
        "trend": "Improving",
        "entries": 21,
        "insight": "Casual social interactions act as a natural decompression mechanism for academic tension.",
        "recs": ["Continue scheduling gentle social touchpoints during busy weeks.", "Savor the feeling of mutual support."],
        "signals": [{"word": "relaxing evening", "weight": 0.89}, {"word": "just what I needed", "weight": 0.84}, {"word": "close friends", "weight": 0.78}],
        "days_ago": 3, "hours_ago": 5
    },
    {
        "text": "Feeling a bit drained and sluggish today. Nothing went wrong, just feeling flat.",
        "emotion": "Sadness",
        "emotion_conf": 0.76,
        "dist": {"Sadness": 0.76, "Neutral": 0.16, "Fear": 0.03, "Joy": 0.02, "Anger": 0.015, "Surprise": 0.01, "Disgust": 0.005},
        "stress": "Moderate",
        "stress_conf": 0.71,
        "wellness": 55,
        "status": "Balanced",
        "trend": "Stable",
        "entries": 20,
        "insight": "Periods of low physiological energy appear after high-focus exertion cycles.",
        "recs": ["Allow yourself an early night without guilt.", "Keep tonight's to-do list minimal."],
        "signals": [{"word": "drained", "weight": 0.85}, {"word": "sluggish", "weight": 0.78}, {"word": "feeling flat", "weight": 0.72}],
        "days_ago": 4, "hours_ago": 8
    },
    {
        "text": "Made steady progress on chapter 3 today. Took regular breaks and listened to calm music.",
        "emotion": "Joy",
        "emotion_conf": 0.84,
        "dist": {"Joy": 0.84, "Neutral": 0.11, "Surprise": 0.02, "Sadness": 0.015, "Fear": 0.008, "Anger": 0.004, "Disgust": 0.003},
        "stress": "Low",
        "stress_conf": 0.86,
        "wellness": 74,
        "status": "Positive Pattern",
        "trend": "Improving",
        "entries": 19,
        "insight": "Incorporating structured micro-breaks preserves positive mood momentum.",
        "recs": ["Reinforce the study-break rhythm tomorrow.", "Note down 1 win before sleeping."],
        "signals": [{"word": "steady progress", "weight": 0.83}, {"word": "calm music", "weight": 0.75}, {"word": "regular breaks", "weight": 0.71}],
        "days_ago": 5, "hours_ago": 3
    },
    {
        "text": "Received unexpected encouraging feedback on my thesis draft from my advisor!",
        "emotion": "Surprise",
        "emotion_conf": 0.81,
        "dist": {"Surprise": 0.81, "Joy": 0.15, "Neutral": 0.02, "Fear": 0.01, "Sadness": 0.005, "Anger": 0.003, "Disgust": 0.002},
        "stress": "Low",
        "stress_conf": 0.84,
        "wellness": 80,
        "status": "Positive Pattern",
        "trend": "Improving",
        "entries": 18,
        "insight": "Affirmative external validation triggers sudden positive wellness shifts.",
        "recs": ["Save this feedback to re-read on harder days.", "Carry this validation forward gently."],
        "signals": [{"word": "unexpected", "weight": 0.88}, {"word": "encouraging feedback", "weight": 0.84}],
        "days_ago": 6, "hours_ago": 7
    },
    {
        "text": "Feeling slightly overwhelmed by multiple pending assignments, but trying to take it one step at a time.",
        "emotion": "Fear",
        "emotion_conf": 0.78,
        "dist": {"Fear": 0.78, "Neutral": 0.10, "Sadness": 0.06, "Joy": 0.03, "Anger": 0.015, "Surprise": 0.01, "Disgust": 0.005},
        "stress": "Moderate",
        "stress_conf": 0.79,
        "wellness": 58,
        "status": "Balanced",
        "trend": "Stable",
        "entries": 17,
        "insight": "Self-regulation strategies ('one step at a time') buffer against escalating anxiety.",
        "recs": ["Write out only the top 2 tasks for tomorrow morning.", "Step away from screens for 20 minutes."],
        "signals": [{"word": "overwhelmed", "weight": 0.84}, {"word": "pending assignments", "weight": 0.76}, {"word": "one step at a time", "weight": 0.68}],
        "days_ago": 7, "hours_ago": 4
    }
]

# Additional 16 historical entries to bring total entries to 24
ADDITIONAL_ENTRIES = [
    ("Morning walk in the garden, crisp air helped clear my thoughts.", "Joy", 0.82, "Low", 0.85, 75, "Positive Pattern", 8),
    ("Lab experiment had a glitch, frustrating to redo the measurements.", "Anger", 0.74, "Moderate", 0.77, 52, "Needs Attention", 9),
    ("Standard study routine, completed problem sets without friction.", "Neutral", 0.88, "Low", 0.83, 68, "Balanced", 10),
    ("Read an interesting chapter on neural network representations.", "Joy", 0.86, "Low", 0.89, 73, "Positive Pattern", 11),
    ("Woke up feeling anxious about seminar questions.", "Fear", 0.79, "High", 0.85, 46, "Needs Attention", 12),
    ("Seminar went much smoother than expected! Felt proud answering.", "Joy", 0.92, "Low", 0.90, 82, "Positive Pattern", 13),
    ("Rainy afternoon reading with tea, quiet peaceful rhythm.", "Joy", 0.89, "Low", 0.91, 79, "Positive Pattern", 14),
    ("Tired after consecutive back-to-back lectures.", "Neutral", 0.80, "Moderate", 0.72, 60, "Balanced", 15),
    ("Frustrated with delays in dataset cleaning scripts.", "Anger", 0.71, "Moderate", 0.75, 54, "Needs Attention", 16),
    ("Fixed the bugs in the preprocessing code, great feeling of clarity.", "Joy", 0.87, "Low", 0.84, 76, "Positive Pattern", 17),
    ("Long commute back home, feeling worn out and fatigued.", "Sadness", 0.75, "Moderate", 0.74, 53, "Needs Attention", 18),
    ("Meal prep with family on Sunday, grounding and warm.", "Joy", 0.93, "Low", 0.92, 84, "Positive Pattern", 19),
    ("Reviewed weekly goals, feeling organized and ready.", "Neutral", 0.86, "Low", 0.81, 70, "Balanced", 20),
    ("A bit nervous before meeting the project panel.", "Fear", 0.75, "Moderate", 0.79, 56, "Balanced", 21),
    ("Panel gave constructive insights, excited to implement revisions.", "Joy", 0.85, "Low", 0.83, 75, "Positive Pattern", 22),
    ("Early morning meditation, starting the week centered.", "Joy", 0.88, "Low", 0.87, 77, "Positive Pattern", 23),
]

def seed_database():
    demo_email = "demo@emotrack.ai"
    existing_user = get_user_by_email(demo_email)
    if not existing_user:
        user = create_user(
            username="demo_preview",
            name="Demo User",
            email=demo_email,
            password_hash=hash_pw("demo123")
        )
        user_id = user["id"]
    else:
        user_id = existing_user["id"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM analyses WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()

    if count < 20:
        now = datetime.now()
        # Seed the 8 primary detailed entries
        for item in SAMPLE_ENTRIES:
            entry_time = (now - timedelta(days=item["days_ago"], hours=item["hours_ago"])).strftime("%Y-%m-%d %H:%M:%S")
            save_analysis(
                user_id=user_id,
                input_text=item["text"],
                primary_emotion=item["emotion"],
                emotion_confidence=item["emotion_conf"],
                emotion_distribution=item["dist"],
                stress_level=item["stress"],
                stress_confidence=item["stress_conf"],
                wellness_score=item["wellness"],
                wellness_status=item["status"],
                trend_direction=item["trend"],
                trend_entries=item["entries"],
                insight=item["insight"],
                recommendations=item["recs"],
                context_signals=item["signals"],
                created_at=entry_time
            )
            
        # Seed additional entries to reach 24
        for text, emo, conf, stress, s_conf, well, stat, d_ago in ADDITIONAL_ENTRIES:
            entry_time = (now - timedelta(days=d_ago, hours=3)).strftime("%Y-%m-%d %H:%M:%S")
            save_analysis(
                user_id=user_id,
                input_text=text,
                primary_emotion=emo,
                emotion_confidence=conf,
                emotion_distribution={emo: conf, "Neutral": round(max(0.01, 1.0 - conf), 2)},
                stress_level=stress,
                stress_confidence=s_conf,
                wellness_score=well,
                wellness_status=stat,
                trend_direction="Stable",
                trend_entries=24 - d_ago,
                insight="Historical reflection recorded during regular self-check-in.",
                recommendations=["Maintain regular reflection intervals."],
                context_signals=[{"word": text.split()[0].lower(), "weight": 0.7}],
                created_at=entry_time
            )
        print("Database seeded with 24 sample entries for the read-only demo.")
