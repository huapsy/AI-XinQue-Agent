"""OTel 兼容导出辅助函数。"""

from __future__ import annotations

import json
from pathlib import Path

from app.settings import get_otel_enabled, get_otel_exporter_endpoint

_OTEL_PATH = Path(__file__).resolve().parent.parent / "data" / "otel_spans.jsonl"


def export_trace_event(name: str, payload: dict) -> None:
    """导出 trace 事件。

    若安装了 opentelemetry，可后续替换为真实 exporter；
    当前最小实现写入 OTel 兼容的 JSON 行文件。
    """
    if not get_otel_enabled():
        return
    _OTEL_PATH.parent.mkdir(exist_ok=True)
    record = {
        "name": name,
        "service.name": "xinque-backend",
        "otel.endpoint": get_otel_exporter_endpoint(),
        "attributes": payload,
    }
    with _OTEL_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
