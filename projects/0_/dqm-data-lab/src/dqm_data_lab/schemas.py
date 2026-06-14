from __future__ import annotations

from datetime import datetime
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


class DatasetContext(BaseModel):
    name: str
    modality: DataModality = "tabular"
    quality_object: QualityObject = "generic"
    use_case: UseCase = "governance"
    standards: list[QualityStandard] = Field(default_factory=lambda: ["project_custom"])
    description: str = ""
    tags: list[str] = Field(default_factory=list)


class DataAssetProfile(BaseModel):
    row_count: int
    column_count: int
    numeric_column_count: int
    missing_rate: float
    label_available: bool
    metadata: dict[str, Any] = Field(default_factory=dict)


class MetricScore(BaseModel):
    name: str
    value: float
    weight: float = 1.0
    description: str = ""


class GovernanceStageResult(BaseModel):
    stage: str
    status: Literal["success", "warning", "skipped", "failed"] = "success"
    summary: str
    metrics: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[str] = Field(default_factory=list)


class DataQualityReport(BaseModel):
    generated_at: datetime = Field(default_factory=datetime.now)
    context: DatasetContext
    profile: DataAssetProfile
    dataset_name: str
    row_count: int
    column_count: int
    missing_rate: float
    anomaly_rate: float
    quality_score: float
    metrics: list[MetricScore]
    top_features: list[str]
    stage_results: list[GovernanceStageResult] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class RiskSummary(BaseModel):
    generated_at: datetime = Field(default_factory=datetime.now)
    context: DatasetContext
    dataset_name: str
    risk_level: str
    abnormal_sample_count: int
    abnormal_rate: float
    evidence: list[dict[str, Any]]
    recommended_next_step: str
    classification: dict[str, Any] | None = None
    rul: dict[str, Any] | None = None
    similarity: dict[str, Any] | None = None
    trend: dict[str, Any] | None = None

