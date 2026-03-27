"""输入安全层（硬编码，LLM 之前执行）

检测危机信号和 prompt injection，触发时绕过 LLM 直接返回预设响应。
"""

import re
from dataclasses import dataclass

# ── 危机关键词 ──────────────────────────────────────────────

_CRISIS_PATTERNS = [
    # 自杀意念
    r"不想活", r"想死", r"想自杀", r"自杀", r"结束生命", r"活着没意思",
    r"活不下去", r"不如死", r"去死", r"寻死", r"轻生", r"了断",
    r"不想.*存在", r"消失.*世界",
    # 自我伤害
    r"割腕", r"割手", r"自残", r"自伤", r"伤害自己", r"烫自己",
    r"撞墙", r"打自己",
]

_CRISIS_RE = re.compile("|".join(_CRISIS_PATTERNS), re.IGNORECASE)

CRISIS_RESPONSE = (
    "听到你这样说，我非常担心你的安全。你现在安全吗？\n\n"
    "如果你正处于困境中，请联系专业的危机支持：\n"
    "· 24小时心理援助热线：400-161-9995\n"
    "· 北京心理危机研究与干预中心：010-82951332\n"
    "· 生命热线：400-821-1215\n"
    "· 紧急情况请拨打 120 或 110\n\n"
    "我会一直在这里陪着你。如果你愿意，可以告诉我现在的感受。"
)

# ── Prompt Injection 检测 ──────────────────────────────────

_INJECTION_PATTERNS = [
    r"忽略.*(?:上面|之前|以上).*(?:指令|提示|要求|规则)",
    r"忘记.*(?:之前|上面).*(?:设定|角色|指令)",
    r"你现在是(?!心雀)",  # "你现在是X"但不是"你现在是心雀"
    r"(?:扮演|充当|假装).*(?:另一个|其他|新的)",
    r"ignore.*(?:previous|above|system).*(?:instructions?|prompt|rules?)",
    r"you are now",
    r"forget.*(?:previous|system)",
    r"jailbreak",
    r"DAN",
]

_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)

INJECTION_RESPONSE = "我注意到你的消息里有一些特殊内容。我是心雀，一位心理咨询师，我只能在这个角色下和你交流。你今天想聊些什么呢？"


# ── 公共接口 ──────────────────────────────────────────────


@dataclass
class GuardResult:
    """输入安全层检测结果"""
    blocked: bool
    reason: str | None = None  # "crisis" | "injection" | None
    response: str | None = None  # 预设响应（blocked=True 时）


def check_input(message: str) -> GuardResult:
    """检测用户输入，返回检测结果

    如果 blocked=True，调用方应直接返回 response，不再调用 LLM。
    """
    # 危机检测（最高优先级）
    if _CRISIS_RE.search(message):
        return GuardResult(blocked=True, reason="crisis", response=CRISIS_RESPONSE)

    # 注入防护
    if _INJECTION_RE.search(message):
        return GuardResult(blocked=True, reason="injection", response=INJECTION_RESPONSE)

    return GuardResult(blocked=False)
