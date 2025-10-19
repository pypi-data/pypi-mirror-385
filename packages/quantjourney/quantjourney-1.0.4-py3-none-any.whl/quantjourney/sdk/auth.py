from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

from .client import APIClient, APIError


@dataclass
class Tokens:
    access_token: str
    refresh_token: Optional[str]
    expires_in: Optional[int] = None


class AuthClient:
    """Auth helper for QuantJourney SDK.

    Provides login/refresh/whoami and wires tokens into the underlying APIClient.
    """

    def __init__(self, api_client: APIClient):
        self._api = api_client

    def login(self, tenant_id: str, user_id: str, password: str) -> Tokens:
        payload = {"tenant_id": tenant_id, "user_id": user_id, "password": password}
        doc = self._api._request(endpoint="/auth/login", payload=payload)
        # /auth/login returns a structured object (not wrapped in success)
        access = doc.get("access_token")
        refresh = doc.get("refresh_token")
        if not access:
            raise APIError("Login did not return access_token")
        self._api.set_bearer_tokens(access, refresh)
        # If tenant header was not set explicitly, derive from token claims via whoami
        try:
            w = self.whoami()
            tid = w.get("tenant_id")
            if tid:
                self._api.set_tenant(tid)
        except Exception:
            pass
        return Tokens(access_token=access, refresh_token=refresh, expires_in=doc.get("expires_in"))

    def refresh(self) -> Tokens:
        if not getattr(self._api, "_refresh_token", None):
            raise APIError("No refresh token available")
        doc = self._api._request(endpoint="/auth/refresh", payload={"refresh_token": self._api._refresh_token})
        access = doc.get("access_token")
        refresh = doc.get("refresh_token") or self._api._refresh_token
        if not access:
            raise APIError("Refresh did not return access_token")
        self._api.set_bearer_tokens(access, refresh)
        return Tokens(access_token=access, refresh_token=refresh, expires_in=doc.get("expires_in"))

    def whoami(self) -> Dict[str, Any]:
        return self._api.get("/auth/whoami")

