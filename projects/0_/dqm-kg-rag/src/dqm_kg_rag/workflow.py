from __future__ import annotations

from .ontology.catalog import ontology_summary
from .rag import explain_risk
from .schemas import ExplainRequest, WorkflowResponse, WorkflowStage
from .store import InMemoryGraph


def run_kg_rag_workflow(
    graph: InMemoryGraph,
    request: ExplainRequest,
) -> WorkflowResponse:
    ontology = ontology_summary()
    validation = graph.validate()
    explanation = explain_risk(graph, request)

    stages = [
        WorkflowStage(
            stage="01_ontology",
            summary="加载质控本体类型与关系约束。",
            metrics={
                "entity_type_count": len(ontology["entities"]),
                "relation_type_count": len(ontology["relations"]),
            },
        ),
        WorkflowStage(
            stage="02_import_validate",
            summary="完成三元组导入与完整性校验。",
            metrics=validation,
        ),
        WorkflowStage(
            stage="03_trace",
            summary="基于图谱路径执行根因追溯。",
            metrics={
                "path_count": len(explanation.trace.paths),
                "recommended_action_count": len(explanation.trace.recommended_actions),
            },
        ),
        WorkflowStage(
            stage="04_explain",
            summary="融合图谱路径、证据与风险等级生成解释文本。",
            metrics={"risk_level": request.risk_level},
        ),
    ]

    return WorkflowResponse(
        phenomenon=request.phenomenon,
        stages=stages,
        explanation=explanation,
    )

