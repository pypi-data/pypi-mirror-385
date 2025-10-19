from __future__ import annotations

from typing import Any, Dict
import pandas as pd

from .client import ConnectorEndpoint
from ..payloads import frame_from_payload


class ANALYTICSEndpoint(ConnectorEndpoint):
    """SDK endpoints for Analytics router (/analytics)."""

    def hv(self, **params) -> pd.DataFrame:
        resp = self.api_client._request("/analytics/hv", params)
        return frame_from_payload(resp)

    def iv(self, **params) -> Dict[str, Any]:
        return self.api_client._request("/analytics/iv", params)

    def greeks(self, **params) -> Dict[str, Any]:
        return self.api_client._request("/analytics/greeks", params)

    def rolling_plot(self, **params) -> Dict[str, Any]:
        return self.api_client._request("/analytics/rolling_plot", params)
