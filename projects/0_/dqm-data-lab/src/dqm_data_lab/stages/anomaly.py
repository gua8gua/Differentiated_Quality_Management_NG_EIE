from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest

from dqm_data_lab.schemas import GovernanceStageResult


def detect_isolation_forest(
    frame: pd.DataFrame,
    contamination: float = 0.08,
) -> tuple[pd.Series, GovernanceStageResult]:
    model = IsolationForest(contamination=contamination, random_state=42)
    labels = model.fit_predict(frame)
    anomalies = pd.Series(labels == -1, index=frame.index)

    return anomalies, GovernanceStageResult(
        stage="06_anomaly_detection",
        summary="完成 IsolationForest 基础异常检测。",
        metrics={
            "method": "IsolationForest",
            "contamination": contamination,
            "abnormal_sample_count": int(anomalies.sum()),
            "anomaly_rate": float(anomalies.mean()),
        },
    )

