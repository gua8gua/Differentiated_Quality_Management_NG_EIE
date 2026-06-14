from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from dqm_data_lab.schemas import GovernanceStageResult


def classify_quality_risk(
    frame: pd.DataFrame,
    labels: pd.Series | None,
) -> tuple[dict[str, object] | None, GovernanceStageResult]:
    if labels is None or labels.nunique() < 2:
        return None, GovernanceStageResult(
            stage="08a_classification",
            status="skipped",
            summary="未检测到可用分类标签，跳过质量风险分类。",
        )

    x_train, x_test, y_train, y_test = train_test_split(
        frame,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels,
    )
    model = RandomForestClassifier(n_estimators=120, random_state=42, class_weight="balanced")
    model.fit(x_train, y_train)
    predicted = model.predict(x_test)

    result: dict[str, object] = {
        "model": "RandomForestClassifier",
        "accuracy": round(float(accuracy_score(y_test, predicted)), 4),
        "precision": round(float(precision_score(y_test, predicted, average="weighted", zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predicted, average="weighted", zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, predicted, average="weighted", zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_test, predicted).tolist(),
        "test_size": int(len(y_test)),
    }
    return result, GovernanceStageResult(
        stage="08a_classification",
        summary="完成 SECOM pass/fail 质量风险分类基线。",
        metrics=result,
    )

