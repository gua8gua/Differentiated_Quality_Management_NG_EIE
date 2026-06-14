from __future__ import annotations

from pathlib import Path

from .registry import get_adapter, infer_adapter
from .schemas import DataQualityReport, DatasetContext, RiskSummary
from .stages.anomaly import detect_isolation_forest
from .stages.classification import classify_quality_risk
from .stages.cleaning import impute_missing_values, normalize_numeric_values
from .stages.evaluation import compute_quality_score
from .stages.feature_selection import select_top_features
from .stages.profiling import profile_frame
from .stages.reporting import write_reports
from .stages.rul import summarize_rul
from .stages.standardization import select_numeric_frame, standardize_schema
from .stages.timeseries_similarity import summarize_similarity_and_trend


def run_dataset_pipeline(
    dataset_dir: Path,
    out_dir: Path,
    context: DatasetContext,
    dataset_type: str = "auto",
) -> tuple[DataQualityReport, RiskSummary]:
    adapter = infer_adapter(dataset_dir) if dataset_type == "auto" else get_adapter(dataset_type)
    bundle = adapter.load(dataset_dir, context)
    raw = bundle.frame
    labels = bundle.labels

    stage_results = []
    stage_results.append(profile_frame(raw))
    standardized, stage = standardize_schema(raw, bundle.context)
    stage_results.append(stage)
    numeric, stage = select_numeric_frame(standardized)
    stage_results.append(stage)

    if numeric.empty:
        raise ValueError("No numeric columns found. Add a modality-specific adapter before running governance.")

    raw_missing_rate = float(raw.isna().sum().sum() / raw.size) if raw.size else 0.0
    imputed, stage = impute_missing_values(numeric)
    stage_results.append(stage)
    cleaned, stage = normalize_numeric_values(imputed)
    stage_results.append(stage)
    anomalies, stage = detect_isolation_forest(cleaned)
    stage_results.append(stage)
    anomaly_rate = float(anomalies.mean())
    features, stage = select_top_features(cleaned, labels)
    stage_results.append(stage)
    score, metrics, stage = compute_quality_score(raw_missing_rate, anomaly_rate, len(features))
    stage_results.append(stage)
    classification, stage = classify_quality_risk(cleaned, labels)
    stage_results.append(stage)
    if "unit_column" in bundle.profile.metadata and "cycle_column" in bundle.profile.metadata:
        unit_column = bundle.profile.metadata["unit_column"]
        cycle_column = bundle.profile.metadata["cycle_column"]
        rul, stage = summarize_rul(raw, unit_column=unit_column, cycle_column=cycle_column)
    else:
        rul, stage = None, summarize_rul(raw, unit_column="__missing_unit__", cycle_column="__missing_cycle__")[1]
    stage_results.append(stage)
    similarity, trend, stage = summarize_similarity_and_trend(cleaned, features)
    stage_results.append(stage)

    report = DataQualityReport(
        context=bundle.context,
        profile=bundle.profile,
        dataset_name=bundle.context.name,
        row_count=int(raw.shape[0]),
        column_count=int(raw.shape[1]),
        missing_rate=round(raw_missing_rate, 4),
        anomaly_rate=round(anomaly_rate, 4),
        quality_score=score,
        metrics=metrics,
        top_features=features,
        stage_results=stage_results,
        notes=[
            "基础版本完成中位数填充、Z-score标准化、IsolationForest异常检测。",
            f"已通过 {adapter.name} 适配器接入，模态={bundle.context.modality}，对象={bundle.context.quality_object}，用途={bundle.context.use_case}。",
        ],
    )

    risk_level = "高" if anomaly_rate > 0.15 else "中" if anomaly_rate > 0.08 else "低"
    risk = RiskSummary(
        context=bundle.context,
        dataset_name=bundle.context.name,
        risk_level=risk_level,
        abnormal_sample_count=int(anomalies.sum()),
        abnormal_rate=round(anomaly_rate, 4),
        evidence=[
            {"type": "top_feature", "name": feature, "description": "随机森林/方差筛选得到的关键质量特征"}
            for feature in features[:5]
        ],
        recommended_next_step="将异常样本和关键特征提交给 dqm-kg-rag 做图谱追溯与解释。",
        classification=classification,
        rul=rul,
        similarity=similarity,
        trend=trend,
    )

    write_reports(out_dir, report, risk)

    return report, risk


def run_secom_pipeline(dataset_dir: Path, out_dir: Path) -> tuple[DataQualityReport, RiskSummary]:
    context = DatasetContext(
        name="SECOM",
        modality="tabular",
        quality_object="component",
        use_case="governance",
        standards=["ISO8000", "project_custom"],
    )
    return run_dataset_pipeline(dataset_dir, out_dir, context, dataset_type="secom")

