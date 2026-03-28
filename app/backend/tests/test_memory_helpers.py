import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.memory_helpers import (
    build_memory_candidate,
    is_duplicate_memory,
    rank_memories_by_query,
)


class MemoryHelperTests(unittest.TestCase):
    def test_build_memory_candidate_extracts_important_event(self) -> None:
        candidate = build_memory_candidate(
            "我妈妈上周住院了，因为心脏问题，我这几天一直很担心。",
            {"domain": "family", "emotions": ["担忧"]},
        )

        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["topic"], "family")
        self.assertIn("担忧", candidate["emotions"])

    def test_build_memory_candidate_ignores_low_information_message(self) -> None:
        candidate = build_memory_candidate("嗯，好的。", {"domain": "workplace"})
        self.assertIsNone(candidate)

    def test_rank_memories_by_query_returns_most_similar_first(self) -> None:
        ranked = rank_memories_by_query(
            "妈妈住院",
            [
                {"content": "妈妈上周住院了，我很担心。", "topic": "family_health", "emotions": ["担忧"]},
                {"content": "最近和领导磨合得不太顺。", "topic": "workplace", "emotions": ["压力"]},
            ],
        )

        self.assertEqual(ranked[0]["topic"], "family_health")

    def test_is_duplicate_memory_rejects_near_identical_content(self) -> None:
        duplicate = is_duplicate_memory(
            {"content": "妈妈上周住院了，我很担心。"},
            [{"content": "妈妈上周住院了，我真的很担心。"}],
        )
        self.assertTrue(duplicate)


if __name__ == "__main__":
    unittest.main()
