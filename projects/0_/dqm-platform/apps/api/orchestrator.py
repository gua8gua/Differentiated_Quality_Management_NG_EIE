from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[5]
SELF = Path(__file__).resolve().parents[3]
DATA_LAB_SRC = SELF / "dqm-data-lab" / "src"
KG_RAG_SRC = SELF / "dqm-kg-rag" / "src"

for path in (str(SELF), str(DATA_LAB_SRC), str(KG_RAG_SRC)):
    if path not in sys.path:
        sys.path.insert(0, path)

from dqm_data_lab.pipeline import run_dataset_pipeline  # noqa: E402
from dqm_data_lab.schemas import DatasetContext  # noqa: E402
from dqm_kg_rag.schemas import ExplainRequest  # noqa: E402
from dqm_kg_rag.store import default_graph  # noqa: E402
from dqm_kg_rag.workflow import run_kg_rag_workflow  # noqa: E402

from job_store import job_store  # noqa: E402
from run_full_flow import _dashboard_payload, _risk_case_from_summary  # noqa: E402


def metadata_options() -> dict[str, list[str]]:
    return {
        "modalities": ["tabular", "timeseries", "image", "text", "audio", "multimodal"],
        "quality_objects": ["whole_equipment", "software", "component", "process", "generic"],
        "use_cases": [
            "governance",
            "quality_evaluation",
            "anomaly_detection",
            "risk_prediction",
            "rag_explanation",
        ],
        "standards": ["ISO8000", "GB_T_34960_5", "IEC62424", "project_custom"],
        "dataset_types": ["auto", "generic_csv", "secom", "cmapss", "mcdm"],
    }


def _emit(job_id: str, event: str, stage: str, summary: str, **payload: Any) -> dict[str, Any]:
    record = {
        "event": event,
        "stage": stage,
        "project": payload.pop("project", "dqm-platform"),
        "summary": summary,
        "metrics": payload.pop("metrics", {}),
        "payload": payload,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    job_store.append_event(job_id, record)
    return record


def run_analysis_job(
    job_id: str,
    upload_dir: Path,
    context_payload: dict[str, Any],
    dataset_type: str = "auto",
    on_event: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    out_dir = upload_dir.parent / "outputs" / job_id
    out_dir.mkdir(parents=True, exist_ok=True)

    def emit(event: str, stage: str, summary: str, **payload: Any) -> None:
        record = _emit(job_id, event, stage, summary, **payload)
        if on_event:
            on_event(record)

    job_store.set_status(job_id, "running")
    emit("job_started", "00_init", "开始执行数据治理与图谱分析任务。", project="dqm-platform")

    context = DatasetContext(**context_payload)
    emit(
        "context_ready",
        "00_context",
        f"已加载数据上下文：{context.name} / {context.modality} / {context.quality_object}",
        project="dqm-data-lab",
        metrics={"modality": context.modality, "quality_object": context.quality_object},
    )

    emit("stage_start", "01_data_governance", "执行数据治理管道。", project="dqm-data-lab")
    report, risk = run_dataset_pipeline(upload_dir, out_dir / "data_lab", context, dataset_type=dataset_type)
    emit(
        "stage_done",
        "01_data_governance",
        f"数据治理完成，质量评分 {report.quality_score}。",
        project="dqm-data-lab",
        metrics={
            "quality_score": report.quality_score,
            "missing_rate": report.missing_rate,
            "anomaly_rate": report.anomaly_rate,
        },
    )

    phenomenon, evidence_text = _risk_case_from_summary(risk)
    emit(
        "stage_start",
        "02_kg_workflow",
        f"基于现象「{phenomenon}」启动知识图谱追溯。",
        project="dqm-kg-rag",
    )
    workflow = run_kg_rag_workflow(
        default_graph(),
        ExplainRequest(phenomenon=phenomenon, risk_level=risk.risk_level, evidence=evidence_text),
    )
    kg_out = out_dir / "kg_workflow.json"
    kg_out.write_text(workflow.model_dump_json(indent=2), encoding="utf-8")
    emit(
        "stage_done",
        "02_kg_workflow",
        workflow.explanation.summary,
        project="dqm-kg-rag",
        metrics={"path_count": len(workflow.explanation.trace.paths)},
    )

    dashboard = _dashboard_payload(report, risk, workflow)
    dashboard["overview"]["subtitle"] = f"{context.name} · {context.modality} · {context.quality_object}"
    dashboard["overview"]["objects"] = [context.quality_object, context.modality, context.use_case]

    mock_path = SELF / "dqm-platform" / "mock-data" / "dashboard.json"
    mock_path.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "dashboard.json").write_text(json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8")

    emit(
        "stage_done",
        "03_dashboard_sync",
        "Dashboard 已刷新，可在首页查看分析结果。",
        project="dqm-platform",
    )
    job_store.set_status(job_id, "completed", dashboard=dashboard)
    emit("job_completed", "99_done", "全流程分析完成。", project="dqm-platform", dashboard=dashboard)
    return dashboard
