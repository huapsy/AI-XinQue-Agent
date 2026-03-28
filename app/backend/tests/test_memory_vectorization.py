import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.memory_helpers import embed_text, rank_memories_by_query


class MemoryVectorizationTests(unittest.TestCase):
    def test_embed_text_returns_fixed_length_vector(self) -> None:
        vector = embed_text("妈妈住院我很担心")
        self.assertEqual(len(vector), 16)

    def test_rank_memories_prefers_semantically_closer_memory(self) -> None:
        ranked = rank_memories_by_query(
            "周会前很紧张",
            [
                {
                    "content": "每次周会前我都会非常紧张，怕领导点名。",
                    "embedding": embed_text("每次周会前我都会非常紧张，怕领导点名。"),
                },
                {
                    "content": "我妈妈上周住院了。",
                    "embedding": embed_text("我妈妈上周住院了。"),
                },
            ],
        )

        self.assertIn("周会前", ranked[0]["content"])


if __name__ == "__main__":
    unittest.main()
