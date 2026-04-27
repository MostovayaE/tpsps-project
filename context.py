from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import pandas as pd


@dataclass
class PipelineContext:
    df: pd.DataFrame
    freq: Optional[str]
    time_col: str
    value_col: str
    mae: Optional[float] = None
    mape: Optional[float] = None
    rmse: Optional[float] = None
    model_name: Optional[str] = None
    test_actual: Optional[pd.Series] = None
    test_predicted: Optional[pd.Series] = None
