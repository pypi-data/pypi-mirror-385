from __future__ import annotations

from typing import Any, Dict, Tuple
import pandas as pd

from .client import ConnectorEndpoint
from ..payloads import frame_from_payload, series_from_payload


class BTEndpoint(ConnectorEndpoint):
    """SDK endpoints for Backtester router (/bt).

    Provides helpers to reconstruct DataFrames from payloads.
    """

    def prepare(self, **params) -> Dict[str, Any]:
        """Call /bt/prepare and return raw JSON response."""
        return self.api_client._request("/bt/prepare", params)

    def prepare_frames(self, **params) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, Dict[str, Any]]:
        """Call /bt/prepare and return (prices, metrics, parameters, nav, meta) as pandas objects."""
        resp = self.prepare(**params)
        prices = frame_from_payload(resp.get("prices", {}))
        metrics = frame_from_payload(resp.get("metrics", {}))
        params_df = frame_from_payload(resp.get("parameters", {}))
        nav = series_from_payload(resp.get("nav", {}))
        meta = resp.get("meta", {})
        return prices, metrics, params_df, nav, meta

    def plots(self, **params) -> Dict[str, Any]:
        """Call /bt/plots."""
        return self.api_client._request("/bt/plots", params)

    # Dataset helpers (subset)
    def datasets_list(self) -> Dict[str, Any]:
        return self.api_client.get("/bt/datasets")

    def datasets_delete(self, dataset_id: str) -> Dict[str, Any]:
        return self.api_client.get(f"/bt/datasets/{dataset_id}/delete")

    def sessions_delete(self, session_id: str) -> Dict[str, Any]:
        return self.api_client.get(f"/bt/sessions/{session_id}")
