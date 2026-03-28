"""Trace 持久化抽象，便于后续切换到 OpenTelemetry 等后端。"""

from __future__ import annotations

from typing import Protocol

from app.trace_helpers import create_trace_record


class TraceSink(Protocol):
    """Trace 写入抽象接口。"""

    def build_record(
        self,
        session_id: str,
        turn_number: int,
        input_safety: dict,
        llm_call: dict,
        output_safety: dict,
        total_latency_ms: int,
    ):
        """构建待持久化的 trace 对象。"""


class DatabaseTraceSink:
    """基于数据库 ORM 的 trace sink。"""

    def __init__(self, trace_model):
        self._trace_model = trace_model

    def build_record(
        self,
        session_id: str,
        turn_number: int,
        input_safety: dict,
        llm_call: dict,
        output_safety: dict,
        total_latency_ms: int,
    ):
        """构建数据库 trace 记录。"""
        return create_trace_record(
            trace_model=self._trace_model,
            session_id=session_id,
            turn_number=turn_number,
            input_safety=input_safety,
            llm_call=llm_call,
            output_safety=output_safety,
            total_latency_ms=total_latency_ms,
        )
