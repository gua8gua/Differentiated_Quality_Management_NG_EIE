from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

DataModality = Literal["tabular", "timeseries", "image", "text", "audio", "multimodal"]
QualityObject = Literal["whole_equipment", "software", "component", "process", "generic"]
UseCase = Literal[
    "governance",
    "quality_evaluation",
    "anomaly_detection",
    "risk_prediction",
    "rag_explanation",
]
QualityStandard = Literal["ISO8000", "GB_T_34960_5", "IEC62424", "project_custom"]


class DatasetContextPayload(BaseModel):
    name: str
    modality: DataModality = "tabular"
    quality_object: QualityObject = "generic"
    use_case: UseCase = "governance"
    standards: list[QualityStandard] = Field(default_factory=lambda: ["project_custom"])
    description: str = ""
    tags: list[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    upload_id: str
    context: DatasetContextPayload
    dataset_type: str = "auto"


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str
    upload_id: str | None = None


class TraceRequestPayload(BaseModel):
    phenomenon: str
    max_depth: int = 3


class StreamEvent(BaseModel):
    event: str
    stage: str = ""
    project: str = ""
    summary: str = ""
    metrics: dict[str, Any] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    timestamp: str = ""
    stage: str = ""


class MetadataOptions(BaseModel):
    modalities: list[str]
    quality_objects: list[str]
    use_cases: list[str]
    standards: list[str]
    dataset_types: list[str]
