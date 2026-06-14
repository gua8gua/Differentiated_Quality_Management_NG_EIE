from __future__ import annotations

import json
from pathlib import Path

from dqm_data_lab.schemas import DataQualityReport, GovernanceStageResult, RiskSummary


def write_reports(
    out_dir: Path,
    report: DataQualityReport,
    risk: RiskSummary,
) -> GovernanceStageResult:
    out_dir.mkdir(parents=True, exist_ok=True)
    stage = GovernanceStageResult(
        stage="09_reporting",
        summary="完成治理报告与风险摘要 JSON 输出。",
        metrics={"file_count": 3},
        artifacts=[
            str(out_dir / "data_quality_report.json"),
            str(out_dir / "risk_summary.json"),
            str(out_dir / "data_quality_report.pretty.json"),
        ],
    )
    report.stage_results.append(stage)

    (out_dir / "data_quality_report.json").write_text(
        report.model_dump_json(indent=2), encoding="utf-8"
    )
    (out_dir / "risk_summary.json").write_text(risk.model_dump_json(indent=2), encoding="utf-8")
    (out_dir / "data_quality_report.pretty.json").write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return stage

