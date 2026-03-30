"""管理侧匿名统计辅助函数。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def filter_sessions_for_admin_metrics(
    sessions: list,
    *,
    recent_sessions: int | None = None,
    since_days: int | None = None,
    now: datetime | None = None,
) -> list:
    """按最近 N 个 session 或最近 N 天过滤会话。"""
    scoped = list(sessions)
    if since_days is not None:
        reference_time = now or datetime.now(timezone.utc)
        cutoff = reference_time - timedelta(days=max(0, since_days))
        scoped = [
            session
            for session in scoped
            if getattr(session, "started_at", None) is not None and session.started_at >= cutoff
        ]

    scoped.sort(key=lambda session: getattr(session, "started_at", None) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    if recent_sessions is not None:
        scoped = scoped[: max(0, recent_sessions)]

    return scoped


def _build_combined_evaluation_summary(sessions: list, combined_evaluations: list | None) -> dict:
    payloads = []
    for item in combined_evaluations or []:
        if isinstance(item, dict):
            payloads.append(item)
            continue
        payloads.append(dict(getattr(item, "payload", {}) or {}))

    evaluated_session_count = len(payloads)
    coverage_rate = 0.0
    if sessions:
        coverage_rate = round(evaluated_session_count / len(sessions), 2)

    risk_flag_counts: dict[str, int] = {}
    average_scores: dict[str, float] = {}
    score_buckets: dict[str, list[float]] = {}
    sessions_with_risk_flags = 0

    for payload in payloads:
        risk_flags = payload.get("risk_flags") or []
        if risk_flags:
            sessions_with_risk_flags += 1
        for flag in risk_flags:
            risk_flag_counts[flag] = risk_flag_counts.get(flag, 0) + 1

        for score_name, value in dict(payload.get("scores") or {}).items():
            if isinstance(value, (int, float)):
                score_buckets.setdefault(score_name, []).append(float(value))

    for score_name, values in score_buckets.items():
        average_scores[score_name] = round(sum(values) / len(values), 2)

    return {
        "evaluated_session_count": evaluated_session_count,
        "coverage_rate": coverage_rate,
        "sessions_with_risk_flags": sessions_with_risk_flags,
        "risk_flag_counts": risk_flag_counts,
        "average_scores": average_scores,
    }


def build_admin_metrics_payload(
    sessions: list,
    interventions: list,
    traces: list,
    message_counts: dict[str, int],
    combined_evaluations: list | None = None,
) -> dict:
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
        "combined_evaluation_summary": _build_combined_evaluation_summary(sessions, combined_evaluations),
    }
