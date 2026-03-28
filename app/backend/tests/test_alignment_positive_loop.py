import json
import pathlib
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.tools import record_outcome
from app.models.tables import UserProfile


class AlignmentPositiveLoopTests(unittest.TestCase):
    def test_completed_outcome_increases_alignment_score(self) -> None:
        profile = UserProfile(
            user_id="user-1",
            alliance={"alignment_score": 8, "misalignment_history": []},
            preferences={},
        )
        db = AsyncMock()
        db.execute = AsyncMock(return_value=type("R", (), {"scalar_one_or_none": lambda self: profile})())
        db.add = MagicMock()

        raw = __import__("asyncio").run(record_outcome.execute(
            "session-1",
            "user-1",
            {"skill_name": "breathing_478", "completed": True, "user_feedback": "helpful"},
            db,
        ))
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(profile.alliance["alignment_score"], 13)

    def test_completed_outcome_without_feedback_still_increases_alignment_score(self) -> None:
        profile = UserProfile(
            user_id="user-1",
            alliance={"alignment_score": 10, "misalignment_history": []},
            preferences={},
        )
        db = AsyncMock()
        db.execute = AsyncMock(return_value=type("R", (), {"scalar_one_or_none": lambda self: profile})())
        db.add = MagicMock()

        raw = __import__("asyncio").run(record_outcome.execute(
            "session-1",
            "user-1",
            {"skill_name": "breathing_478", "completed": True},
            db,
        ))
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(profile.alliance["alignment_score"], 15)


if __name__ == "__main__":
    unittest.main()
