import os
import json
import pathlib
import sys
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.tools import save_session
from app.encryption_helpers import decrypt_text, is_encrypted
from app.models.tables import Message, Session


class SaveSessionToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_key = os.environ.get("XINQUE_ENCRYPTION_KEY")
        os.environ["XINQUE_ENCRYPTION_KEY"] = "unit-test-encryption-key"

    def tearDown(self) -> None:
        if self.original_key is None:
            os.environ.pop("XINQUE_ENCRYPTION_KEY", None)
        else:
            os.environ["XINQUE_ENCRYPTION_KEY"] = self.original_key

    def test_save_session_generates_and_persists_summary(self) -> None:
        session = Session(session_id="session-1", user_id="user-1", summary=None, ended_at=None)
        messages = [
            Message(session_id="session-1", role="user", content="我最近开会前很紧张。"),
            Message(session_id="session-1", role="assistant", content="听起来你最近压力很大。"),
            Message(session_id="session-1", role="user", content="是的，我总担心自己会说错。"),
        ]
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=[
            SimpleNamespace(scalar_one_or_none=lambda: session),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: messages)),
        ])
        db.flush = AsyncMock()

        raw = __import__("asyncio").run(save_session.execute("session-1", db))
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["session_id"], "session-1")
        self.assertIsNotNone(session.summary)
        self.assertIsInstance(session.ended_at, datetime)
        self.assertEqual(session.ended_at.tzinfo, timezone.utc)
        self.assertTrue(is_encrypted(session.summary))
        self.assertIn("开会前很紧张", decrypt_text(session.summary))


if __name__ == "__main__":
    unittest.main()
