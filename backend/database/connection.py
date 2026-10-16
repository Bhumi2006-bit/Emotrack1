# backend/database/connection.py
import sqlite3
from pathlib import Path
from app.config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        age INTEGER DEFAULT 18,
        date_of_birth TEXT,
        is_email_verified INTEGER DEFAULT 0,
        email_verification_token TEXT,
        verification_token_expires_at TIMESTAMP,
        streak_days INTEGER DEFAULT 1,
        save_history INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Lightweight migration for databases created by earlier project builds.
    user_columns = {row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()}
    if "save_history" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN save_history INTEGER DEFAULT 1")
    if "age" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN age INTEGER DEFAULT 18")
    if "date_of_birth" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN date_of_birth TEXT")
    if "is_email_verified" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_email_verified INTEGER DEFAULT 0")
    if "email_verification_token" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email_verification_token TEXT")
    if "verification_token_expires_at" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN verification_token_expires_at TIMESTAMP")

    # Analyses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        input_text TEXT NOT NULL,
        primary_emotion TEXT NOT NULL,
        emotion_confidence REAL NOT NULL,
        emotion_distribution TEXT NOT NULL, -- JSON string
        stress_level TEXT NOT NULL,
        stress_confidence REAL NOT NULL,
        wellness_score INTEGER NOT NULL,
        wellness_status TEXT NOT NULL,
        trend_direction TEXT NOT NULL,
        trend_entries INTEGER NOT NULL,
        insight TEXT NOT NULL,
        recommendations TEXT NOT NULL, -- JSON string
        context_signals TEXT NOT NULL, -- JSON string
        user_feedback TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    analysis_columns = {row[1] for row in cursor.execute("PRAGMA table_info(analyses)").fetchall()}
    if "user_feedback" not in analysis_columns:
        cursor.execute("ALTER TABLE analyses ADD COLUMN user_feedback TEXT")

    # Saved Recommendations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        analysis_id INTEGER,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        is_completed INTEGER DEFAULT 0,
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (analysis_id) REFERENCES analyses(id)
    );
    """)

    # Conversation Sessions (Multi-turn assessment sessions)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversation_sessions (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        status TEXT NOT NULL, -- 'active', 'completed'
        turn_count INTEGER DEFAULT 1,
        initial_text TEXT NOT NULL,
        turns_data TEXT NOT NULL, -- JSON list of turn objects
        final_analysis_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (final_analysis_id) REFERENCES analyses(id)
    );
    """)

    conn.commit()
    conn.close()
