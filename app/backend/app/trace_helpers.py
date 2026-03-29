"""Trace 构建与脱敏辅助函数。"""

from __future__ import annotations

from app.privacy_helpers import redact_sensitive_text


def redact_trace_text(text: str | None, limit: int = 120) -> str:
    """对 trace 中的文本做最小截断，避免长原文直接落库。"""
    return redact_sensitive_text(text, limit=limit)


def build_tool_trace_entry(
    tool_name: str,
    arguments: str,
    result: str,
    success: bool,
    latency_ms: int,
) -> dict:
    """构建单次 tool 调用的 trace 记录。"""
    return {
        "tool": tool_name,
        "arguments": redact_trace_text(arguments),
        "result": redact_trace_text(result),
        "success": success,
        "latency_ms": latency_ms,
    }


def serialize_trace_records(records: list) -> dict:
    """将 Trace ORM 记录转换为 API 可返回结构。"""
    return {
        "traces": [
            {
                "trace_id": record.trace_id,
                "turn_number": record.turn_number,
                "input_safety": record.input_safety,
                "llm_call": record.llm_call,
                "output_safety": record.output_safety,
                "total_latency_ms": record.total_latency_ms,
                "created_at": record.created_at.isoformat() if record.created_at else None,
            }
            for record in records
        ]
    }


def serialize_phase_timeline(records: list) -> dict:
    """将 trace 中的 phase timeline 扁平化为会话级读取结构。"""
    return {
        "timeline": [
            {
                "turn_number": record.turn_number,
                "created_at": record.created_at.isoformat() if getattr(record, "created_at", None) else None,
                "phases": [item.get("phase") for item in ((getattr(record, "llm_call", {}) or {}).get("phase_timeline") or [])],
                "phase_timeline": ((getattr(record, "llm_call", {}) or {}).get("phase_timeline") or []),
            }
            for record in records
        ]
    }


def create_trace_record(
    trace_model,
    session_id: str,
    turn_number: int,
    input_safety: dict,
    llm_call: dict,
    output_safety: dict,
    total_latency_ms: int,
):
    """构建待持久化的 Trace ORM 对象。"""
    return trace_model(
        session_id=session_id,
        turn_number=turn_number,
        input_safety=input_safety,
        llm_call=llm_call,
        output_safety=output_safety,
        total_latency_ms=total_latency_ms,
    )
