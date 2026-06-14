from __future__ import annotations

import pandas as pd

from dqm_data_lab.schemas import GovernanceStageResult


def summarize_rul(frame: pd.DataFrame, unit_column: int | str = 0, cycle_column: int | str = 1) -> tuple[dict[str, object] | None, GovernanceStageResult]:
    if unit_column not in frame.columns or cycle_column not in frame.columns:
        return None, GovernanceStageResult(
            stage="08b_rul",
            status="skipped",
            summary="未检测到 unit/cycle 列，跳过 RUL 简化计算。",
        )

    units = frame[[unit_column, cycle_column]].copy()
    units.columns = ["unit", "cycle"]
    max_cycle = units.groupby("unit")["cycle"].transform("max")
    units["rul"] = max_cycle - units["cycle"]
    sample = units.groupby("cycle")["rul"].mean().reset_index().head(12)

    result: dict[str, object] = {
        "method": "max_cycle_minus_current_cycle",
        "unit_count": int(units["unit"].nunique()),
        "max_cycle": int(units["cycle"].max()),
        "mean_rul": round(float(units["rul"].mean()), 4),
        "curve": [
            {"cycle": int(row["cycle"]), "value": round(float(row["rul"]), 4)}
            for _, row in sample.iterrows()
        ],
    }
    return result, GovernanceStageResult(
        stage="08b_rul",
        summary="完成 C-MAPSS 简化 RUL 摘要计算。",
        metrics=result,
    )

