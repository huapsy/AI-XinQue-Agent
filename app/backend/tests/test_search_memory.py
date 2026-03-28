import json
import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.tools import search_memory


class SearchMemoryToolTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
