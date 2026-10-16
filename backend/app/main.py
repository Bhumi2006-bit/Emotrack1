# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.connection import init_db
from database.seed_data import seed_database
from routes.auth import router as auth_router
from routes.analysis import router as analysis_router
from routes.dashboard import router as dashboard_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed demo user Bhumi
    init_db()
    seed_database()
    print("EmoTrack API ready with initialized database and seeded entries.")
    yield
    # Shutdown

app = FastAPI(
    title="EmoTrack API",
    description="AI-Powered Emotional Wellness & Self-Reflection Platform Backend",
    version="1.0.0",
    lifespan=lifespan
)

import os

# Configurable CORS for production deployment
cors_origins_raw = os.environ.get("CORS_ORIGINS", "*")
if cors_origins_raw == "*" or not cors_origins_raw.strip():
    cors_origins = ["*"]
else:
    cors_origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(dashboard_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "EmoTrack API",
        "version": "1.0.0",
        "mode": "Live Backend"
    }

if __name__ == "__main__":
    import uvicorn
    from app.config import HOST, PORT
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
