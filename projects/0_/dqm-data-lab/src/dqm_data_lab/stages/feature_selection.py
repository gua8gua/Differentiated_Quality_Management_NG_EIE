from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from dqm_data_lab.schemas import GovernanceStageResult


def select_top_features(
    frame: pd.DataFrame,
    labels: pd.Series | None,
    limit: int = 10,
) -> tuple[list[str], GovernanceStageResult]:
    if labels is None or labels.nunique() < 2:
        scores = frame.var().sort_values(ascending=False)
        method = "variance"
    else:
        model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        model.fit(frame, labels)
        scores = pd.Series(model.feature_importances_, index=frame.columns).sort_values(ascending=False)
        method = "random_forest_importance"

    features = [str(column) for column in scores.head(limit).index]
    return features, GovernanceStageResult(
        stage="07_feature_selection",
        summary=f"完成关键质量特征筛选，方法={method}。",
        metrics={
            "method": method,
            "selected_count": len(features),
            "top_features": features,
        },
    )

