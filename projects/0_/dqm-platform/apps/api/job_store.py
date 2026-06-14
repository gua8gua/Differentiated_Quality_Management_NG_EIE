from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class UploadRecord:
    upload_id: str
    filename: str
    path: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class JobRecord:
    job_id: str
    upload_id: str
    status: str = "pending"
    events: list[dict[str, Any]] = field(default_factory=list)
    dashboard: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=datetime.now)


class JobStore:
    def __init__(self) -> None:
        self.uploads: dict[str, UploadRecord] = {}
        self.jobs: dict[str, JobRecord] = {}

    def create_upload(self, filename: str, path: str) -> UploadRecord:
        upload_id = uuid.uuid4().hex[:12]
        record = UploadRecord(upload_id=upload_id, filename=filename, path=path)
        self.uploads[upload_id] = record
        return record

    def get_upload(self, upload_id: str) -> UploadRecord:
        if upload_id not in self.uploads:
            raise KeyError(upload_id)
        return self.uploads[upload_id]

    def create_job(self, upload_id: str) -> JobRecord:
        job_id = uuid.uuid4().hex[:12]
        record = JobRecord(job_id=job_id, upload_id=upload_id)
        self.jobs[job_id] = record
        return record

    def get_job(self, job_id: str) -> JobRecord:
        if job_id not in self.jobs:
            raise KeyError(job_id)
        return self.jobs[job_id]

    def append_event(self, job_id: str, event: dict[str, Any]) -> None:
        job = self.get_job(job_id)
        job.events.append(event)

    def set_status(self, job_id: str, status: str, *, dashboard: dict[str, Any] | None = None, error: str | None = None) -> None:
        job = self.get_job(job_id)
        job.status = status
        if dashboard is not None:
            job.dashboard = dashboard
        if error is not None:
            job.error = error


job_store = JobStore()
