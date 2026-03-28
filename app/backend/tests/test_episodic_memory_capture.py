import os
import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.encryption_helpers import decrypt_text, is_encrypted
from app.memory_helpers import maybe_store_episodic_memory
from app.models.tables import EpisodicMemory


class EpisodicMemoryCaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_key = os.environ.get("XINQUE_ENCRYPTION_KEY")
        os.environ["XINQUE_ENCRYPTION_KEY"] = "unit-test-encryption-key"

    def tearDown(self) -> None:
        if self.original_key is None:
            os.environ.pop("XINQUE_ENCRYPTION_KEY", None)
        else:
            os.environ["XINQUE_ENCRYPTION_KEY"] = self.original_key

    def test_store_memory_for_important_event(self) -> None:
        captured: list[EpisodicMemory] = []
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [])))
        db.add = MagicMock(side_effect=lambda obj: captured.append(obj))

        __import__("asyncio").run(maybe_store_episodic_memory(
            db,
            EpisodicMemory,
            "user-1",
            "session-1",
            "我妈妈上周住院了，因为心脏问题，我很担心。",
        ))

        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0].topic, "family_health")
        self.assertTrue(is_encrypted(captured[0].content))
        self.assertIn("妈妈上周住院了", decrypt_text(captured[0].content))

    def test_skip_duplicate_memory_for_same_user(self) -> None:
        captured: list[EpisodicMemory] = []
        existing = [SimpleNamespace(content="我妈妈上周住院了，我真的很担心。")]
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: existing)))
        db.add = MagicMock(side_effect=lambda obj: captured.append(obj))

        __import__("asyncio").run(maybe_store_episodic_memory(
            db,
            EpisodicMemory,
            "user-1",
            "session-1",
            "我妈妈上周住院了，因为心脏问题，我很担心。",
        ))

        self.assertEqual(captured, [])


if __name__ == "__main__":
    unittest.main()
