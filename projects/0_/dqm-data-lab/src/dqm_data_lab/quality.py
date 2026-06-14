from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier


def detect_anomalies(frame: pd.DataFrame, contamination: float = 0.08) -> pd.Series:
    model = IsolationForest(contamination=contamination, random_state=42)
    labels = model.fit_predict(frame)
    return pd.Series(labels == -1, index=frame.index)


def top_features(frame: pd.DataFrame, labels: pd.Series | None, limit: int = 10) -> list[str]:
    if labels is None or labels.nunique() < 2:
        return [str(column) for column in frame.var().sort_values(ascending=False).head(limit).index]

    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    model.fit(frame, labels)
    importance = pd.Series(model.feature_importances_, index=frame.columns)
    return [str(column) for column in importance.sort_values(ascending=False).head(limit).index]


def quality_score(missing_rate_value: float, anomaly_rate_value: float) -> float:
    score = 100.0 - missing_rate_value * 45.0 - anomaly_rate_value * 35.0
    return round(max(0.0, min(100.0, score)), 2)

