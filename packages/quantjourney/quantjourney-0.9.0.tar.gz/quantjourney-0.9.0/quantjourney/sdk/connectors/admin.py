from __future__ import annotations

from typing import Any, Dict

from ..client import ConnectorEndpoint


class ADMINEndpoint(ConnectorEndpoint):
    """SDK endpoints for Admin router (/admin)."""

    def routers(self) -> Dict[str, Any]:
        return self.api_client.get("/admin/routers")

    def logging(self) -> Dict[str, Any]:
        return self.api_client.get("/admin/logging")

    def health_summary(self) -> Dict[str, Any]:
        return self.api_client.get("/admin/health/summary")

