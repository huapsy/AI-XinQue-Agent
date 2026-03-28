import json
import pathlib
import sys
import unittest
from unittest.mock import AsyncMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.tools import update_profile
from app.models.tables import UserProfile


class UpdateProfileToolTests(unittest.TestCase):
    def test_update_profile_persists_explicit_preferences_only(self) -> None:
        profile = UserProfile(user_id="user-1", preferences={"preferred_techniques": ["mindfulness"]})
        db = AsyncMock()
        db.execute = AsyncMock(return_value=type("R", (), {"scalar_one_or_none": lambda self: profile})())

        raw = __import__("asyncio").run(update_profile.execute(
            "user-1",
            {
                "preferences": {
                    "communication_style": "direct",
                    "disliked_techniques": ["breathing_478"],
                }
            },
            db,
        ))
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(profile.preferences["communication_style"], "direct")
        self.assertEqual(profile.preferences["disliked_techniques"], ["breathing_478"])
        self.assertEqual(profile.preferences["preferred_techniques"], ["mindfulness"])

    def test_update_profile_rejects_unsupported_fields(self) -> None:
        profile = UserProfile(user_id="user-1", preferences={"preferred_techniques": ["mindfulness"]})
        db = AsyncMock()
        db.execute = AsyncMock(return_value=type("R", (), {"scalar_one_or_none": lambda self: profile})())

        raw = __import__("asyncio").run(update_profile.execute(
            "user-1",
            {"preferences": {"risk_level": "crisis"}},
            db,
        ))
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "error")
        self.assertIn("unsupported", payload["message"])


if __name__ == "__main__":
    unittest.main()
