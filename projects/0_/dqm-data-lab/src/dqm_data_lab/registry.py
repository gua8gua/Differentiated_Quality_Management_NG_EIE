from __future__ import annotations

from pathlib import Path

from .adapters import CmapssAdapter, DatasetAdapter, GenericCsvAdapter, McdmAdapter, SecomAdapter

ADAPTERS: dict[str, DatasetAdapter] = {
    SecomAdapter.name: SecomAdapter(),
    CmapssAdapter.name: CmapssAdapter(),
    McdmAdapter.name: McdmAdapter(),
    GenericCsvAdapter.name: GenericCsvAdapter(),
}


def list_adapters() -> list[str]:
    return sorted(ADAPTERS)


def get_adapter(name: str) -> DatasetAdapter:
    try:
        return ADAPTERS[name]
    except KeyError as exc:
        supported = ", ".join(list_adapters())
        raise ValueError(f"Unsupported dataset type '{name}'. Supported: {supported}") from exc


def infer_adapter(dataset_dir: Path) -> DatasetAdapter:
    if (dataset_dir / "secom.data").exists():
        return get_adapter("secom")
    if (dataset_dir / "FD001" / "train_FD001.txt").exists():
        return get_adapter("cmapss")
    if (dataset_dir / "decision_matrix.csv").exists():
        return get_adapter("mcdm")
    if list(dataset_dir.glob("*.csv")):
        return get_adapter("generic_csv")
    raise ValueError(f"Cannot infer dataset adapter for: {dataset_dir}")

