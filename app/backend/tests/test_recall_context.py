import json
import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.tools import recall_context
from app.models.tables import Intervention, Session, User, UserProfile


class RecallContextTests(unittest.TestCase):
    def test_recall_context_returns_stable_sections(self) -> None:
        user = User(user_id="user-1", client_id="client-1", nickname="旧昵称")
        profile = UserProfile(
            user_id="user-1",
            nickname="阿明",
            session_count=3,
            risk_level="low",
            alliance={"alignment_score": 11, "misalignment_history": []},
            preferences={"communication_style": "direct"},
        )
        profile.clinical_profile = {"key_themes": ["workplace_pressure"]}
        user.profile = profile

        session = Session(
            session_id="session-1",
            user_id="user-1",
            summary="上次聊了工作压力和回避反馈。",
        )
        intervention = Intervention(
            session_id="session-1",
            user_id="user-1",
            skill_name="breathing_478",
            completed=True,
            user_feedback="helpful",
            key_insight="先让身体慢下来",
            homework_assigned={"description": "每天练习一次", "frequency": "每天"},
            homework_completed=False,
        )

        db = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: user),
            SimpleNamespace(scalar_one_or_none=lambda: session),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [intervention])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [intervention])),
        ])

        raw = __import__("asyncio").run(recall_context.execute("user-1", db))
        payload = json.loads(raw)

        self.assertIn("profile_snapshot", payload)
        self.assertIn("last_session_summary", payload)
        self.assertIn("pending_homework", payload)
        self.assertIn("recent_interventions", payload)
        self.assertEqual(payload["profile_snapshot"]["nickname"], "阿明")
        self.assertEqual(payload["profile_snapshot"]["preferences"]["communication_style"], "direct")
        self.assertEqual(payload["last_session_summary"], "上次聊了工作压力和回避反馈。")
        self.assertEqual(payload["pending_homework"][0]["skill_name"], "breathing_478")


if __name__ == "__main__":
    unittest.main()
