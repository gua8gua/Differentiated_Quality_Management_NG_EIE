from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import pandas as pd

from .io import load_secom
from .schemas import DataAssetProfile, DatasetContext


@dataclass(frozen=True)
class DataBundle:
    context: DatasetContext
    frame: pd.DataFrame
    labels: pd.Series | None
    profile: DataAssetProfile


class DatasetAdapter(Protocol):
    name: str

    def load(self, dataset_dir: Path, context: DatasetContext) -> DataBundle:
        """Load a dataset into the common DQM tabular contract."""


def build_profile(frame: pd.DataFrame, labels: pd.Series | None, metadata: dict | None = None) -> DataAssetProfile:
    numeric_columns = frame.select_dtypes(include="number").columns
    return DataAssetProfile(
        row_count=int(frame.shape[0]),
        column_count=int(frame.shape[1]),
        numeric_column_count=int(len(numeric_columns)),
        missing_rate=float(frame.isna().sum().sum() / frame.size) if frame.size else 0.0,
        label_available=labels is not None,
        metadata=metadata or {},
    )


class SecomAdapter:
    name = "secom"

    def load(self, dataset_dir: Path, context: DatasetContext) -> DataBundle:
        frame, labels = load_secom(dataset_dir)
        resolved_context = context.model_copy(
            update={
                "name": context.name or "SECOM",
                "modality": "tabular",
                "quality_object": context.quality_object if context.quality_object != "generic" else "component",
                "tags": [*context.tags, "semiconductor", "high_dimensional"],
            }
        )
        return DataBundle(resolved_context, frame, labels, build_profile(frame, labels))


class CmapssAdapter:
    name = "cmapss"

    def load(self, dataset_dir: Path, context: DatasetContext) -> DataBundle:
        train_file = dataset_dir / "FD001" / "train_FD001.txt"
        if not train_file.exists():
            raise FileNotFoundError(f"C-MAPSS train file not found: {train_file}")

        frame = pd.read_csv(train_file, sep=r"\s+", header=None)
        resolved_context = context.model_copy(
            update={
                "name": context.name or "C-MAPSS FD001",
                "modality": "timeseries",
                "quality_object": context.quality_object if context.quality_object != "generic" else "component",
                "use_case": context.use_case if context.use_case != "governance" else "risk_prediction",
                "tags": [*context.tags, "rul", "degradation"],
            }
        )
        return DataBundle(
            resolved_context,
            frame,
            labels=None,
            profile=build_profile(frame, None, {"unit_column": 0, "cycle_column": 1}),
        )


class GenericCsvAdapter:
    name = "generic_csv"

    def load(self, dataset_dir: Path, context: DatasetContext) -> DataBundle:
        csv_files = sorted(dataset_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV file found in: {dataset_dir}")

        frame = pd.read_csv(csv_files[0])
        labels = None
        label_candidates = {"label", "target", "pass_fail", "y", "class"}
        for column in frame.columns:
            if str(column).lower() in label_candidates:
                labels = frame.pop(column)
                break

        resolved_context = context.model_copy(
            update={
                "name": context.name or csv_files[0].stem,
                "tags": [*context.tags, "uploaded", "generic_csv"],
            }
        )
        return DataBundle(resolved_context, frame, labels, build_profile(frame, labels))


class McdmAdapter:
    name = "mcdm"

    def load(self, dataset_dir: Path, context: DatasetContext) -> DataBundle:
        matrix_file = dataset_dir / "decision_matrix.csv"
        if not matrix_file.exists():
            raise FileNotFoundError(f"MCDM decision matrix not found: {matrix_file}")

        frame = pd.read_csv(matrix_file)
        resolved_context = context.model_copy(
            update={
                "name": context.name or "Synthetic MCDM",
                "modality": "tabular",
                "quality_object": context.quality_object if context.quality_object != "generic" else "generic",
                "use_case": "quality_evaluation",
                "tags": [*context.tags, "mcdm", "evaluation"],
            }
        )
        return DataBundle(resolved_context, frame, labels=None, profile=build_profile(frame, None))

