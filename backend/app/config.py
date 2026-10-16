# backend/app/config.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.environ.get("EMOTRACK_DB_PATH", str(BASE_DIR / "emotrack.db"))
PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")

# Security / Demo defaults
SECRET_KEY = os.environ.get("SECRET_KEY", "emotrack-demo-secret-key-2026")
ALGORITHM = "HS256"
