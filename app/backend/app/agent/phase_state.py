"""四阶段 flow state 最小变量集。"""

from __future__ import annotations

from app.agent.flow_controller import build_minimal_flow_state


def build_default_phase_state(
    *,
    active_phase: str = "p1_listener",
    active_skill: dict | None = None,
) -> dict:
    """构造最小 phase state 默认值。"""
    return build_minimal_flow_state(
        active_phase=active_phase,
        active_skill=active_skill,
    )
