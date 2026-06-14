from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SELF = ROOT / "projects" / "0_"
DATA_LAB_SRC = SELF / "dqm-data-lab" / "src"
KG_RAG_SRC = SELF / "dqm-kg-rag" / "src"

sys.path.insert(0, str(DATA_LAB_SRC))
sys.path.insert(0, str(KG_RAG_SRC))

from dqm_data_lab.pipeline import run_dataset_pipeline  # noqa: E402
from dqm_data_lab.schemas import DatasetContext  # noqa: E402
from dqm_kg_rag.schemas import ExplainRequest  # noqa: E402
from dqm_kg_rag.store import default_graph  # noqa: E402
from dqm_kg_rag.workflow import run_kg_rag_workflow  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the DQM minimal full-flow analysis.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=ROOT / "datasets" / "01_tabular_secom",
        help="Highly relevant local dataset path. Default: datasets/01_tabular_secom",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=SELF / "outputs" / "secom_full_flow",
        help="Full-flow output directory.",
    )
    parser.add_argument(
        "--cmapss",
        type=Path,
        default=ROOT / "datasets" / "03_phm_nasa_cmapss",
        help="Optional C-MAPSS path for simplified RUL output.",
    )
    return parser


def _risk_case_from_summary(risk_summary: Any) -> tuple[str, list[str]]:
    evidence = risk_summary.evidence
    feature = evidence[0]["name"] if evidence else "feature_87"
    phenomenon = f"异常特征{feature}"
    evidence_text = [f"{item['name']}：{item['description']}" for item in evidence[:5]]
    return phenomenon, evidence_text


def _path_nodes(workflow: Any) -> list[list[str]]:
    paths = workflow.explanation.trace.paths
    return [path.nodes for path in paths[:5]]


def _dtw_mock_from_evidence(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labels = ["制造过程波动", "设备状态漂移", "工艺窗口偏移"]
    return [
        {
            "caseId": f"secom-case-{index + 1:03d}",
            "similarity": round(0.92 - index * 0.04, 2),
            "label": labels[index % len(labels)],
        }
        for index, _ in enumerate(evidence[:3])
    ]


def _similar_segments(risk: Any) -> list[dict[str, Any]]:
    segments = (risk.similarity or {}).get("segments", []) if risk.similarity else []
    if segments:
        return [
            {
                "caseId": item["caseId"],
                "similarity": item["similarity"],
                "label": item["label"],
            }
            for item in segments
        ]
    return _dtw_mock_from_evidence(risk.evidence)


def _rul_curve(secom_risk: Any, cmapss_risk: Any | None) -> list[dict[str, Any]]:
    source = cmapss_risk or secom_risk
    rul = source.rul if source else None
    if rul and rul.get("curve"):
        return [{"cycle": item["cycle"], "value": item["value"]} for item in rul["curve"][:8]]
    return [
        {"cycle": 1, "value": 122},
        {"cycle": 20, "value": 105},
        {"cycle": 40, "value": 82},
        {"cycle": 60, "value": 61},
    ]


def _disposal_report(risk: Any, workflow: Any) -> dict[str, Any]:
    paths = _path_nodes(workflow)
    root_path = paths[-1] if paths else [workflow.phenomenon]
    evidence = [f"{item['name']}：{item['description']}" for item in risk.evidence[:5]]
    action = workflow.explanation.trace.recommended_actions[0] if workflow.explanation.trace.recommended_actions else "继续补充证据并复核质量记录"
    return {
        "phenomenon": workflow.phenomenon,
        "riskLevel": risk.risk_level,
        "evidenceChain": evidence,
        "rootCausePath": root_path,
        "recommendation": action,
        "responsibleObject": "元器件/制造过程",
    }


def _agent_decisions(risk: Any, workflow: Any) -> list[dict[str, Any]]:
    action = workflow.explanation.trace.recommended_actions[0] if workflow.explanation.trace.recommended_actions else "补充人工复核"
    return [
        {
            "agent": "整机质量管控智能体",
            "judgment": "当前风险来自元器件/制造过程侧，可能向整机可靠性传导。",
            "recommendation": "维持运行但提升相关批次监测频率。",
            "confidence": 0.72,
        },
        {
            "agent": "软件质量管控智能体",
            "judgment": "本轮证据未指向软件接口或版本变更根因。",
            "recommendation": "保持日志监测，暂不触发版本回退。",
            "confidence": 0.64,
        },
        {
            "agent": "元器件质量管控智能体",
            "judgment": f"异常率 {risk.abnormal_rate}，图谱建议执行：{action}。",
            "recommendation": action,
            "confidence": 0.86,
        },
    ]


def _feedback_evaluation(risk: Any, workflow: Any) -> dict[str, Any]:
    action_count = len(workflow.explanation.trace.recommended_actions)
    return {
        "timeliness": 0.86,
        "effectiveness": 0.82 if action_count else 0.62,
        "completeness": 0.78,
        "recurrenceRisk": "中" if risk.risk_level == "中" else risk.risk_level,
        "summary": "已形成从异常特征、图谱根因到处置建议的闭环；后续需接入真实处置结果以校准复发风险。",
    }


def _dashboard_payload(report: Any, risk: Any, workflow: Any, cmapss_risk: Any | None = None) -> dict[str, Any]:
    phenomenon = workflow.phenomenon
    return {
        "overview": {
            "title": "新一代电子信息装备差异化质量管控",
            "subtitle": "SECOM 元器件/制造过程质量数据全流程分析样例",
            "objects": ["基础元器件", "制造过程", "质量指标"],
            "coreWorks": [
                "质量数据可信治理与评价",
                "质控知识图谱与差异化根因追溯",
                "质量风险预测与三类智能体协同管控",
            ],
        },
        "dataQuality": {
            "dataset": report.dataset_name,
            "qualityScore": report.quality_score,
            "missingRate": report.missing_rate,
            "anomalyRate": report.anomaly_rate,
            "topFeatures": report.top_features[:5],
        },
        "riskPrediction": {
            "riskLevel": risk.risk_level,
            "phenomenon": phenomenon,
            "classification": risk.classification,
            "trend": risk.trend,
            "dtwSimilarSegments": _similar_segments(risk),
            "rul": _rul_curve(risk, cmapss_risk),
        },
        "graphTrace": {
            "phenomenon": phenomenon,
            "paths": _path_nodes(workflow),
            "summary": workflow.explanation.summary,
        },
        "workflow": [
            {"stage": "01_data_governance", "project": "dqm-data-lab", "output": "data_quality_report.json"},
            {"stage": "02_risk_summary", "project": "dqm-data-lab", "output": "risk_summary.json"},
            {"stage": "03_kg_workflow", "project": "dqm-kg-rag", "output": "kg_workflow.json"},
            {"stage": "04_agent_disposal", "project": "dqm-platform", "output": "disposalReport / agentDecisions"},
            {"stage": "05_feedback", "project": "dqm-platform", "output": "feedbackEvaluation"},
            {"stage": "06_dashboard_sync", "project": "dqm-platform", "output": "mock-data/dashboard.json"},
        ],
        "agents": [
            {
                "name": "整机质量管控智能体",
                "code": "PRL",
                "input": "质量评分、风险等级、下级元器件风险",
                "output": "全局质量状态与处置优先级",
                "recommendation": "当前为制造过程样例，整机侧建议关注批次风险对整机可靠性的传导。",
            },
            {
                "name": "软件质量管控智能体",
                "code": "FCT",
                "input": "质量事件、接口日志、版本信息",
                "output": "软件侧关联风险与回归测试建议",
                "recommendation": "本样例未触发软件侧根因，可保持监测并等待软件质量数据接入。",
            },
            {
                "name": "元器件质量管控智能体",
                "code": "PFP",
                "input": "SECOM关键特征、异常率、图谱处置路径",
                "output": "元器件/制造过程风险与筛查建议",
                "recommendation": "优先复核工艺参数、设备状态和批次一致性。",
            },
        ],
        "agentDecisions": _agent_decisions(risk, workflow),
        "disposalReport": _disposal_report(risk, workflow),
        "feedbackEvaluation": _feedback_evaluation(risk, workflow),
    }


def main() -> None:
    args = build_parser().parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    context = DatasetContext(
        name="SECOM",
        modality="tabular",
        quality_object="component",
        use_case="governance",
        standards=["ISO8000", "project_custom"],
        description="本地最相关的元器件/半导体制造过程质量数据。",
        tags=["semiconductor", "component", "manufacturing_quality"],
    )
    report, risk = run_dataset_pipeline(args.dataset, args.out / "data_lab", context, dataset_type="secom")
    cmapss_risk = None
    if args.cmapss.exists():
        cmapss_context = DatasetContext(
            name="C-MAPSS FD001",
            modality="timeseries",
            quality_object="component",
            use_case="risk_prediction",
            standards=["project_custom"],
            description="本地 C-MAPSS 退化数据，用于简化 RUL 输出。",
            tags=["rul", "degradation"],
        )
        _, cmapss_risk = run_dataset_pipeline(args.cmapss, args.out / "cmapss", cmapss_context, dataset_type="cmapss")
    phenomenon, evidence_text = _risk_case_from_summary(risk)
    workflow = run_kg_rag_workflow(
        default_graph(),
        ExplainRequest(phenomenon=phenomenon, risk_level=risk.risk_level, evidence=evidence_text),
    )

    kg_out = args.out / "kg_workflow.json"
    kg_out.write_text(workflow.model_dump_json(indent=2), encoding="utf-8")

    dashboard = _dashboard_payload(report, risk, workflow, cmapss_risk)
    dashboard_out = SELF / "dqm-platform" / "mock-data" / "dashboard.json"
    dashboard_out.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.out / "dashboard.json").write_text(json.dumps(dashboard, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"dataset={report.dataset_name}")
    print(f"quality_score={report.quality_score}")
    print(f"risk_level={risk.risk_level}")
    print(f"phenomenon={phenomenon}")
    print(f"dashboard={dashboard_out}")


if __name__ == "__main__":
    main()

