from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MOCK_DATA = ROOT / "mock-data" / "dashboard.json"
UPLOADS = ROOT / "uploads"


def load_dashboard() -> dict[str, Any]:
    return json.loads(MOCK_DATA.read_text(encoding="utf-8"))


def section(name: str) -> Any:
    data = load_dashboard()
    if name not in data:
        raise KeyError(name)
    return data[name]


def platform_workflow() -> list[dict[str, str]]:
    return [
        {"stage": "01_data_governance", "project": "dqm-data-lab", "output": "data_quality_report.json"},
        {"stage": "02_kg_trace", "project": "dqm-kg-rag", "output": "trace / explain API"},
        {"stage": "03_risk_mock", "project": "dqm-platform", "output": "riskPrediction mock"},
        {"stage": "04_agent_mock", "project": "dqm-platform", "output": "agents mock"},
        {"stage": "05_dashboard", "project": "dqm-platform", "output": "web dashboard"},
    ]


def ensure_upload_dir() -> Path:
    UPLOADS.mkdir(parents=True, exist_ok=True)
    return UPLOADS
