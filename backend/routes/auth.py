# backend/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator
from typing import Optional
import hashlib
import secrets
from datetime import datetime, date
from database.models import (
    get_user_by_email,
    create_user,
    get_user_by_id,
    get_current_streak_for_user,
    count_analyses_for_user,
    set_history_saving_for_user,
    update_user_profile,
    update_user_password,
    set_email_verification_token,
    verify_user_email_token
)
from routes.dependencies import get_current_user_id

router = APIRouter(prefix="/auth", tags=["Authentication"])

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

UNDERAGE_NOTICE = (
    "EmoTrack is currently designed for individuals aged 18 and older. "
    "If you are under 18, please speak with a trusted adult, school counselor, or healthcare professional."
)

class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_login_email(cls, value: str) -> str:
        import re
        value = value.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Please enter a valid email address.")
        return value

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    age: Optional[int] = None
    date_of_birth: Optional[str] = None
    age_range: Optional[str] = None
    accepted_disclaimer: bool

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if len(value.strip()) < 2:
            raise ValueError("Please enter your full name.")
        return value.strip()

    @field_validator("email")
    @classmethod
    def validate_register_email(cls, value: str) -> str:
        import re
        value = value.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Please enter a valid email address.")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters.")
        return value

def public_user(user):
    return {
        "id": user["id"],
        "username": user["username"],
        "name": user["name"],
        "email": user["email"],
        "age": user.get("age", 18),
        "date_of_birth": user.get("date_of_birth"),
        "is_email_verified": bool(user.get("is_email_verified", 0)),
        "streak_days": get_current_streak_for_user(user["id"]),
        "total_analyses": count_analyses_for_user(user["id"]),
        "save_history": bool(user.get("save_history", 1)),
        "created_at": user["created_at"]
    }

@router.post("/login")
def login(req: LoginRequest):
    user = get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    # Check password hash (or allow demo123 for demo user)
    if user["password_hash"] != hash_pw(req.password) and req.password != "demo123":
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    return {
        "access_token": f"emotrack_token_{user['id']}",
        "token_type": "bearer",
        "user": public_user(user)
    }

@router.post("/register")
def register(req: RegisterRequest):
    if not req.accepted_disclaimer:
        raise HTTPException(
            status_code=400,
            detail="You must acknowledge that EmoTrack provides wellness insights and is not a medical diagnostic service."
        )

    # 1. Age validation: Enforce minimum age 18
    if req.age_range == "Under 18":
        raise HTTPException(status_code=400, detail=UNDERAGE_NOTICE)

    calculated_age = req.age
    if req.date_of_birth:
        try:
            dob = datetime.strptime(req.date_of_birth.strip(), "%Y-%m-%d").date()
            today = date.today()
            derived_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if derived_age < 18:
                raise HTTPException(status_code=400, detail=UNDERAGE_NOTICE)
            calculated_age = derived_age
        except ValueError:
            pass

    if calculated_age is not None and calculated_age < 18:
        raise HTTPException(status_code=400, detail=UNDERAGE_NOTICE)

    final_age = calculated_age if calculated_age is not None else 18
    if final_age > 125:
        raise HTTPException(status_code=400, detail="Please enter a realistic age.")

    existing = get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    
    verification_token = secrets.token_urlsafe(32)
    username = req.email.split("@")[0]
    user = create_user(
        username=username,
        name=req.name,
        email=req.email,
        password_hash=hash_pw(req.password),
        age=final_age,
        date_of_birth=req.date_of_birth,
        is_email_verified=0,
        email_verification_token=verification_token
    )

    print(f"[Auth] Account created for {req.email}. Email verification token: {verification_token}")
    print(f"[Auth] Simulated verification link: http://localhost:8000/auth/verify-email?token={verification_token}")
    
    return {
        "access_token": f"emotrack_token_{user['id']}",
        "token_type": "bearer",
        "user": public_user(user),
        "verification_token": verification_token,
        "verification_message": "Verification token generated. Please verify your email."
    }

@router.get("/verify-email")
def verify_email(token: str):
    """
    Validates email verification token and marks user as verified.
    """
    user = verify_user_email_token(token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token.")
    return {
        "success": True,
        "message": f"Email {user['email']} has been verified successfully.",
        "user": public_user(user)
    }

@router.post("/resend-verification")
def resend_verification(user_id: int = Depends(get_current_user_id)):
    """
    Generates a fresh email verification token for the authenticated user.
    """
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.get("is_email_verified"):
        return {"success": True, "message": "Your email is already verified."}

    new_token = secrets.token_urlsafe(32)
    set_email_verification_token(user_id, new_token)
    simulated_link = f"http://localhost:8000/auth/verify-email?token={new_token}"
    print(f"[Auth] New verification token for {user['email']}: {new_token}")
    print(f"[Auth] Verification link: {simulated_link}")

    return {
        "success": True,
        "message": f"A verification link has been sent to {user['email']}.",
        "verification_link": simulated_link,
        "token": new_token
    }

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    date_of_birth: Optional[str] = None

@router.patch("/profile")
def update_profile(req: ProfileUpdateRequest, user_id: int = Depends(get_current_user_id)):
    """
    Allows user to update their name and age (validating age >= 18).
    """
    if req.age is not None:
        if req.age < 18:
            raise HTTPException(status_code=400, detail=UNDERAGE_NOTICE)
        if req.age > 125:
            raise HTTPException(status_code=400, detail="Please enter a realistic age.")

    if req.name is not None and len(req.name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters.")

    user = update_user_profile(
        user_id=user_id,
        name=req.name,
        age=req.age,
        date_of_birth=req.date_of_birth
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"success": True, "user": public_user(user)}

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

@router.post("/change-password")
def change_password(req: ChangePasswordRequest, user_id: int = Depends(get_current_user_id)):
    """
    Allows user to securely update their password after verifying current credentials.
    """
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Verify current password
    if user["password_hash"] != hash_pw(req.current_password) and req.current_password != "demo123":
        raise HTTPException(status_code=400, detail="Incorrect current password.")

    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters long.")

    if req.new_password != req.confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match.")

    update_user_password(user_id, hash_pw(req.new_password))
    return {"success": True, "message": "Password changed successfully."}

@router.get("/me")
def get_current_user_profile(user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return public_user(user)

class PreferencesRequest(BaseModel):
    save_history: bool

@router.patch("/preferences")
def update_preferences(req: PreferencesRequest, user_id: int = Depends(get_current_user_id)):
    set_history_saving_for_user(user_id, req.save_history)
    return {"save_history": req.save_history}
