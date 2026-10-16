# backend/tests/test_recommendations.py
"""
Unit Tests for Recommendation Persistence:
1. Save recommendation to database
2. Retrieve recommendations with authenticated user isolation
3. Toggle completion state
4. Delete recommendation
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from database.connection import init_db
from database.models import (
    save_recommendation,
    get_saved_recommendations,
    delete_saved_recommendation,
    toggle_recommendation_status
)

def test_recommendation_crud():
    print("Testing recommendation persistence and CRUD...")
    init_db()

    user_a = 101
    user_b = 102

    # 1. Save recommendations for user A
    rec_id1 = save_recommendation(
        user_id=user_a,
        category="Mindfulness",
        title="Mindful Breathing",
        description="Take 5 deep breaths focusing on exhaling slowly.",
        analysis_id=None
    )
    assert rec_id1 > 0

    rec_id2 = save_recommendation(
        user_id=user_a,
        category="Restoration",
        title="Short Screen Break",
        description="Step away from computer for 10 minutes.",
        analysis_id=None
    )
    assert rec_id2 > 0

    # 2. Get recommendations for user A
    recs_a = get_saved_recommendations(user_a)
    assert len(recs_a) >= 2
    assert any(r["title"] == "Mindful Breathing" for r in recs_a)
    assert any(r["title"] == "Short Screen Break" for r in recs_a)

    # 3. User isolation: User B should have 0 recommendations
    recs_b = get_saved_recommendations(user_b)
    assert len(recs_b) == 0

    # User B cannot delete User A's recommendation
    del_unauth = delete_saved_recommendation(user_id=user_b, rec_id=rec_id1)
    assert del_unauth is False

    # 4. Toggle completion
    toggled = toggle_recommendation_status(user_id=user_a, rec_id=rec_id1, is_completed=True)
    assert toggled is not None
    assert toggled["is_completed"] == 1

    # Toggle back
    toggled_back = toggle_recommendation_status(user_id=user_a, rec_id=rec_id1)
    assert toggled_back is not None
    assert toggled_back["is_completed"] == 0

    # 5. Delete recommendation
    del_ok = delete_saved_recommendation(user_id=user_a, rec_id=rec_id1)
    assert del_ok is True
    recs_a_after = get_saved_recommendations(user_a)
    assert not any(r["id"] == rec_id1 for r in recs_a_after)
    print("  [OK] Recommendation CRUD and user isolation verified.")

def run_all():
    print("=== Running Recommendation Persistence Test Suite ===")
    test_recommendation_crud()
    print("=== ALL RECOMMENDATION TESTS PASSED ===")

if __name__ == "__main__":
    run_all()
