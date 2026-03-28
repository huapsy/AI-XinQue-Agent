import json
import pathlib
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.tools import record_outcome
from app.models.tables import UserProfile


class RecordOutcomeProfileTests(unittest.TestCase):
    def test_helpful_outcome_updates_preferred_techniques(self) -> None:
        profile = UserProfile(user_id="user-1", preferences={"preferred_techniques": ["cbt"]})
        db = AsyncMock()
        db.execute = AsyncMock(return_value=type("R", (), {"scalar_one_or_none": lambda self: profile})())
        db.add = MagicMock()

        raw = __import__("asyncio").run(record_outcome.execute(
            "session-1",
            "user-1",
            {
                "skill_name": "breathing_478",
                "completed": True,
                "user_feedback": "helpful",
            },
            db,
        ))
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "ok")
        self.assertIn("breathing_478", profile.preferences["preferred_techniques"])


if __name__ == "__main__":
    unittest.main()
