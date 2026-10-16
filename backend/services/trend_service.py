# backend/services/trend_service.py
"""
Multi-Entry Longitudinal Trend Engine

Calculates trajectory across historical wellness indicator observations.
Strict Rule: Requires at least 3 entries to establish a meaningful trend.
For fewer than 3 entries, it explicitly reports 'Insufficient Data' rather than
generating a premature trajectory from isolated points.
"""

from typing import List, Dict, Any

MINIMUM_ENTRIES_FOR_TREND = 3

def calculate_longitudinal_trend(
    current_score: int,
    history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates multi-entry trajectory.
    Returns:
    - direction: 'Improving' | 'Stable' | 'Needs Attention' | 'Insufficient Data'
    - based_on_entries: int
    - points: list of recent scores
    - message: explanatory string
    """
    if not history or len(history) < (MINIMUM_ENTRIES_FOR_TREND - 1):
        # We need at least 2 historical + current = 3 total points
        total_available = 1 + (len(history) if history else 0)
        return {
            "direction": "Insufficient Data",
            "based_on_entries": total_available,
            "points": [current_score],
            "message": "Not enough historical data to determine a meaningful trend yet."
        }

    # Gather recent scores up to 6 entries (chronological order)
    recent_history = history[:5]
    recent_history.reverse()
    points = [h.get("wellness_score", 65) for h in recent_history] + [current_score]
    n = len(points)

    # Statistical trajectory indicators
    min_val = min(points)
    max_val = max(points)
    total_range = max_val - min_val
    net_change = points[-1] - points[0]
    recent_delta = points[-1] - points[-2]

    # Successive steps and directional reversals
    diffs = [points[i + 1] - points[i] for i in range(n - 1)]
    total_volatility = sum(abs(d) for d in diffs) / (n - 1)
    direction_flips = sum(1 for i in range(len(diffs) - 1) if (diffs[i] * diffs[i + 1]) < 0)

    # Linear regression slope across points
    mean_x = (n - 1) / 2.0
    mean_y = sum(points) / float(n)
    denom = sum((i - mean_x) ** 2 for i in range(n))
    slope = sum((i - mean_x) * (p - mean_y) for i, p in enumerate(points)) / denom if denom > 0 else 0.0

    # Volatility detection: sharp swings or meaningful reversals (requires notable range)
    is_volatile = total_range >= 18 and (total_volatility >= 8.0 or direction_flips >= 1)

    if is_volatile:
        # Check if the recent momentum is recovering upward
        has_rebound = recent_delta >= 8 or (n >= 4 and points[-1] >= points[-2] >= points[-3] and (points[-1] - points[-3]) >= 10)
        # Check if recently stabilizing
        is_stabilizing = abs(recent_delta) <= 4

        if has_rebound:
            direction = "Improving"
            message = "Your wellness pattern shows emotional variation with a recent upward rebound across your latest reflections."
        elif is_stabilizing:
            direction = "Fluctuating"
            message = "Your reflections show variable wellness scores that are beginning to stabilize around current levels."
        elif recent_delta <= -8:
            direction = "Needs Attention"
            message = "Your reflections show emotional volatility with a recent downward shift, suggesting emerging strain."
        else:
            direction = "Fluctuating"
            message = "Your recent reflections show notable day-to-day fluctuation across emotional and wellness indicators."
    else:
        # Non-volatile, sustained progression or steady equilibrium
        if slope >= 2.0 or net_change >= 8:
            direction = "Improving"
            message = "Your wellness indicator shows an upward, restorative trajectory over recent reflections."
        elif slope <= -2.0 or net_change <= -8:
            direction = "Needs Attention"
            message = "Your recent reflections show a downward drift in wellness indicators, suggesting increased cumulative strain."
        else:
            direction = "Stable"
            message = "Your wellness pattern has remained steady and consistent over your recent reflections."

    return {
        "direction": direction,
        "based_on_entries": len(points),
        "points": points,
        "message": message
    }
