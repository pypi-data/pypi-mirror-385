from __future__ import annotations

from typing import Any, Dict

from ..client import ConnectorEndpoint


class UNIVERSEEndpoint(ConnectorEndpoint):
    """SDK endpoints for Universe router (/universe)."""

    def preview(self, **spec) -> Dict[str, Any]:
        return self.api_client._request("/universe/preview", spec)

    def build(self, **spec) -> Dict[str, Any]:
        return self.api_client._request("/universe/build", spec)

    def list(self) -> Dict[str, Any]:
        return self.api_client.get("/universe/list")

    def get(self, universe_id: str) -> Dict[str, Any]:
        return self.api_client.get(f"/universe/{universe_id}")

