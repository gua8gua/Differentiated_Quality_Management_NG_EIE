from __future__ import annotations

import pandas as pd

from dqm_data_lab.schemas import GovernanceStageResult


def profile_frame(frame: pd.DataFrame) -> GovernanceStageResult:
    numeric_columns = frame.select_dtypes(include="number").columns
    missing_by_column = frame.isna().mean().sort_values(ascending=False).head(10)

    return GovernanceStageResult(
        stage="01_profile",
        summary="完成数据资产剖析，统计行列规模、数值列数量、缺失率和高缺失字段。",
        metrics={
            "row_count": int(frame.shape[0]),
            "column_count": int(frame.shape[1]),
            "numeric_column_count": int(len(numeric_columns)),
            "missing_rate": float(frame.isna().sum().sum() / frame.size) if frame.size else 0.0,
            "top_missing_columns": {str(k): float(v) for k, v in missing_by_column.items()},
        },
    )

