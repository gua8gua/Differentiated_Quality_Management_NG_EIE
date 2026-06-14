from __future__ import annotations

import asyncio
import json
import os
import random
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator

ROOT = Path(__file__).resolve().parents[5]
SELF = Path(__file__).resolve().parents[3]
DATA_LAB_SRC = SELF / "dqm-data-lab" / "src"
KG_RAG_SRC = SELF / "dqm-kg-rag" / "src"

for path in (str(SELF), str(DATA_LAB_SRC), str(KG_RAG_SRC)):
    if path not in sys.path:
        sys.path.insert(0, path)

from dqm_kg_rag.store import default_graph  # noqa: E402

from job_store import job_store  # noqa: E402
from orchestrator import run_analysis_job  # noqa: E402
from services import load_dashboard  # noqa: E402


class ChatSession:
    def __init__(self) -> None:
        self.session_id = uuid.uuid4().hex[:12]
        self.messages: list[dict[str, Any]] = []
        self.logs: list[dict[str, Any]] = []
        self.upload_id: str | None = None
        self.job_id: str | None = None


class ChatStore:
    def __init__(self) -> None:
        self.sessions: dict[str, ChatSession] = {}

    def get_or_create(self, session_id: str | None = None) -> ChatSession:
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        session = ChatSession()
        self.sessions[session.session_id] = session
        return session


chat_store = ChatStore()


def _append_log(session: ChatSession, stage: str, summary: str, **payload: Any) -> dict[str, Any]:
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "stage": stage,
        "summary": summary,
        **payload,
    }
    session.logs.append(record)
    return record


def _build_mock_reply(message: str, dashboard: dict[str, Any] | None) -> str:
    lower = message.lower()
    if any(word in message for word in ("风险", "risk")):
        risk = (dashboard or {}).get("riskPrediction", {})
        return (
            f"当前风险等级为「{risk.get('riskLevel', '未知')}」，"
            f"主要现象是「{risk.get('phenomenon', '待分析')}」。"
            "建议结合图谱根因路径执行差异化管控。"
        )
    if any(word in message for word in ("根因", "追溯", "图谱")):
        trace = (dashboard or {}).get("graphTrace", {})
        paths = trace.get("paths") or []
        path_text = " → ".join(paths[0]) if paths else "暂无路径"
        return f"图谱追溯摘要：{trace.get('summary', '')}\n推荐路径：{path_text}"
    if any(word in message for word in ("质量", "治理", "评分")):
        dq = (dashboard or {}).get("dataQuality", {})
        return (
            f"数据质量评分 {dq.get('qualityScore', 'N/A')}，"
            f"缺失率 {dq.get('missingRate', 'N/A')}，"
            f"异常率 {dq.get('anomalyRate', 'N/A')}。"
        )
    if any(word in lower for word in ("agent", "智能体")):
        agents = (dashboard or {}).get("agentDecisions") or []
        if not agents:
            return "尚未生成智能体决策，请先上传数据并完成分析。"
        lines = [f"- {item['agent']}：{item['recommendation']}（置信度 {item['confidence']}）" for item in agents]
        return "三类智能体当前建议：\n" + "\n".join(lines)
    return (
        "我是 DQM 质量管控 Agent。你可以询问：数据质量评分、风险等级、图谱根因、智能体建议，"
        "或发送「分析上传文件」触发全流程。"
    )


def _try_langgraph_reply(message: str, dashboard: dict[str, Any] | None) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_openai import ChatOpenAI
        from langgraph.graph import END, START, StateGraph
        from typing_extensions import TypedDict

        class AgentState(TypedDict):
            answer: str

        context_blob = json.dumps(dashboard or {}, ensure_ascii=False)[:6000]

        def reason(state: AgentState) -> AgentState:
            llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.2)
            response = llm.invoke(
                [
                    SystemMessage(
                        content=(
                            "你是电子信息装备差异化质量管控助手。"
                            "结合给定 dashboard JSON 回答用户问题，输出简洁中文。"
                        )
                    ),
                    SystemMessage(content=f"当前分析上下文：{context_blob}"),
                    HumanMessage(content=message),
                ]
            )
            return {"answer": str(response.content)}

        graph = StateGraph(AgentState)
        graph.add_node("reason", reason)
        graph.add_edge(START, "reason")
        graph.add_edge("reason", END)
        app = graph.compile()
        result = app.invoke({"answer": ""})
        return result["answer"]
    except Exception:
        return None


async def stream_agent_response(session_id: str, message: str, upload_id: str | None = None) -> AsyncIterator[str]:
    session = chat_store.get_or_create(session_id)
    if upload_id:
        session.upload_id = upload_id

    session.messages.append(
        {"role": "user", "content": message, "timestamp": datetime.now().isoformat(timespec="seconds")}
    )
    yield _sse("log", _append_log(session, "user_input", f"收到用户消息：{message}"))

    trigger_analysis = any(word in message for word in ("分析", "上传", "运行", "全流程"))
    dashboard = None

    if trigger_analysis and session.upload_id:
        upload = job_store.get_upload(session.upload_id)
        job = job_store.create_job(session.upload_id)
        session.job_id = job.job_id
        yield _sse("log", _append_log(session, "analysis_start", "开始执行上传文件的全流程分析。"))

        def on_event(record: dict[str, Any]) -> None:
            session.logs.append(record)

        loop = asyncio.get_event_loop()
        dashboard = await loop.run_in_executor(
            None,
            lambda: run_analysis_job(
                job.job_id,
                Path(upload.path),
                {
                    "name": Path(upload.filename).stem,
                    "modality": "tabular",
                    "quality_object": "generic",
                    "use_case": "governance",
                },
                dataset_type="auto",
                on_event=on_event,
            ),
        )
        for record in job_store.get_job(job.job_id).events:
            yield _sse("log", record)
    else:
        try:
            dashboard = load_dashboard()
        except Exception:
            dashboard = None

    yield _sse("log", _append_log(session, "agent_thinking", "Agent 正在生成回复…", project="langgraph"))
    reply = _try_langgraph_reply(message, dashboard) or _build_mock_reply(message, dashboard)

    session.messages.append(
        {
            "role": "assistant",
            "content": reply,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "stage": "agent_reply",
        }
    )
    yield _sse("message", {"role": "assistant", "content": reply, "session_id": session.session_id})
    yield _sse("log", _append_log(session, "agent_reply", "Agent 回复已生成。", project="langgraph"))
    yield _sse("done", {"session_id": session.session_id})


async def stream_realtime_metrics() -> AsyncIterator[str]:
    tick = 0
    while tick < 120:
        tick += 1
        payload = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "qualityScore": round(88 + random.uniform(-2, 4), 2),
            "anomalyRate": round(0.05 + random.uniform(-0.01, 0.02), 4),
            "riskLevelIndex": round(0.45 + random.uniform(-0.08, 0.08), 3),
            "sensorValue": round(100 + random.uniform(-8, 8), 2),
            "tick": tick,
        }
        yield _sse("metric", payload)
        await asyncio.sleep(1)


async def stream_job_events(job_id: str) -> AsyncIterator[str]:
    seen = 0
    while True:
        job = job_store.get_job(job_id)
        while seen < len(job.events):
            yield _sse("log", job.events[seen])
            seen += 1
        if job.status in {"completed", "failed"}:
            yield _sse("done", {"status": job.status, "dashboard": job.dashboard, "error": job.error})
            break
        await asyncio.sleep(0.5)


def get_graph_data() -> dict[str, Any]:
    return default_graph().as_elements()


def trace_graph(phenomenon: str, max_depth: int = 3) -> dict[str, Any]:
    trace = default_graph().trace(phenomenon, max_depth)
    return trace.model_dump()


def _sse(event: str, payload: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
