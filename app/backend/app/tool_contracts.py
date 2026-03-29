"""Tool 结果契约与 envelope 辅助函数。"""

from __future__ import annotations

import json


def build_tool_success_envelope(tool_name: str, payload: dict | list | str | int | float | bool | None) -> dict:
    """构造统一成功 envelope。"""
    return {
        "status": "ok",
        "tool": tool_name,
        "payload": payload,
    }


def build_tool_error_envelope(tool_name: str, error: str, *, status: str = "error") -> dict:
    """构造统一失败 envelope。"""
    return {
        "status": status,
        "tool": tool_name,
        "error": error,
    }


def normalize_tool_result(tool_name: str, raw_result: str) -> dict:
    """将各类 tool 返回统一收敛为 envelope。"""
    try:
        parsed = json.loads(raw_result)
    except json.JSONDecodeError:
        return build_tool_success_envelope(tool_name, raw_result)

    if not isinstance(parsed, dict):
        return build_tool_success_envelope(tool_name, parsed)

    status = parsed.get("status")
    if status in {"ok", "blocked", "error"}:
        if status == "error":
            return build_tool_error_envelope(tool_name, str(parsed.get("error", "unknown_error")))

        payload = {
            key: value
            for key, value in parsed.items()
            if key not in {"status", "tool"}
        }
        return {
            "status": status,
            "tool": tool_name,
            "payload": payload,
        }

    if "error" in parsed:
        return build_tool_error_envelope(tool_name, str(parsed["error"]))

    return build_tool_success_envelope(tool_name, parsed)


def dump_tool_envelope(envelope: dict) -> str:
    """将 envelope 序列化为 JSON 字符串。"""
    return json.dumps(envelope, ensure_ascii=False)
