import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.combined_evaluation_store import (
    list_combined_evaluations,
    load_combined_evaluation,
    save_combined_evaluation,
)
from app.models.tables import CombinedEvaluation


class CombinedEvaluationStoreTests(unittest.TestCase):
    def test_load_combined_evaluation_returns_payload(self) -> None:
        record = CombinedEvaluation(
            session_id="session-1",
            payload={"summary": "整体稳定。", "risk_flags": ["unfinished_p4"]},
        )
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: record))

        payload = __import__("asyncio").run(load_combined_evaluation(db, "session-1"))

        self.assertEqual(payload["summary"], "整体稳定。")
        self.assertEqual(payload["risk_flags"], ["unfinished_p4"])

    def test_save_combined_evaluation_updates_existing_record(self) -> None:
        existing = CombinedEvaluation(
            session_id="session-1",
            payload={"summary": "旧结果"},
        )
        db = AsyncMock()
        db.add = MagicMock()
        db.flush = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: existing))

        saved = __import__("asyncio").run(save_combined_evaluation(
            db,
            "session-1",
            {"summary": "新结果", "risk_flags": ["phase_regression"]},
        ))

        self.assertIs(saved, existing)
        self.assertEqual(existing.payload["summary"], "新结果")
        self.assertEqual(existing.payload["risk_flags"], ["phase_regression"])
        db.add.assert_not_called()

    def test_list_combined_evaluations_returns_payloads(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [
            CombinedEvaluation(
                session_id="session-1",
                payload={"summary": "整体稳定。", "risk_flags": ["unfinished_p4"]},
            ),
            CombinedEvaluation(
                session_id="session-2",
                payload={"summary": "存在阶段回退。", "risk_flags": ["phase_regression"]},
            ),
        ])))

        payloads = __import__("asyncio").run(list_combined_evaluations(db))

        self.assertEqual(len(payloads), 2)
        self.assertEqual(payloads[0]["session_id"], "session-1")
        self.assertEqual(payloads[1]["risk_flags"], ["phase_regression"])
