"""Phase Flow 场景评估器。"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent import xinque


async def run_phase_flow_scenario(
    *,
    client,
    db: AsyncSession,
    user_id: str,
    session_id: str,
    turns: list[dict],
) -> dict:
    """执行一组多轮场景，并输出 phase flow 结构化报告。"""
    persisted_state = None
    observed_phases: list[str | None] = []
    expected_phases: list[str | None] = []
    mismatches: list[dict] = []

    for index, turn in enumerate(turns, start=1):
        result = await xinque.chat(
            client=client,
            history=[],
            user_message=turn["user_message"],
            user_id=user_id,
            session_id=session_id,
            db=db,
            trace_collector=[],
            persisted_session_state=persisted_state,
        )
        persisted_state = result["llm_trace"]["persisted_session_state"]
        observed_phase = persisted_state["stable_state"].get("active_phase")
        expected_phase = turn.get("expected_phase")

        observed_phases.append(observed_phase)
        expected_phases.append(expected_phase)

        if observed_phase != expected_phase:
            mismatches.append({
                "turn": index,
                "user_message": turn["user_message"],
                "expected_phase": expected_phase,
                "observed_phase": observed_phase,
            })

    return {
        "passed": not mismatches,
        "observed_phases": observed_phases,
        "expected_phases": expected_phases,
        "mismatches": mismatches,
        "turn_count": len(turns),
        "final_state": persisted_state["stable_state"] if persisted_state else {},
    }
