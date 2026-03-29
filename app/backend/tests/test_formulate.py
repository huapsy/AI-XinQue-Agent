import json
import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.tools import formulate
from app.models.tables import CaseFormulation, UserProfile


class FormulateToolTests(unittest.TestCase):
    def test_formulate_returns_structured_envelope(self) -> None:
        state: dict[str, object | None] = {"formulation": None}

        def add(obj: object) -> None:
            if isinstance(obj, CaseFormulation):
                state["formulation"] = obj

        profile = UserProfile(user_id="user-1")
        db = AsyncMock()
        db.add = MagicMock(side_effect=add)
        db.flush = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: None),
            SimpleNamespace(scalar_one_or_none=lambda: profile),
        ])

        raw = __import__("asyncio").run(
            formulate.execute(
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
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["schema"], "formulation_v1")
        self.assertEqual(payload["formulation"]["primary_issue"], "工作压力下的自我怀疑")
        self.assertIn("readiness", payload["formulation"])
        self.assertIn("missing", payload["formulation"])
        self.assertIsInstance(payload["formulation"]["context"], dict)

    def test_formulate_normalizes_missing_optional_sections(self) -> None:
        existing = CaseFormulation(session_id="session-1", user_id="user-1")
        profile = UserProfile(user_id="user-1")
        db = AsyncMock()
        db.flush = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: existing),
            SimpleNamespace(scalar_one_or_none=lambda: profile),
        ])

        raw = __import__("asyncio").run(
            formulate.execute(
                "session-1",
                "user-1",
                {"primary_issue": "我最近状态不好"},
                db,
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["formulation"]["primary_issue"], "我最近状态不好")
        self.assertEqual(payload["formulation"]["emotions"], [])
        self.assertEqual(payload["formulation"]["cognitive_patterns"], [])
        self.assertEqual(payload["formulation"]["behavioral_patterns"], {"maladaptive": [], "adaptive": []})
        self.assertEqual(payload["formulation"]["context"], {})
        self.assertIsInstance(payload["formulation"]["missing"], list)


if __name__ == "__main__":
    unittest.main()
