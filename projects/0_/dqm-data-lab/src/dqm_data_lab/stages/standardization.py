from __future__ import annotations

import re

import pandas as pd

from dqm_data_lab.schemas import DatasetContext, GovernanceStageResult


def normalize_column_name(column: object) -> str:
    value = str(column).strip().lower()
    value = re.sub(r"[^0-9a-zA-Z_\u4e00-\u9fff]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unnamed"


def standardize_schema(
    frame: pd.DataFrame,
    context: DatasetContext,
) -> tuple[pd.DataFrame, GovernanceStageResult]:
    standardized = frame.copy()
    original_columns = [str(column) for column in standardized.columns]
    standardized.columns = [normalize_column_name(column) for column in standardized.columns]

    return standardized, GovernanceStageResult(
        stage="02_standardize",
        summary="完成字段命名规范化，并记录标准体系与数据对象语义。",
        metrics={
            "modality": context.modality,
            "quality_object": context.quality_object,
            "use_case": context.use_case,
            "standards": context.standards,
            "renamed_column_count": sum(
                old != new for old, new in zip(original_columns, standardized.columns, strict=False)
            ),
        },
    )


def select_numeric_frame(frame: pd.DataFrame) -> tuple[pd.DataFrame, GovernanceStageResult]:
    numeric = frame.select_dtypes(include="number")
    return numeric, GovernanceStageResult(
        stage="03_select_numeric",
        status="success" if not numeric.empty else "warning",
        summary="完成数值型质量指标提取；非数值模态后续应接入专用特征提取适配器。",
        metrics={
            "input_column_count": int(frame.shape[1]),
            "numeric_column_count": int(numeric.shape[1]),
            "dropped_non_numeric_count": int(frame.shape[1] - numeric.shape[1]),
        },
    )

