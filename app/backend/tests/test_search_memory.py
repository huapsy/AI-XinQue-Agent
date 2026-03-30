import json
import pathlib
import sys
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.tools import search_memory


class SearchMemoryToolTests(unittest.TestCase):
    def test_search_memory_uses_retrieval_backend_entrypoint(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(
            scalars=lambda: SimpleNamespace(all=lambda: [
                SimpleNamespace(
                    content="妈妈上周住院了，我很担心。",
                    topic="family_health",
                    emotions=["担忧"],
                    created_at=None,
                    embedding=[],
                ),
            ])
        ))

        with patch("app.agent.tools.search_memory.retrieve_memories", return_value=[{
            "content": "妈妈上周住院了，我很担心。",
            "topic": "family_health",
            "emotions": ["担忧"],
            "created_at": None,
        }]) as retrieve_mock:
            raw = __import__("asyncio").run(search_memory.execute(
                "user-1",
                {"query": "妈妈住院", "top_k": 2},
                db,
            ))

        payload = json.loads(raw)
        self.assertEqual(payload["results"][0]["topic"], "family_health")
        retrieve_mock.assert_called()

    def test_search_memory_returns_ranked_matches(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(
            scalars=lambda: SimpleNamespace(all=lambda: [
                SimpleNamespace(
                    content="妈妈上周住院了，我很担心。",
                    topic="family_health",
                    emotions=["担忧"],
                    created_at=None,
                ),
                SimpleNamespace(
                    content="最近和领导磨合得不太顺。",
                    topic="workplace",
                    emotions=["压力"],
                    created_at=None,
                ),
            ])
        ))

        raw = __import__("asyncio").run(search_memory.execute(
            "user-1",
            {"query": "妈妈住院", "top_k": 2},
            db,
        ))
        payload = json.loads(raw)

        self.assertEqual(payload["results"][0]["topic"], "family_health")
        self.assertEqual(len(payload["results"]), 1)

    def test_search_memory_can_recall_specific_workplace_scene(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(
            scalars=lambda: SimpleNamespace(all=lambda: [
                SimpleNamespace(
                    content="之前每次周会前我都会特别紧张，最怕被领导点名。",
                    topic="workplace",
                    emotions=["紧张"],
                    created_at=None,
                    embedding=["周", "会", "前", "紧", "张", "点", "名"],
                ),
                SimpleNamespace(
                    content="妈妈上周住院了，我很担心。",
                    topic="family_health",
                    emotions=["担忧"],
                    created_at=None,
                    embedding=["妈", "妈", "住", "院"],
                ),
            ])
        ))

        raw = __import__("asyncio").run(search_memory.execute(
            "user-1",
            {"query": "周会紧张", "top_k": 3},
            db,
        ))
        payload = json.loads(raw)

        self.assertEqual(payload["results"][0]["topic"], "workplace")
        self.assertIn("周会前", payload["results"][0]["content"])

    def test_search_memory_retries_without_topic_when_topic_filter_is_too_narrow(self) -> None:
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(
            scalars=lambda: SimpleNamespace(all=lambda: [
                SimpleNamespace(
                    content="之前每次周会前我都会特别紧张，最怕被领导点名。",
                    topic="workplace",
                    emotions=["紧张"],
                    created_at=None,
                    embedding=["周", "会", "前", "紧", "张", "点", "名"],
                ),
            ])
        ))

        raw = __import__("asyncio").run(search_memory.execute(
            "user-1",
            {"query": "周会紧张", "top_k": 3, "topic": "family_health"},
            db,
        ))
        payload = json.loads(raw)

        self.assertEqual(payload["status"], "fallback")
        self.assertEqual(payload["fallback_strategy"], "drop_topic_filter")
        self.assertEqual(payload["results"][0]["topic"], "workplace")

    def test_search_memory_prefers_more_recent_memory_when_relevance_is_close(self) -> None:
        now = datetime.now(timezone.utc)
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(
            scalars=lambda: SimpleNamespace(all=lambda: [
                SimpleNamespace(
                    content="上周和领导谈话时我很紧张，怕自己表达不好。",
                    topic="workplace",
                    emotions=["紧张"],
                    created_at=now - timedelta(days=14),
                    embedding=None,
                ),
                SimpleNamespace(
                    content="昨天和领导一对一时我也很紧张，还是担心自己说错话。",
                    topic="workplace",
                    emotions=["紧张"],
                    created_at=now - timedelta(days=1),
                    embedding=None,
                ),
            ])
        ))

        raw = __import__("asyncio").run(search_memory.execute(
            "user-1",
            {"query": "领导紧张说错话", "top_k": 2},
            db,
        ))
        payload = json.loads(raw)

        self.assertEqual(len(payload["results"]), 2)
        self.assertEqual(payload["results"][0]["created_at"], (now - timedelta(days=1)).isoformat())


if __name__ == "__main__":
    unittest.main()
