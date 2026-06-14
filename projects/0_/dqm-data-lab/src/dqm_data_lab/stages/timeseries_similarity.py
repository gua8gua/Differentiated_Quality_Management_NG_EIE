from __future__ import annotations

import numpy as np
import pandas as pd

from dqm_data_lab.schemas import GovernanceStageResult


def _dtw_distance(left: np.ndarray, right: np.ndarray) -> float:
    rows, cols = len(left), len(right)
    table = np.full((rows + 1, cols + 1), np.inf)
    table[0, 0] = 0.0
    for row in range(1, rows + 1):
        for col in range(1, cols + 1):
            cost = abs(left[row - 1] - right[col - 1])
            table[row, col] = cost + min(table[row - 1, col], table[row, col - 1], table[row - 1, col - 1])
    return float(table[rows, cols])


def summarize_similarity_and_trend(
    frame: pd.DataFrame,
    feature_names: list[str],
    window: int = 24,
) -> tuple[dict[str, object], dict[str, object], GovernanceStageResult]:
    selected = [feature for feature in feature_names if feature in frame.columns]
    if not selected:
        selected = [str(frame.columns[0])]

    series = pd.to_numeric(frame[selected[0]], errors="coerce").dropna().reset_index(drop=True)
    if len(series) < window * 2:
        window = max(4, len(series) // 2)

    first = series.iloc[:window].to_numpy(dtype=float)
    segments = []
    for index, start in enumerate(range(window, min(len(series) - window + 1, window * 6), window)):
        current = series.iloc[start : start + window].to_numpy(dtype=float)
        distance = _dtw_distance(first, current)
        segments.append(
            {
                "caseId": f"window-{index + 1:03d}",
                "start": int(start),
                "distance": round(distance, 4),
                "similarity": round(float(1 / (1 + distance)), 4),
                "label": "相似工艺片段",
            }
        )
    segments = sorted(segments, key=lambda item: item["distance"])[:3]

    rolling = series.rolling(window=min(window, max(2, len(series))), min_periods=1).mean()
    trend = {
        "method": "rolling_mean_trend",
        "feature": selected[0],
        "start": round(float(rolling.iloc[0]), 4),
        "end": round(float(rolling.iloc[-1]), 4),
        "delta": round(float(rolling.iloc[-1] - rolling.iloc[0]), 4),
    }
    similarity = {"method": "dtw_window_distance", "feature": selected[0], "segments": segments}
    return similarity, trend, GovernanceStageResult(
        stage="08c_similarity_trend",
        summary="完成 DTW 相似片段检索与滚动趋势摘要。",
        metrics={"similar_segment_count": len(segments), "trend_delta": trend["delta"]},
    )

