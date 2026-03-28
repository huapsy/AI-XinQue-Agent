"""管理侧匿名统计辅助函数。"""

from __future__ import annotations


def build_admin_metrics_payload(sessions: list, interventions: list, traces: list, message_counts: dict[str, int]) -> dict:
    """聚合会话、干预和 trace 统计。"""
    session_count = len(sessions)
    average_turns = 0.0
    if session_count:
        average_turns = round(sum(message_counts.get(session.session_id, 0) / 2 for session in sessions) / session_count, 1)

    intervention_completion_rate = 0.0
    if interventions:
        intervention_completion_rate = round(
            sum(1 for item in interventions if getattr(item, "completed", False)) / len(interventions),
            2,
        )

    safety_trigger_rate = 0.0
    tool_failure_rate = 0.0
    average_latency_ms = 0.0
    if traces:
        safety_trigger_rate = round(
            sum(1 for trace in traces if (getattr(trace, "input_safety", {}) or {}).get("triggered")) / len(traces),
            2,
        )
        tool_calls = [call for trace in traces for call in (getattr(trace, "llm_call", {}) or {}).get("tool_calls", [])]
        if tool_calls:
            tool_failure_rate = round(sum(1 for call in tool_calls if not call.get("success", True)) / len(tool_calls), 2)
        average_latency_ms = round(
            sum(getattr(trace, "total_latency_ms", 0) or 0 for trace in traces) / len(traces),
            1,
        )

    return {
        "session_count": session_count,
        "average_turns": average_turns,
        "intervention_completion_rate": intervention_completion_rate,
        "safety_trigger_rate": safety_trigger_rate,
        "tool_failure_rate": tool_failure_rate,
        "average_latency_ms": average_latency_ms,
    }
