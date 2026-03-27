"""输出安全层（硬编码，LLM 之后执行）

检测 LLM 回复中的安全红线违规，触发时替换为安全回复。
"""

import re
from dataclasses import dataclass

# ── 诊断性表述 ──────────────────────────────────────────

_DIAGNOSIS_PATTERNS = [
    r"你(?:患有|得了|有)(?:抑郁症|焦虑症|双相|精神分裂|PTSD|强迫症|恐惧症|人格障碍)",
    r"(?:诊断|判断).*(?:你是|你有|你患)",
    r"你的(?:症状|病情)(?:是|属于)",
    r"根据.*(?:诊断标准|DSM|ICD)",
]

# ── 药物推荐 ──────────────────────────────────────────

_MEDICATION_PATTERNS = [
    r"(?:建议|推荐|可以).*(?:服用|吃|用).*(?:药|片|胶囊|颗粒)",
    r"(?:舍曲林|氟西汀|帕罗西汀|文拉法辛|度洛西汀|米氮平|阿米替林|氯硝西泮|阿普唑仑|劳拉西泮|奥氮平|喹硫平|利培酮|碳酸锂)",
    r"(?:抗抑郁|抗焦虑|镇静|安眠)(?:药物?|剂)",
    r"(?:SSRI|SNRI|苯二氮卓)",
]

# ── 绝对化承诺 ──────────────────────────────────────────

_ABSOLUTE_PATTERNS = [
    r"(?:保证|一定|肯定|绝对)(?:会|能|可以)(?:好起来|康复|痊愈|治好|解决)",
    r"(?:包治|根治|彻底治愈)",
]

_ALL_PATTERNS = _DIAGNOSIS_PATTERNS + _MEDICATION_PATTERNS + _ABSOLUTE_PATTERNS
_OUTPUT_RE = re.compile("|".join(_ALL_PATTERNS), re.IGNORECASE)

SAFE_REPLACEMENT = (
    "我注意到我刚才的表达可能不够准确。"
    "我不是医生，没有办法做专业诊断或给出医学建议。"
    "如果你有这方面的疑虑，建议咨询专业的心理咨询师或医生。"
    "你愿意继续和我聊聊你的感受吗？"
)


@dataclass
class OutputGuardResult:
    """输出安全层检测结果"""
    filtered: bool
    original: str
    output: str  # 过滤后的输出（filtered=False 时与 original 相同）
    reason: str | None = None


def check_output(reply: str) -> OutputGuardResult:
    """检测 LLM 回复是否违反安全红线

    如果 filtered=True，调用方应使用 output 替代 original 返回给用户。
    """
    match = _OUTPUT_RE.search(reply)
    if match:
        return OutputGuardResult(
            filtered=True,
            original=reply,
            output=SAFE_REPLACEMENT,
            reason=f"matched: {match.group()}"
        )

    return OutputGuardResult(filtered=False, original=reply, output=reply)
