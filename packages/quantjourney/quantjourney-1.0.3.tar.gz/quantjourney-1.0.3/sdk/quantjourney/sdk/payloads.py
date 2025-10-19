from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd


def frame_from_payload(payload: Dict[str, Any]) -> pd.DataFrame:
    """Reconstruct a pandas DataFrame from a FramePayload {columns,index,data}.

    Expected columns: list of { instrument, field } dicts (or plain strings).
    Index: list of ISO8601 timestamps (assumed UTC) or scalar values.
    Data: 2D array-like matching index x columns.
    """
    cols_meta = payload.get("columns") or []
    idx_vals: List[Any] = payload.get("index") or []
    data: List[List[Any]] = payload.get("data") or []

    # Derive column tuples
    tuples: List[Any] = []
    names: Optional[List[str]] = None
    if cols_meta and isinstance(cols_meta[0], dict) and "instrument" in cols_meta[0]:
        tuples = [(c.get("instrument"), c.get("field")) for c in cols_meta]
        names = ["instrument", "field"]
        columns = pd.MultiIndex.from_tuples(tuples, names=names)
    else:
        # Fallback: simple columns
        columns = [c.get("name") if isinstance(c, dict) else c for c in cols_meta]

    # Parse index (prefer datetime with UTC)
    try:
        index = pd.to_datetime(idx_vals, utc=True)
    except Exception:
        index = pd.Index(idx_vals)

    df = pd.DataFrame(data, index=index, columns=columns)
    return df


def series_from_payload(payload: Dict[str, Any]) -> pd.Series:
    """Reconstruct a pandas Series from a SeriesPayload {index, values, name}.
    """
    idx_vals = payload.get("index") or []
    values = payload.get("values") or payload.get("data") or []
    name = payload.get("name")
    try:
        index = pd.to_datetime(idx_vals, utc=True)
    except Exception:
        index = pd.Index(idx_vals)
    s = pd.Series(values, index=index, name=name)
    return s


__all__ = ["frame_from_payload", "series_from_payload"]

