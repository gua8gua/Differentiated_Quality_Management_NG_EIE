from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_secom(dataset_dir: Path) -> tuple[pd.DataFrame, pd.Series | None]:
    """Load the local SECOM dataset if feature and label files exist."""
    data_file = dataset_dir / "secom.data"
    label_file = dataset_dir / "secom_labels.data"

    if not data_file.exists():
        raise FileNotFoundError(f"SECOM feature file not found: {data_file}")

    features = pd.read_csv(data_file, sep=r"\s+", header=None, na_values=["NaN"])
    labels = None

    if label_file.exists():
        label_df = pd.read_csv(label_file, sep=r"\s+", header=None)
        labels = label_df.iloc[:, 0]

    return features, labels

