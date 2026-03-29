import json
import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.tools import formulate, recall_context, record_outcome
from app.models.tables import CaseFormulation, Intervention, Session, User, UserProfile


class ProfileFlowTests(unittest.TestCase):
    def test_formulate_outcome_and_recall_context_work_together(self) -> None:
        user = User(user_id="user-1", client_id="client-1")
        profile = UserProfile(
            user_id="user-1",
            nickname="阿明",
            session_count=2,
            alliance={"alignment_score": 10, "misalignment_history": []},
            preferences={"preferred_techniques": ["cbt"]},
        )
        user.profile = profile
        session = Session(session_id="session-1", user_id="user-1", summary="上次主要聊工作压力。")

        state: dict[str, object | None] = {"formulation": None, "intervention": None}

        def add(obj: object) -> None:
            if isinstance(obj, CaseFormulation):
                state["formulation"] = obj
            if isinstance(obj, Intervention):
                state["intervention"] = obj

        db = AsyncMock()
        db.add = MagicMock(side_effect=add)
        db.flush = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: None),
            SimpleNamespace(scalar_one_or_none=lambda: profile),
            SimpleNamespace(scalar_one_or_none=lambda: profile),
            SimpleNamespace(scalar_one_or_none=lambda: user),
            SimpleNamespace(scalar_one_or_none=lambda: session),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [state["intervention"]])),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [state["intervention"]])),
        ])

        formulate_raw = __import__("asyncio").run(formulate.execute(
            "session-1",
            "user-1",
            {
                "primary_issue": "工作压力下的自我怀疑",
                "context": {"domain": "workplace"},
                "emotions": [{"name": "焦虑"}],
                "cognitions": [{"content": "我会做不好", "type": "catastrophizing"}],
                "behaviors": {"maladaptive": ["回避反馈"]},
            },
            db,
        ))
        formulate_payload = json.loads(formulate_raw)

        outcome_raw = __import__("asyncio").run(record_outcome.execute(
            "session-1",
            "user-1",
            {
                "skill_name": "breathing_478",
                "completed": True,
                "user_feedback": "helpful",
                "homework_description": "每天练习一次",
                "homework_frequency": "每天",
            },
            db,
        ))
        outcome_payload = json.loads(outcome_raw)

        recall_raw = __import__("asyncio").run(recall_context.execute("user-1", db))
        recall_payload = json.loads(recall_raw)

        self.assertEqual(formulate_payload["status"], "ok")
        self.assertEqual(formulate_payload["schema"], "formulation_v1")
        self.assertEqual(formulate_payload["formulation"]["primary_issue"], "工作压力下的自我怀疑")
        self.assertEqual(profile.clinical_profile["key_themes"], ["workplace"])
        self.assertIn("breathing_478", profile.preferences["preferred_techniques"])
        self.assertEqual(outcome_payload["status"], "ok")
        self.assertEqual(recall_payload["profile_snapshot"]["nickname"], "阿明")
        self.assertEqual(recall_payload["last_session_summary"], "上次主要聊工作压力。")
        self.assertEqual(recall_payload["recent_interventions"][0]["skill_name"], "breathing_478")


if __name__ == "__main__":
    unittest.main()
