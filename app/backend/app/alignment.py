"""对齐分数代码层追踪

轻量级文本检测 + 分数更新，作为 LLM 自主感知的安全网。
"""

import re

# 不对齐关键词 → (类型, 分数变化)
MISALIGNMENT_PATTERNS: list[tuple[str, str, int]] = [
    # 不信任
    (r"你只是.{0,4}(机器|AI|程序|机器人)", "distrust", -5),
    (r"(你|AI).{0,6}(不懂|不理解|不明白)", "distrust", -5),
    (r"你.{0,4}(不是|又不是).{0,4}(人|真人|咨询师)", "distrust", -5),
    # 不满
    (r"(没用|没有用|没什么用|一点用都没)", "dissatisfaction", -3),
    (r"(没帮助|没有帮助|帮不了)", "dissatisfaction", -3),
    (r"你.{0,4}(根本|完全).{0,6}(没|不)", "dissatisfaction", -3),
    (r"(浪费时间|浪费我的时间)", "dissatisfaction", -3),
    # 拒绝
    (r"(不想说|不想聊|不想谈|别问了|不要问)", "refusal", -5),
    (r"(算了|不说了|不聊了)", "refusal", -5),
    # 不同意
    (r"(不是这样|你说错了|不对|你搞错了)", "disagreement", -3),
    (r"(才不是|根本不是)", "disagreement", -3),
    # 困惑
    (r"(什么意思|听不懂|你在说什么)", "confusion", -2),
]

# 对齐正向信号
ALIGNMENT_PATTERNS: list[tuple[str, int]] = [
    (r"(有帮助|有用|有点用|感觉好一点)", 3),
    (r"(说得对|你说的对|确实是这样)", 2),
    (r"(愿意|可以试试|好的我试试)", 2),
    (r"(谢谢|感谢)", 2),
]


def detect_alignment_signal(user_message: str) -> tuple[int, str | None]:
    """检测用户消息中的对齐/不对齐信号

    返回 (分数变化, 不对齐类型或None)
    """
    text = user_message.strip()
    if not text:
        return 0, None

    # 先检测不对齐
    for pattern, signal_type, score_delta in MISALIGNMENT_PATTERNS:
        if re.search(pattern, text):
            return score_delta, signal_type

    # 检测正向对齐
    for pattern, score_delta in ALIGNMENT_PATTERNS:
        if re.search(pattern, text):
            return score_delta, None

    return 0, None
