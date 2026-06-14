from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent_service import (
    chat_store,
    get_graph_data,
    stream_agent_response,
    stream_job_events,
    stream_realtime_metrics,
    trace_graph,
)
from job_store import job_store
from orchestrator import metadata_options, run_analysis_job
from schemas import ChatRequest, TraceRequestPayload
from services import ensure_upload_dir, load_dashboard, platform_workflow, section

app = FastAPI(title="DQM Platform API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "dqm-platform-api"}


@app.get("/dashboard")
def dashboard() -> dict[str, Any]:
    return load_dashboard()


@app.get("/dashboard/{section_name}")
def dashboard_section(section_name: str) -> Any:
    try:
        return section(section_name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown section: {section_name}") from exc


@app.get("/workflow")
def workflow() -> list[dict[str, str]]:
    return platform_workflow()


@app.get("/metadata/options")
def get_metadata_options() -> dict[str, list[str]]:
    return metadata_options()


@app.post("/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)) -> dict[str, str]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    upload_root = ensure_upload_dir()
    upload_id_dir = upload_root / "pending"
    upload_id_dir.mkdir(parents=True, exist_ok=True)

    temp_path = upload_id_dir / file.filename
    content = await file.read()
    temp_path.write_bytes(content)

    record = job_store.create_upload(file.filename, str(temp_path.parent))
    final_dir = upload_root / record.upload_id
    final_dir.mkdir(parents=True, exist_ok=True)
    final_path = final_dir / file.filename
    shutil.move(str(temp_path), str(final_path))
    record.path = str(final_dir)

    return {
        "upload_id": record.upload_id,
        "filename": record.filename,
        "message": "文件上传成功，请选择数据上下文后发起分析。",
    }


class AnalyzeBody(BaseModel):
    upload_id: str
    context: dict[str, Any]
    dataset_type: str = "auto"


def _run_job(job_id: str, upload_id: str, context: dict[str, Any], dataset_type: str) -> None:
    try:
        upload = job_store.get_upload(upload_id)
        run_analysis_job(job_id, Path(upload.path), context, dataset_type=dataset_type)
    except Exception as exc:
        job_store.set_status(job_id, "failed", error=str(exc))
        job_store.append_event(
            job_id,
            {"event": "job_failed", "stage": "error", "summary": str(exc), "timestamp": ""},
        )


@app.post("/datasets/analyze")
def analyze_dataset(body: AnalyzeBody, background_tasks: BackgroundTasks) -> dict[str, str]:
    try:
        job_store.get_upload(body.upload_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Upload not found") from exc

    job = job_store.create_job(body.upload_id)
    background_tasks.add_task(_run_job, job.job_id, body.upload_id, body.context, body.dataset_type)
    return {"job_id": job.job_id, "status": "running"}


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    try:
        job = job_store.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return {
        "job_id": job.job_id,
        "upload_id": job.upload_id,
        "status": job.status,
        "events": job.events,
        "dashboard": job.dashboard,
        "error": job.error,
    }


@app.get("/jobs/{job_id}/stream")
async def stream_job(job_id: str) -> StreamingResponse:
    try:
        job_store.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return StreamingResponse(stream_job_events(job_id), media_type="text/event-stream")


@app.get("/graph")
def graph() -> dict[str, Any]:
    return get_graph_data()


@app.post("/graph/trace")
def graph_trace(request: TraceRequestPayload) -> dict[str, Any]:
    return trace_graph(request.phenomenon, request.max_depth)


@app.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    session = chat_store.get_or_create(request.session_id)
    if request.upload_id:
        session.upload_id = request.upload_id
    generator = stream_agent_response(session.session_id, request.message, request.upload_id)
    return StreamingResponse(generator, media_type="text/event-stream")


@app.get("/chat/{session_id}/history")
def chat_history(session_id: str) -> dict[str, Any]:
    if session_id not in chat_store.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    session = chat_store.sessions[session_id]
    return {
        "session_id": session.session_id,
        "messages": session.messages,
        "logs": session.logs,
        "upload_id": session.upload_id,
        "job_id": session.job_id,
    }


@app.get("/realtime/stream")
async def realtime_stream() -> StreamingResponse:
    return StreamingResponse(stream_realtime_metrics(), media_type="text/event-stream")
