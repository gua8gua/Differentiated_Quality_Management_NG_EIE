from __future__ import annotations

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


def clean_numeric_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Median-impute and z-score normalize numeric quality data."""
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()

    imputed = imputer.fit_transform(frame)
    scaled = scaler.fit_transform(imputed)
    return pd.DataFrame(scaled, columns=frame.columns)


def missing_rate(frame: pd.DataFrame) -> float:
    return float(frame.isna().sum().sum() / frame.size)

