from __future__ import annotations

from fastapi import FastAPI, Query

from .ontology.catalog import ontology_summary
from .persistence.graph import Neo4jConfig, trace_phenomenon
from .rag import explain_risk
from .schemas import ExplainRequest, ExplainResponse, TraceRequest, TraceResponse, WorkflowResponse
from .store import default_graph
from .workflow import run_kg_rag_workflow

app = FastAPI(title="DQM KG RAG API", version="0.1.0")
graph = default_graph()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "dqm-kg-rag"}


@app.get("/graph")
def get_graph() -> dict[str, list[dict[str, str]]]:
    return graph.as_elements()


@app.get("/ontology")
def get_ontology() -> dict[str, list[dict[str, object]]]:
    return ontology_summary()


@app.get("/validate")
def validate_graph() -> dict[str, object]:
    return graph.validate()


@app.post("/trace", response_model=TraceResponse)
def trace(
    request: TraceRequest,
    backend: str = Query(default="in_memory", pattern="^(in_memory|neo4j)$"),
    neo4j_uri: str = "bolt://localhost:7687",
    neo4j_username: str = "neo4j",
    neo4j_password: str = "password",
    neo4j_database: str = "neo4j",
) -> TraceResponse:
    if backend == "neo4j":
        return trace_phenomenon(
            Neo4jConfig(
                uri=neo4j_uri,
                username=neo4j_username,
                password=neo4j_password,
                database=neo4j_database,
            ),
            request.phenomenon,
            request.max_depth,
        )
    return graph.trace(request.phenomenon, request.max_depth)


@app.post("/explain", response_model=ExplainResponse)
def explain(request: ExplainRequest) -> ExplainResponse:
    return explain_risk(graph, request)


@app.post("/workflow", response_model=WorkflowResponse)
def workflow(request: ExplainRequest) -> WorkflowResponse:
    return run_kg_rag_workflow(graph, request)

