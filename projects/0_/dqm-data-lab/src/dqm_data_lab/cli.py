from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_dataset_pipeline
from .registry import list_adapters
from .schemas import DatasetContext


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run DQM data governance experiments.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run the extensible governance pipeline.")
    run.add_argument("--dataset", type=Path, required=True, help="Path to a supported dataset directory")
    run.add_argument(
        "--dataset-type",
        default="auto",
        choices=["auto", *list_adapters()],
        help="Dataset adapter type",
    )
    run.add_argument("--out", type=Path, default=Path("reports"), help="Output report directory")
    run.add_argument("--name", default="数据集", help="Dataset display name")
    run.add_argument(
        "--modality",
        default="tabular",
        choices=["tabular", "timeseries", "image", "text", "audio", "multimodal"],
        help="Data modality",
    )
    run.add_argument(
        "--quality-object",
        default="generic",
        choices=["whole_equipment", "software", "component", "process", "generic"],
        help="Quality object type",
    )
    run.add_argument(
        "--use-case",
        default="governance",
        choices=[
            "governance",
            "quality_evaluation",
            "anomaly_detection",
            "risk_prediction",
            "rag_explanation",
        ],
        help="Primary data use case",
    )
    run.add_argument(
        "--standards",
        default="ISO8000,project_custom",
        help="Comma-separated standards, e.g. ISO8000,GB_T_34960_5",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "run":
        context = DatasetContext(
            name=args.name,
            modality=args.modality,
            quality_object=args.quality_object,
            use_case=args.use_case,
            standards=[item.strip() for item in args.standards.split(",") if item.strip()],
        )
        report, risk = run_dataset_pipeline(args.dataset, args.out, context, args.dataset_type)
        print(f"quality_score={report.quality_score} risk_level={risk.risk_level}")


if __name__ == "__main__":
    main()

