from __future__ import annotations

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from dqm_data_lab.schemas import GovernanceStageResult


def impute_missing_values(
    frame: pd.DataFrame,
    strategy: str = "median",
) -> tuple[pd.DataFrame, GovernanceStageResult]:
    missing_before = int(frame.isna().sum().sum())
    imputer = SimpleImputer(strategy=strategy)
    imputed = pd.DataFrame(imputer.fit_transform(frame), columns=frame.columns, index=frame.index)

    return imputed, GovernanceStageResult(
        stage="04_impute",
        summary=f"完成缺失值填补，策略={strategy}。",
        metrics={
            "missing_before": missing_before,
            "missing_after": int(imputed.isna().sum().sum()),
            "strategy": strategy,
        },
    )


def normalize_numeric_values(frame: pd.DataFrame) -> tuple[pd.DataFrame, GovernanceStageResult]:
    scaler = StandardScaler()
    scaled = pd.DataFrame(scaler.fit_transform(frame), columns=frame.columns, index=frame.index)

    return scaled, GovernanceStageResult(
        stage="05_normalize",
        summary="完成数值质量指标 Z-score 标准化。",
        metrics={
            "method": "z_score",
            "column_count": int(scaled.shape[1]),
        },
    )

