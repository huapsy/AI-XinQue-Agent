import os
import pathlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app import main
from app.encryption_helpers import encrypt_text


class StructuredOutputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_key = os.environ.get("XINQUE_ENCRYPTION_KEY")
        os.environ["XINQUE_ENCRYPTION_KEY"] = "unit-test-encryption-key"
        self.original_client = main.client

    def tearDown(self) -> None:
        main.client = self.original_client
        if self.original_key is None:
            os.environ.pop("XINQUE_ENCRYPTION_KEY", None)
        else:
            os.environ["XINQUE_ENCRYPTION_KEY"] = self.original_key

    def test_generate_summary_uses_structured_output_schema(self) -> None:
        messages = [
            SimpleNamespace(role="user", content=encrypt_text("我最近一直担心明天的一对一反馈。")),
            SimpleNamespace(role="assistant", content=encrypt_text("听起来你这几天一直在绷着。")),
        ]
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(
            scalars=lambda: SimpleNamespace(all=lambda: messages)
        ))
        main.client = SimpleNamespace(
            responses=SimpleNamespace(create=AsyncMock(return_value=SimpleNamespace(
                output_parsed={
                    "summary": "本次主要讨论了一对一反馈焦虑，并约定继续观察呼吸练习的效果。",
                    "themes": ["一对一反馈", "工作焦虑"],
                    "interventions": ["呼吸练习"],
                    "follow_up": ["下次跟进练习效果"],
                },
                output=[],
            )))
        )

        summary = __import__("asyncio").run(main._generate_summary(db, "session-1"))

        self.assertIn("一对一反馈焦虑", summary)
        create_kwargs = main.client.responses.create.await_args.kwargs
        self.assertEqual(create_kwargs["text"]["format"]["type"], "json_schema")
        self.assertEqual(create_kwargs["text"]["format"]["name"], "session_summary")

    def test_generate_summary_falls_back_when_structured_output_is_invalid(self) -> None:
        messages = [
            SimpleNamespace(role="user", content=encrypt_text("我最近一直担心明天的一对一反馈。")),
            SimpleNamespace(role="assistant", content=encrypt_text("听起来你这几天一直在绷着。")),
        ]
        db = AsyncMock()
        db.execute = AsyncMock(return_value=SimpleNamespace(
            scalars=lambda: SimpleNamespace(all=lambda: messages)
        ))
        main.client = SimpleNamespace(
            responses=SimpleNamespace(create=AsyncMock(return_value=SimpleNamespace(output=[], output_parsed=None)))
        )

        summary = __import__("asyncio").run(main._generate_summary(db, "session-1"))

        self.assertIn("担心明天的一对一反馈", summary)


if __name__ == "__main__":
    unittest.main()
