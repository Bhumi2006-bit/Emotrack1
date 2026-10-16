# backend/tests/test_recommendation_isolation.py
"""
Tests recommendation persistence, authentication ownership, and user isolation.
"""
import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from database.connection import init_db
from database.seed_data import seed_database
from database.models import get_user_by_email, create_user
import hashlib

def run_tests():
    print("=== Testing Recommendation Ownership and User Isolation ===")
    init_db()
    seed_database()
    client = TestClient(app)

    # 1. Ensure user 1 and user 2 exist in DB
    u1 = get_user_by_email("demo@emotrack.ai")
    assert u1 is not None, "Demo user should exist after seeding"
    u1_id = u1["id"]

    u2 = get_user_by_email("user2@emotrack.internal")
    if not u2:
        u2 = create_user(
            username="user2",
            name="Second User",
            email="user2@emotrack.internal",
            password_hash=hashlib.sha256("password123".encode()).hexdigest()
        )
    u2_id = u2["id"]

    headers_u1 = {"Authorization": f"Bearer emotrack_token_{u1_id}"}
    headers_u2 = {"Authorization": f"Bearer emotrack_token_{u2_id}"}

    # 2. User 1 saves a practice recommendation
    save_payload = {
        "items": [
            {
                "analysis_id": 1,
                "title": "Box Breathing",
                "description": "Practice 5-minute box breathing before bed.",
                "category": "Mindfulness"
            }
        ]
    }
    res_save = client.post("/analysis/recommendations/save", json=save_payload, headers=headers_u1)
    assert res_save.status_code == 200, f"Failed to save recommendation: {res_save.text}"
    saved_data = res_save.json()
    rec_id = saved_data["saved_ids"][0]
    print(f"  [PASSED] User 1 saved recommendation ID {rec_id}")

    # 3. User 1 retrieves recommendations -> should have rec_id
    res_get1 = client.get("/analysis/recommendations", headers=headers_u1)
    assert res_get1.status_code == 200
    u1_items = res_get1.json()["items"]
    assert any(r["id"] == rec_id for r in u1_items)
    print(f"  [PASSED] User 1 retrieved saved recommendation (Count: {len(u1_items)})")

    # 4. User 2 retrieves recommendations -> must NOT see User 1's recommendation
    res_get2 = client.get("/analysis/recommendations", headers=headers_u2)
    assert res_get2.status_code == 200
    u2_items = res_get2.json()["items"]
    assert not any(r["id"] == rec_id for r in u2_items), "CRITICAL LEAK: User 2 saw User 1's recommendation!"
    print(f"  [PASSED] User isolation verified: User 2 cannot see User 1's recommendation.")

    # 5. User 2 tries to toggle User 1's recommendation -> must fail with 404
    res_toggle_unauthorized = client.patch(f"/analysis/recommendations/{rec_id}/toggle", headers=headers_u2)
    assert res_toggle_unauthorized.status_code == 404, f"Expected 404 unauthorized toggle, got {res_toggle_unauthorized.status_code}"
    print(f"  [PASSED] User 2 unauthorized toggle blocked with 404.")

    # 6. User 1 toggles status -> succeeds
    res_toggle_u1 = client.patch(f"/analysis/recommendations/{rec_id}/toggle", headers=headers_u1)
    assert res_toggle_u1.status_code == 200
    assert res_toggle_u1.json()["item"]["is_completed"] == 1
    print(f"  [PASSED] User 1 successfully toggled recommendation completed state.")

    # 7. User 1 deletes recommendation -> succeeds
    res_del = client.delete(f"/analysis/recommendations/{rec_id}", headers=headers_u1)
    assert res_del.status_code == 200
    print(f"  [PASSED] User 1 successfully deleted recommendation.")

    # 8. Re-fetch: should no longer exist
    res_get1_after = client.get("/analysis/recommendations", headers=headers_u1)
    assert not any(r["id"] == rec_id for r in res_get1_after.json()["items"])
    print(f"  [PASSED] Deleted recommendation is confirmed absent.")

    print("=== ALL RECOMMENDATION ISOLATION TESTS PASSED ===")

if __name__ == "__main__":
    run_tests()
