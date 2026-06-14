from __future__ import annotations

from pydantic import BaseModel, Field


class Triple(BaseModel):
    head: str
    relation: str
    tail: str
    head_type: str = "未知"
    tail_type: str = "未知"
    description: str = ""


class TraceRequest(BaseModel):
    phenomenon: str
    max_depth: int = Field(default=3, ge=1, le=5)


class TracePath(BaseModel):
    nodes: list[str]
    relations: list[str]
    evidence: list[str]


class TraceResponse(BaseModel):
    phenomenon: str
    paths: list[TracePath]
    recommended_actions: list[str]


class ExplainRequest(BaseModel):
    phenomenon: str
    risk_level: str = "中"
    evidence: list[str] = Field(default_factory=list)


class ExplainResponse(BaseModel):
    title: str
    summary: str
    trace: TraceResponse


class WorkflowStage(BaseModel):
    stage: str
    summary: str
    metrics: dict[str, object] = Field(default_factory=dict)


class WorkflowResponse(BaseModel):
    phenomenon: str
    stages: list[WorkflowStage]
    explanation: ExplainResponse

