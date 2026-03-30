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


def serialize_phase_timeline(
    records: list,
    *,
    limit: int | None = None,
    before_turn: int | None = None,
    phase: str | None = None,
) -> dict:
    """将 trace 中的 phase timeline 扁平化为会话级读取结构。"""
    normalized_limit = max(1, min(int(limit or 20), 100))
    visible_records = []
    for record in records:
        if before_turn is not None and getattr(record, "turn_number", 0) >= before_turn:
            continue
        phase_timeline = ((getattr(record, "llm_call", {}) or {}).get("phase_timeline") or [])
        phases = [item.get("phase") for item in phase_timeline]
        if phase and phase not in phases:
            continue
        visible_records.append({
            "turn_number": record.turn_number,
            "created_at": record.created_at.isoformat() if getattr(record, "created_at", None) else None,
            "phases": phases,
            "phase_timeline": phase_timeline,
        })

    sliced_records = visible_records[: normalized_limit + 1]
    returned_records = sliced_records[:normalized_limit]
    has_more = len(sliced_records) > normalized_limit
    next_before_turn = returned_records[-1]["turn_number"] if has_more and returned_records else None
    return {
        "timeline": returned_records,
        "meta": {
            "limit": normalized_limit,
            "returned": len(returned_records),
            "before_turn": before_turn,
            "phase": phase,
            "has_more": has_more,
            "next_before_turn": next_before_turn,
        },
    }


def build_session_analysis_payload(*, session_id: str, state_history: list, traces: list) -> dict:
    """构建会话级聚合分析载荷。"""
    def _state_value(record, field: str, default=None):
        if isinstance(record, dict):
            return record.get(field, default)
        return getattr(record, field, default)

    latest_state = state_history[0] if state_history else None
    latest_trace = traces[-1] if traces else None
    latest_timeline = ((getattr(latest_trace, "llm_call", {}) or {}).get("phase_timeline") or [])
    latest_phases = [item.get("phase") for item in latest_timeline]
    phase_flow = build_phase_flow_report(traces)

    phase_counts: dict[str, int] = {}
    for trace in traces:
        for item in ((getattr(trace, "llm_call", {}) or {}).get("phase_timeline") or []):
            phase = item.get("phase")
            if not phase:
                continue
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

    key_state_changes = [
        {
            "version": _state_value(record, "version"),
            "change_reason": _state_value(record, "change_reason"),
            "current_focus_summary": (_state_value(record, "current_focus", {}) or {}).get("summary"),
            "created_at": _state_value(record, "created_at"),
        }
        for record in state_history[:5]
    ]

    return {
        "session_id": session_id,
        "analysis": {
            "current_focus_summary": ((_state_value(latest_state, "current_focus", {}) or {}).get("summary")),
            "latest_phases": latest_phases,
            "phase_counts": phase_counts,
            "key_state_changes": key_state_changes,
            "phase_flow": phase_flow,
            "phase_anomalies": phase_flow.get("anomalies", {}),
        },
    }


def build_phase_flow_report(traces: list) -> dict:
    """基于 trace phase_routing 事件构建会话级 phase flow 报告。"""
    phase_sequence: list[str] = []
    phase_counts: dict[str, int] = {}

    for trace in traces:
        phase_timeline = ((getattr(trace, "llm_call", {}) or {}).get("phase_timeline") or [])
        routed_phase = None
        for item in phase_timeline:
            if item.get("phase") == "phase_routing" and item.get("active_phase"):
                routed_phase = item.get("active_phase")
        if not routed_phase:
            continue
        phase_sequence.append(routed_phase)
        phase_counts[routed_phase] = phase_counts.get(routed_phase, 0) + 1

    transition_pairs = [
        f"{prev}->{curr}"
        for prev, curr in zip(phase_sequence, phase_sequence[1:])
    ]

    repeated_phase_runs: list[dict] = []
    if phase_sequence:
        current_phase = phase_sequence[0]
        run_length = 1
        for phase in phase_sequence[1:]:
            if phase == current_phase:
                run_length += 1
                continue
            if run_length > 1:
                repeated_phase_runs.append({"phase": current_phase, "length": run_length})
            current_phase = phase
            run_length = 1
        if run_length > 1:
            repeated_phase_runs.append({"phase": current_phase, "length": run_length})

    anomalies = {
        "stuck_in_p2": any(
            item["phase"] == "p2_explorer" and item["length"] >= 2
            for item in repeated_phase_runs
        ),
        "phase_regression": any(
            pair in {"p3_recommender->p2_explorer", "p4_interventor->p2_explorer", "p4_interventor->p3_recommender"}
            for pair in transition_pairs
        ),
        "unfinished_p4": bool(phase_sequence) and phase_sequence[-1] == "p4_interventor",
    }

    return {
        "phase_sequence": phase_sequence,
        "phase_counts": phase_counts,
        "transition_pairs": transition_pairs,
        "repeated_phase_runs": repeated_phase_runs,
        "anomalies": anomalies,
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
