"""用户侧情绪趋势数据构建。"""

from __future__ import annotations


def build_mood_trend_payload(sessions: list) -> dict:
    """从会话列表构建前端趋势视图需要的数据。"""
    points = [
        {
            "session_id": session.session_id,
            "date": session.started_at.date().isoformat() if session.started_at else None,
            "score": session.opening_mood_score,
        }
        for session in sessions
        if session.opening_mood_score is not None
    ]
    scores = [point["score"] for point in points]
    average = round(sum(scores) / len(scores), 1) if scores else None
    latest = points[-1]["score"] if points else None
    trend_direction = "stable"
    volatility = 0.0
    if len(scores) >= 2:
        delta = scores[-1] - scores[0]
        if delta >= 1:
            trend_direction = "up"
        elif delta <= -1:
            trend_direction = "down"
        volatility = round((max(scores) - min(scores)) / 4, 2)
    return {
        "count": len(points),
        "average_mood_score": average,
        "latest_mood_score": latest,
        "trend_direction": trend_direction,
        "volatility": volatility,
        "points": points,
    }
