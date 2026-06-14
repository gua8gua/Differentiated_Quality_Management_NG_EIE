from __future__ import annotations

from dqm_data_lab.schemas import GovernanceStageResult, MetricScore


def compute_quality_score(missing_rate: float, anomaly_rate: float, feature_count: int) -> tuple[float, list[MetricScore], GovernanceStageResult]:
    completeness = round(1 - missing_rate, 4)
    anomaly_control = round(1 - anomaly_rate, 4)
    modelability = round(min(1.0, feature_count / 10), 4)
    consistency = 0.82
    score = round(
        max(
            0.0,
            min(
                100.0,
                completeness * 35 + anomaly_control * 25 + modelability * 25 + consistency * 15,
            ),
        ),
        2,
    )
    metrics = [
        MetricScore(name="完整性", value=completeness, weight=0.35),
        MetricScore(name="异常可控性", value=anomaly_control, weight=0.25),
        MetricScore(name="可建模性", value=modelability, weight=0.25),
        MetricScore(name="一致性", value=consistency, weight=0.15, description="基础版本用固定示例值，后续接入规则校验"),
    ]

    return score, metrics, GovernanceStageResult(
        stage="08_quality_evaluation",
        summary="完成综合质量评分，当前为可扩展的基础加权模型。",
        metrics={
            "quality_score": score,
            "metric_count": len(metrics),
            "method": "weighted_quality_score",
        },
    )

