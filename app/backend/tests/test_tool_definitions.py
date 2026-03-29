import pathlib
import sys
import unittest
from types import SimpleNamespace

sys.modules.setdefault("openai", SimpleNamespace(AsyncAzureOpenAI=object))
sys.modules.setdefault("yaml", SimpleNamespace(safe_load=lambda *_args, **_kwargs: {}))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.agent.xinque import TOOL_DEFINITIONS


class ToolDefinitionTests(unittest.TestCase):
    def test_all_tool_definitions_are_responses_native(self) -> None:
        for tool in TOOL_DEFINITIONS:
            self.assertEqual(tool["type"], "function")
            self.assertIn("name", tool)
            self.assertIn("parameters", tool)
            self.assertNotIn("function", tool)
            self._assert_array_items_declared(tool["parameters"])

    def _assert_array_items_declared(self, schema: object) -> None:
        if not isinstance(schema, dict):
            return
        if schema.get("type") == "array":
            self.assertIn("items", schema, f"array schema missing items: {schema}")
        for key in ("properties",):
            nested = schema.get(key)
            if isinstance(nested, dict):
                for child in nested.values():
                    self._assert_array_items_declared(child)
        for key in ("items",):
            self._assert_array_items_declared(schema.get(key))
        for key in ("anyOf", "oneOf", "allOf"):
            nested = schema.get(key)
            if isinstance(nested, list):
                for child in nested:
                    self._assert_array_items_declared(child)


if __name__ == "__main__":
    unittest.main()
