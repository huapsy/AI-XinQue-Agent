"""四阶段子 agent profile 定义。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhaseProfile:
    """单个阶段子 agent 的最小配置。"""

    key: str
    display_name: str
    goal: str
    allowed_tools: tuple[str, ...]
    prompt_block: str


PHASE_PROFILES: dict[str, PhaseProfile] = {
    "p1_listener": PhaseProfile(
        key="p1_listener",
        display_name="P1 子Agent",
        goal="优先承接、澄清与建立最小联盟，不越级推进到推荐或干预。",
        allowed_tools=("recall_context", "search_memory", "referral"),
        prompt_block="""## 当前阶段子Agent

P1 子Agent（共情倾听）

- 当前目标：优先让用户感到被接住、被理解、被允许继续说
- 行为边界：不要过早推荐方法，不把回复写成表单式分流
- 允许工具：recall_context、search_memory、referral
""",
    ),
    "p2_explorer": PhaseProfile(
        key="p2_explorer",
        display_name="P2 子Agent",
        goal="边探索边形成工作性理解，补齐问题情境、情绪、认知和机制线索。",
        allowed_tools=("formulate", "search_memory", "update_profile", "referral"),
        prompt_block="""## 当前阶段子Agent

P2 子Agent（探索与个案概念化）

- 当前目标：继续探索、澄清，并形成工作性假设
- 行为边界：理解不足时不要进入推荐或干预
- 允许工具：formulate、search_memory、update_profile、referral
""",
    ),
    "p3_recommender": PhaseProfile(
        key="p3_recommender",
        display_name="P3 子Agent",
        goal="基于已有理解提出 1-2 个合适方案，并促成用户对下一步的接受。",
        allowed_tools=("match_intervention", "search_memory", "update_profile", "referral"),
        prompt_block="""## 当前阶段子Agent

P3 子Agent（推荐与激发）

- 当前目标：基于已有理解推荐有限方案并征得用户接受
- 行为边界：不要在用户尚未接受时直接进入 skill 执行
- 允许工具：match_intervention、search_memory、update_profile、referral
""",
    ),
    "p4_interventor": PhaseProfile(
        key="p4_interventor",
        display_name="P4 子Agent",
        goal="围绕已接受的 skill 或练习继续推进、收口并记录结果。",
        allowed_tools=("load_skill", "render_card", "record_outcome", "update_profile", "referral"),
        prompt_block="""## 当前阶段子Agent

P4 子Agent（干预执行）

- 当前目标：沿当前练习自然推进，必要时收口并记录结果
- 行为边界：不要回退成菜单式分流；优先继续当前 skill
- 允许工具：load_skill、render_card、record_outcome、update_profile、referral
""",
    ),
}


def list_phase_profiles() -> dict[str, PhaseProfile]:
    """返回全部阶段子 agent profile。"""
    return dict(PHASE_PROFILES)


def get_phase_profile(key: str) -> PhaseProfile:
    """按 key 获取阶段 profile。"""
    return PHASE_PROFILES[key]
