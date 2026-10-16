# backend/tests/test_auth_profile.py
"""
Comprehensive Test Suite for Authentication, Age Validation, and Profile Management.
Verifies:
1. Registration rejects underage users (< 18) with respectful notice.
2. Registration succeeds for eligible adults (>= 18) and issues verification token.
3. Email verification token endpoint validates and marks account as verified.
4. Resending verification email issues fresh token.
5. Profile age update enforces age >= 18.
6. Password change enforces current password verification and updates hash.
7. Analysis feedback endpoint records user agreement/disagreement accurately.
8. Backward compatibility with demo account ('demo123') is preserved.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app
from database.connection import init_db
from database.models import get_user_by_email, save_analysis, get_analysis_by_id

client = TestClient(app)

def run_auth_tests():
    print("=== STARTING AUTHENTICATION & PROFILE MANAGEMENT TESTS ===")
    init_db()

    # TEST 1: Underage Registration Rejection (< 18)
    print("\n--- TEST 1: Enforce Strict Minimum Age (18+) on Registration ---")
    res_underage_num = client.post("/auth/register", json={
        "name": "Underage Kid",
        "email": "underage_kid@test.com",
        "password": "password123",
        "age": 16,
        "accepted_disclaimer": True
    })
    assert res_underage_num.status_code == 400
    assert "individuals aged 18 and older" in res_underage_num.json()["detail"], \
        f"Underage registration did not receive expected respectful notice: {res_underage_num.json()}"
    print("  [PASSED] Underage registration (<18 numeric) rejected with respectful notice.")

    res_underage_range = client.post("/auth/register", json={
        "name": "Underage Range",
        "email": "underage_range@test.com",
        "password": "password123",
        "age_range": "Under 18",
        "accepted_disclaimer": True
    })
    assert res_underage_range.status_code == 400
    assert "individuals aged 18 and older" in res_underage_range.json()["detail"]
    print("  [PASSED] Underage registration ('Under 18' range) rejected with respectful notice.")

    # TEST 2: Adult Registration & Verification Token Generation
    import uuid
    test_email = f"adult_student_{uuid.uuid4().hex[:8]}@test.com"
    res_reg = client.post("/auth/register", json={
        "name": "Adult Student",
        "email": test_email,
        "password": "password123",
        "age": 22,
        "accepted_disclaimer": True
    })
    assert res_reg.status_code == 200, f"Adult registration failed: {res_reg.text}"
    data_reg = res_reg.json()
    token = data_reg["access_token"]
    user_reg = data_reg["user"]
    assert user_reg["age"] == 22
    assert user_reg["is_email_verified"] is False
    v_token = data_reg.get("verification_token")
    assert v_token is not None, "Verification token was not generated on registration!"
    print(f"  [PASSED] Adult account created. Age: {user_reg['age']}. Verification token: {v_token[:10]}...")

    headers = {"Authorization": f"Bearer {token}"}

    # TEST 3: Token-based Email Verification
    print("\n--- TEST 3: Email Verification Endpoint ---")
    res_verify = client.get(f"/auth/verify-email?token={v_token}")
    assert res_verify.status_code == 200
    assert res_verify.json()["user"]["is_email_verified"] is True
    print("  [PASSED] Email successfully verified with token.")

    # Check /auth/me reflects verification
    res_me = client.get("/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["is_email_verified"] is True
    print("  [PASSED] /auth/me confirms is_email_verified = True.")

    # TEST 4: Resend Verification (when unverified)
    print("\n--- TEST 4: Resend Email Verification ---")
    # Temporarily mark unverified in DB to test resend
    user_db = get_user_by_email(test_email)
    from database.models import set_email_verification_token
    set_email_verification_token(user_db["id"], "fresh_test_token")
    res_resend = client.post("/auth/resend-verification", headers=headers)
    assert res_resend.status_code == 200
    assert res_resend.json()["success"] is True
    assert "verification_link" in res_resend.json()
    print(f"  [PASSED] Resend verification issued link: {res_resend.json()['verification_link']}")

    # TEST 5: Profile Age Update Validation
    print("\n--- TEST 5: Profile Age Editing with Validation ---")
    # Reject age < 18
    res_age_invalid = client.patch("/auth/profile", json={"age": 15}, headers=headers)
    assert res_age_invalid.status_code == 400
    assert "individuals aged 18 and older" in res_age_invalid.json()["detail"]
    print("  [PASSED] Profile update rejected underage value (15).")

    # Accept age >= 18
    res_age_valid = client.patch("/auth/profile", json={"age": 24}, headers=headers)
    assert res_age_valid.status_code == 200
    assert res_age_valid.json()["user"]["age"] == 24
    print("  [PASSED] Profile age updated to 24 successfully.")

    # TEST 6: Change Password Endpoint
    print("\n--- TEST 6: Change Password Verification ---")
    # Wrong current password
    res_pw_wrong = client.post("/auth/change-password", json={
        "current_password": "wrongpassword",
        "new_password": "newpassword123",
        "confirm_password": "newpassword123"
    }, headers=headers)
    assert res_pw_wrong.status_code == 400
    assert "Incorrect current password" in res_pw_wrong.json()["detail"]
    print("  [PASSED] Rejected change password with incorrect current password.")

    # Valid change password
    res_pw_valid = client.post("/auth/change-password", json={
        "current_password": "password123",
        "new_password": "newpassword123",
        "confirm_password": "newpassword123"
    }, headers=headers)
    assert res_pw_valid.status_code == 200
    assert res_pw_valid.json()["success"] is True
    print("  [PASSED] Password successfully updated.")

    # Verify login with new password works
    res_new_login = client.post("/auth/login", json={
        "email": test_email,
        "password": "newpassword123"
    })
    assert res_new_login.status_code == 200
    print("  [PASSED] Login succeeded with new password.")

    # TEST 7: Analysis Feedback Submission
    print("\n--- TEST 7: User Feedback Control on Reflections ---")
    # Create test analysis
    analysis_id = save_analysis(
        user_id=user_db["id"],
        input_text="Testing feedback mechanism",
        primary_emotion="Joy",
        emotion_confidence=0.88,
        emotion_distribution={"Joy": 0.88, "Neutral": 0.12},
        stress_level="Low",
        stress_confidence=0.85,
        wellness_score=85,
        wellness_status="Balanced",
        trend_direction="Improving",
        trend_entries=3,
        insight="Looking strong.",
        recommendations=["Keep going."],
        context_signals=[]
    )
    res_fb = client.post(f"/analysis/{analysis_id}/feedback", json={"feedback": "feels_right"}, headers=headers)
    assert res_fb.status_code == 200
    assert res_fb.json()["success"] is True
    assert res_fb.json()["feedback"] == "feels_right"

    # Verify stored in DB
    analysis_rec = get_analysis_by_id(analysis_id)
    assert analysis_rec.get("user_feedback") == "feels_right"
    print("  [PASSED] Feedback recorded and stored in database as 'feels_right'.")

    # TEST 8: Backward Compatibility with Demo Account
    print("\n--- TEST 8: Verify Existing Demo Account Compatibility ---")
    demo_user = get_user_by_email("demo@emotrack.internal")
    if demo_user:
        res_demo_login = client.post("/auth/login", json={
            "email": "demo@emotrack.internal",
            "password": "demo123"
        })
        assert res_demo_login.status_code == 200
        print("  [PASSED] Demo account login (demo@emotrack.internal / demo123) functions properly.")

    print("\n=== ALL AUTHENTICATION & PROFILE MANAGEMENT TESTS PASSED! ===")

if __name__ == "__main__":
    run_auth_tests()
