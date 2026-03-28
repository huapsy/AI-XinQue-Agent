import pathlib
import sys
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.mood_trend_helpers import build_mood_trend_payload


class MoodTrendHelperTests(unittest.TestCase):
    def test_build_mood_trend_payload_returns_average_and_points(self) -> None:
        sessions = [
            SimpleNamespace(
                session_id="s1",
                started_at=datetime(2026, 3, 20, tzinfo=timezone.utc),
                opening_mood_score=2,
            ),
            SimpleNamespace(
                session_id="s2",
                started_at=datetime(2026, 3, 24, tzinfo=timezone.utc),
                opening_mood_score=4,
            ),
            SimpleNamespace(
                session_id="s3",
                started_at=datetime(2026, 3, 27, tzinfo=timezone.utc),
                opening_mood_score=None,
            ),
        ]

        payload = build_mood_trend_payload(sessions)

        self.assertEqual(payload["count"], 2)
        self.assertEqual(payload["average_mood_score"], 3.0)
        self.assertEqual(payload["trend_direction"], "up")
        self.assertEqual(payload["points"][0]["session_id"], "s1")
        self.assertEqual(payload["points"][1]["score"], 4)


if __name__ == "__main__":
    unittest.main()
