"""隐私脱敏辅助函数。"""

from __future__ import annotations

import re

EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?86[- ]?)?1\d{10}(?!\d)")
UUID_RE = re.compile(
    r"\b[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}\b"
)
LONG_ID_RE = re.compile(r"(?<!\d)\d{15,18}(?!\d)")


def redact_sensitive_text(text: str | None, limit: int = 160) -> str:
    """对诊断、评估、trace 场景中的文本做轻量脱敏和截断。"""
    value = (text or "").strip()
    if not value:
        return ""

    value = PHONE_RE.sub("[phone]", value)
    value = EMAIL_RE.sub("[email]", value)
    value = UUID_RE.sub("[id]", value)
    value = LONG_ID_RE.sub("[id]", value)

    if len(value) <= limit:
        return value
    return value[:limit] + "..."
