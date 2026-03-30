import json
import pathlib
import sys
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.modules.setdefault("openai", SimpleNamespace(AsyncAzureOpenAI=object))
sys.modules.setdefault("yaml", SimpleNamespace(safe_load=lambda *_args, **_kwargs: {}))
fernet_stub = SimpleNamespace(Fernet=object, InvalidToken=Exception)
sys.modules.setdefault("cryptography", SimpleNamespace(fernet=fernet_stub))
sys.modules.setdefault("cryptography.fernet", fernet_stub)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent import xinque
from app.models.tables import CaseFormulation, Intervention
from app.tool_runtime import resolve_active_skill_state


class XinqueGuardrailTests(unittest.TestCase):
    def test_match_intervention_is_blocked_in_p1_listener_phase(self) -> None:
        formulation = CaseFormulation(
            session_id="session-1",
            user_id="user-1",
            readiness="sufficient",
            missing=[],
        )
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: formulation))

        raw = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="match_intervention",
                arguments={},
                user_id="user-1",
                session_id="session-1",
                user_message="我最近总在开会前发慌",
                messages=[],
                db=db,
                active_phase="p1_listener",
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["reason"], "phase_tool_not_allowed")
        self.assertEqual(payload["active_phase"], "p1_listener")

    def test_formulate_is_allowed_in_p2_explorer_phase(self) -> None:
        db = AsyncMock()

        result = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="formulate",
                arguments={"primary_issue": "周会前焦虑"},
                user_id="user-1",
                session_id="session-1",
                user_message="每次周会前我都很紧绷",
                messages=[],
                db=db,
                active_phase="p2_explorer",
            )
        )

        self.assertIsNone(result)

    def test_match_intervention_is_blocked_when_formulation_is_missing(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: None))

        raw = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="match_intervention",
                arguments={},
                user_id="user-1",
                session_id="session-1",
                user_message="我最近总在开会前发慌",
                messages=[],
                db=db,
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["tool"], "match_intervention")
        self.assertEqual(payload["reason"], "formulation_not_ready")

    def test_match_intervention_is_blocked_when_formulation_still_exploring(self) -> None:
        formulation = CaseFormulation(
            session_id="session-1",
            user_id="user-1",
            readiness="exploring",
            missing=["情绪状态待探索"],
        )
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: formulation))

        raw = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="match_intervention",
                arguments={},
                user_id="user-1",
                session_id="session-1",
                user_message="我最近总在开会前发慌",
                messages=[],
                db=db,
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["reason"], "formulation_not_ready")
        self.assertIn("情绪状态待探索", payload["missing"])

    def test_match_intervention_is_allowed_when_formulation_is_sufficient(self) -> None:
        formulation = CaseFormulation(
            session_id="session-1",
            user_id="user-1",
            readiness="sufficient",
            missing=[],
        )
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: formulation))

        result = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="match_intervention",
                arguments={},
                user_id="user-1",
                session_id="session-1",
                user_message="我最近总在开会前发慌",
                messages=[],
                db=db,
            )
        )

        self.assertIsNone(result)

    def test_save_session_is_blocked_without_end_signal(self) -> None:
        db = AsyncMock()

        raw = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="save_session",
                arguments={},
                user_id="user-1",
                session_id="session-1",
                user_message="我还有点想继续聊工作上的事",
                messages=[],
                db=db,
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["tool"], "save_session")
        self.assertEqual(payload["reason"], "missing_end_signal")

    def test_referral_requires_explicit_urgency(self) -> None:
        db = AsyncMock()

        raw = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="referral",
                arguments={"reason": "需要专业支持"},
                user_id="user-1",
                session_id="session-1",
                user_message="我想找真人咨询师",
                messages=[],
                db=db,
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["tool"], "referral")
        self.assertEqual(payload["reason"], "missing_urgency")

    def test_load_skill_requires_user_acceptance_signal(self) -> None:
        db = AsyncMock()

        raw = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="load_skill",
                arguments={"skill_name": "breathing_478"},
                user_id="user-1",
                session_id="session-1",
                user_message="还有别的方法吗",
                messages=[],
                db=db,
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["tool"], "load_skill")
        self.assertEqual(payload["reason"], "missing_acceptance_signal")

    def test_record_outcome_requires_meaningful_outcome_payload(self) -> None:
        db = AsyncMock()

        raw = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="record_outcome",
                arguments={"skill_name": "breathing_478", "completed": False},
                user_id="user-1",
                session_id="session-1",
                user_message="嗯",
                messages=[],
                db=db,
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["tool"], "record_outcome")
        self.assertEqual(payload["reason"], "insufficient_outcome_payload")

    def test_record_outcome_allows_completed_intervention(self) -> None:
        db = AsyncMock()

        result = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="record_outcome",
                arguments={"skill_name": "breathing_478", "completed": True},
                user_id="user-1",
                session_id="session-1",
                user_message="我刚做完，感觉缓下来一点",
                messages=[],
                db=db,
                active_phase="p4_interventor",
            )
        )

        self.assertIsNone(result)

    def test_load_skill_is_allowed_when_match_result_exists_in_current_turn(self) -> None:
        db = AsyncMock()
        tool_state = [
            {
                "tool": "match_intervention",
                "payload": {"plans": [{"skill_name": "breathing_478"}]},
            }
        ]

        result = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="load_skill",
                arguments={"skill_name": "breathing_478"},
                user_id="user-1",
                session_id="session-1",
                user_message="那你继续吧",
                messages=[],
                tool_state=tool_state,
                db=db,
            )
        )

        self.assertIsNone(result)

    def test_record_outcome_is_allowed_when_skill_loaded_in_current_turn(self) -> None:
        db = AsyncMock()
        tool_state = [
            {
                "tool": "load_skill",
                "payload": {"skill_name": "breathing_478"},
            }
        ]

        result = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="record_outcome",
                arguments={"skill_name": "breathing_478", "user_feedback": "helpful"},
                user_id="user-1",
                session_id="session-1",
                user_message="嗯",
                messages=[],
                tool_state=tool_state,
                db=db,
            )
        )

        self.assertIsNone(result)

    def test_match_intervention_is_blocked_when_recent_intervention_needs_follow_up(self) -> None:
        formulation = CaseFormulation(
            session_id="session-1",
            user_id="user-1",
            readiness="sufficient",
            missing=[],
        )
        recent_intervention = Intervention(
            session_id="session-0",
            user_id="user-1",
            skill_name="breathing_478",
            started_at=datetime.now(timezone.utc) - timedelta(hours=20),
            completed=False,
            user_feedback=None,
            key_insight=None,
            homework_completed=False,
        )
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: formulation),
            SimpleNamespace(scalar_one_or_none=lambda: recent_intervention),
        ])

        raw = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="match_intervention",
                arguments={},
                user_id="user-1",
                session_id="session-1",
                user_message="我今天还是有点烦",
                messages=[],
                db=db,
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["tool"], "match_intervention")
        self.assertEqual(payload["reason"], "recent_intervention_needs_follow_up")
        self.assertEqual(payload["recent_skill_name"], "breathing_478")

    def test_match_intervention_is_allowed_when_user_explicitly_requests_new_method(self) -> None:
        formulation = CaseFormulation(
            session_id="session-1",
            user_id="user-1",
            readiness="sufficient",
            missing=[],
        )
        recent_intervention = Intervention(
            session_id="session-0",
            user_id="user-1",
            skill_name="breathing_478",
            started_at=datetime.now(timezone.utc) - timedelta(hours=20),
            completed=False,
            user_feedback=None,
            key_insight=None,
            homework_completed=False,
        )
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: formulation),
            SimpleNamespace(scalar_one_or_none=lambda: recent_intervention),
        ])

        result = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="match_intervention",
                arguments={},
                user_id="user-1",
                session_id="session-1",
                user_message="那个方法不太适合我，还有别的方法吗",
                messages=[],
                db=db,
            )
        )

        self.assertIsNone(result)

    def test_load_skill_is_blocked_when_recent_same_skill_needs_follow_up(self) -> None:
        recent_intervention = Intervention(
            session_id="session-0",
            user_id="user-1",
            skill_name="breathing_478",
            started_at=datetime.now(timezone.utc) - timedelta(hours=12),
            completed=False,
            user_feedback=None,
            key_insight=None,
            homework_completed=False,
        )
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: recent_intervention))

        raw = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="load_skill",
                arguments={"skill_name": "breathing_478"},
                user_id="user-1",
                session_id="session-1",
                user_message="开始吧",
                messages=[],
                db=db,
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["tool"], "load_skill")
        self.assertEqual(payload["reason"], "recent_intervention_needs_follow_up")

    def test_load_skill_is_allowed_when_user_explicitly_requests_retry(self) -> None:
        recent_intervention = Intervention(
            session_id="session-0",
            user_id="user-1",
            skill_name="breathing_478",
            started_at=datetime.now(timezone.utc) - timedelta(hours=12),
            completed=False,
            user_feedback=None,
            key_insight=None,
            homework_completed=False,
        )
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: recent_intervention))

        result = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="load_skill",
                arguments={"skill_name": "breathing_478"},
                user_id="user-1",
                session_id="session-1",
                user_message="再带我做一次那个呼吸练习吧",
                messages=[],
                db=db,
            )
        )

        self.assertIsNone(result)

    def test_load_skill_allows_positive_experience_consolidation_on_positive_sentiment_start(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: None))

        result = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="load_skill",
                arguments={"skill_name": "positive_experience_consolidation"},
                user_id="user-1",
                session_id="session-1",
                user_message="我今天真的很开心，感觉自己做成了一件大事",
                messages=[],
                db=db,
            )
        )

        self.assertIsNone(result)

    def test_load_skill_blocks_positive_experience_consolidation_when_negative_emotion_is_dominant(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: None))

        raw = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="load_skill",
                arguments={"skill_name": "positive_experience_consolidation"},
                user_id="user-1",
                session_id="session-1",
                user_message="我其实还是很焦虑，只是刚刚有一瞬间有点开心",
                messages=[],
                db=db,
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["tool"], "load_skill")
        self.assertEqual(payload["reason"], "positive_sentiment_not_clear")

    def test_match_intervention_is_blocked_when_active_skill_is_still_in_progress(self) -> None:
        formulation = CaseFormulation(
            session_id="session-1",
            user_id="user-1",
            readiness="sufficient",
            missing=[],
        )
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: formulation))

        raw = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="match_intervention",
                arguments={},
                user_id="user-1",
                session_id="session-1",
                user_message="嗯，我继续说",
                messages=[],
                db=db,
                active_skill={"skill_name": "positive_experience_consolidation"},
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["reason"], "active_skill_in_progress")

    def test_load_skill_is_blocked_when_another_active_skill_is_still_in_progress(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: None))

        raw = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="load_skill",
                arguments={"skill_name": "breathing_478"},
                user_id="user-1",
                session_id="session-1",
                user_message="开始吧",
                messages=[],
                db=db,
                active_skill={"skill_name": "positive_experience_consolidation"},
            )
        )
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["reason"], "active_skill_in_progress")

    def test_match_intervention_is_allowed_when_user_explicitly_wants_to_switch_method_during_active_skill(self) -> None:
        formulation = CaseFormulation(
            session_id="session-1",
            user_id="user-1",
            readiness="sufficient",
            missing=[],
        )
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: formulation))

        result = __import__("asyncio").run(
            xinque._preflight_tool_call(
                tool_name="match_intervention",
                arguments={},
                user_id="user-1",
                session_id="session-1",
                user_message="这个方法不太适合我，换一个吧",
                messages=[],
                db=db,
                active_skill={"skill_name": "positive_experience_consolidation"},
            )
        )

        self.assertIsNone(result)

    def test_resolve_active_skill_state_clears_skill_after_record_outcome(self) -> None:
        active_skill = {"skill_name": "positive_experience_consolidation"}
        tool_state = [
            {
                "tool": "record_outcome",
                "status": "ok",
                "arguments": {"skill_name": "positive_experience_consolidation", "completed": True},
                "payload": {"intervention_id": "iv-1"},
            }
        ]

        resolved = resolve_active_skill_state(active_skill, tool_state, user_message="我做完了")

        self.assertEqual(resolved, {})


if __name__ == "__main__":
    unittest.main()
