from __future__ import annotations

from .schemas import ExplainRequest, ExplainResponse
from .store import InMemoryGraph


def explain_risk(graph: InMemoryGraph, request: ExplainRequest) -> ExplainResponse:
    trace = graph.trace(request.phenomenon, max_depth=3)
    action_text = "、".join(trace.recommended_actions) if trace.recommended_actions else "继续补充案例库"
    evidence_text = "；".join(request.evidence) if request.evidence else "图谱路径与历史案例"

    return ExplainResponse(
        title=f"{request.phenomenon} 风险解释",
        summary=(
            f"当前风险等级为{request.risk_level}。系统基于{evidence_text}进行追溯，"
            f"建议优先执行：{action_text}。"
        ),
        trace=trace,
    )

