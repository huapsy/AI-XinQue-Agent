"""Responses API 协议辅助函数。"""

from __future__ import annotations

import json


def make_response_message(role: str, content: str, phase: str | None = None) -> dict:
    """构造 Responses API 输入消息。"""
    message = {
        "type": "message",
        "role": role,
        "content": content,
    }
    if phase:
        message["phase"] = phase
    return message


def build_response_input(history: list[dict], user_message: str) -> list[dict]:
    """把当前项目的历史消息结构转换为 Responses API 输入。"""
    items: list[dict] = []
    for item in history:
        role = item.get("role")
        content = str(item.get("content", ""))
        if role == "assistant":
            items.append(make_response_message("assistant", content, phase="final_answer"))
        elif role in {"user", "system", "developer"}:
            items.append(make_response_message(role, content))
    items.append(make_response_message("user", user_message))
    return items


def build_function_call_output(call_id: str, output: str) -> dict:
    """构造 function_call_output 输入项。"""
    return {
        "type": "function_call_output",
        "call_id": call_id,
        "output": output,
    }


def build_text_format_json_schema(name: str, schema: dict, strict: bool = True) -> dict:
    """构造 Responses API 的 text.format json_schema 配置。"""
    return {
        "format": {
            "type": "json_schema",
            "name": name,
            "strict": strict,
            "schema": schema,
        }
    }


def resolve_function_call_id(tool_call) -> str | None:
    """兼容不同 SDK 中 function call 标识字段。"""
    return getattr(tool_call, "call_id", None) or getattr(tool_call, "id", None)


def get_response_output_items(response) -> list:
    return list(getattr(response, "output", None) or [])


def extract_response_function_calls(response) -> list:
    """提取 Responses API 输出中的 function_call 项。"""
    return [item for item in get_response_output_items(response) if getattr(item, "type", None) == "function_call"]


def extract_response_message_text(response) -> tuple[str, str | None]:
    """提取最终 assistant 文本及其 phase。"""
    output_items = get_response_output_items(response)
    for item in reversed(output_items):
        if getattr(item, "type", None) != "message":
            continue
        if getattr(item, "role", None) != "assistant":
            continue
        parts = getattr(item, "content", None) or []
        texts = [getattr(part, "text", "") for part in parts if getattr(part, "type", None) == "output_text"]
        return "".join(texts), getattr(item, "phase", None)
    return "", None


def extract_structured_output(response) -> dict | None:
    """优先读取 SDK 已解析的 structured output，必要时回退到文本 JSON。"""
    parsed = getattr(response, "output_parsed", None)
    if isinstance(parsed, dict):
        return parsed

    for item in get_response_output_items(response):
        if getattr(item, "type", None) != "message":
            continue
        if getattr(item, "role", None) != "assistant":
            continue
        for part in getattr(item, "content", None) or []:
            parsed_part = getattr(part, "parsed", None)
            if isinstance(parsed_part, dict):
                return parsed_part

    text, _phase = extract_response_message_text(response)
    if not text:
        return None
    try:
        parsed_text = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed_text if isinstance(parsed_text, dict) else None


def get_usage_counts(response) -> tuple[int, int, int]:
    """兼容不同 SDK usage 字段命名。"""
    usage = getattr(response, "usage", None)
    if usage is None:
        return 0, 0, 0

    prompt_tokens = getattr(usage, "input_tokens", None)
    if prompt_tokens is None:
        prompt_tokens = getattr(usage, "prompt_tokens", 0)

    completion_tokens = getattr(usage, "output_tokens", None)
    if completion_tokens is None:
        completion_tokens = getattr(usage, "completion_tokens", 0)

    total_tokens = getattr(usage, "total_tokens", None)
    if total_tokens is None:
        total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

    return int(prompt_tokens or 0), int(completion_tokens or 0), int(total_tokens or 0)
