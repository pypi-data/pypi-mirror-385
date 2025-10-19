import requests
from dataclasses import dataclass
import os
from typing import Any, Dict, Optional


class APIError(Exception):
    """Exception raised for API errors."""
    pass


@dataclass
class APIResponse:
    """Wrapper for API responses."""
    success: bool
    data: Any
    error: Optional[str] = None
    status_code: int = 200

    def __bool__(self):
        return self.success


class ConnectorEndpoint:
    """Base class for connector endpoints."""

    def __init__(self, api_client: 'APIClient', connector_name: str):
        self.api_client = api_client
        self.connector_name = connector_name

    def _call(self, method: str, **params) -> Any:
        # Friendly param normalization for batch-friendly methods
        try:
            # For selected connectors, map symbol->symbols when server expects plural
            if self.connector_name in {"yf", "eod", "fmp"} and method in {
                "get_historical_prices", "get_intraday_prices", "get_real_time_prices", "get_forex_intraday_prices"
            }:
                if "symbols" not in params and "symbol" in params:
                    sym = params.pop("symbol")
                    params["symbols"] = sym
        except Exception:
            pass

        return self.api_client._request(
            endpoint=f"/{self.connector_name}/{method}",
            payload=params,
        )

    def __getattr__(self, name: str):
        # Dynamic fallback: allow calling any server-exposed method without a stub.
        if name.startswith("get_") or name.startswith("search_"):
            def _dyn_call(**params):
                return self._call(name, **params)
            return _dyn_call
        raise AttributeError(f"{self.__class__.__name__} has no attribute '{name}'")


class APIClient:
    """Low-level HTTP client for API requests."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30, tenant_id: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self._refresh_token: Optional[str] = None
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        if tenant_id:
            self.session.headers.update({"X-Tenant-Id": tenant_id})

    def set_bearer_tokens(self, access_token: str, refresh_token: Optional[str] = None) -> None:
        """Set Authorization bearer tokens and update headers."""
        self.api_key = access_token
        self._refresh_token = refresh_token
        if access_token:
            self.session.headers.update({"Authorization": f"Bearer {access_token}"})
        else:
            self.session.headers.pop("Authorization", None)

    def set_tenant(self, tenant_id: Optional[str]) -> None:
        if tenant_id:
            self.session.headers.update({"X-Tenant-Id": tenant_id})
        else:
            self.session.headers.pop("X-Tenant-Id", None)

    def _maybe_log(self, direction: str, url: str, obj: Any) -> None:
        debug = str(os.getenv("QJ_SDK_DEBUG", "")).lower() in {"1", "true", "yes"}
        if not debug:
            return
        if direction == "->":
            print(f"[QJ SDK] POST {url} payload={obj}")
        else:
            snippet = str(obj)
            if isinstance(snippet, str) and len(snippet) > 1000:
                snippet = snippet[:1000] + "..."
            print(f"[QJ SDK] <- {direction} {snippet}")

    def _handle_json(self, resp: requests.Response) -> Any:
        data = resp.json()
        # If API uses { success, data } wrapper, unwrap; else return raw dict
        if isinstance(data, dict) and "success" in data:
            if data.get("success"):
                return data.get("data")
            msg = data.get("error") or data.get("detail") or f"HTTP {resp.status_code}"
            raise APIError(f"API error: {msg}")
        return data

    def _refresh_and_retry(self, endpoint: str, payload: Dict[str, Any]) -> Any:
        # Attempt refresh if we have a refresh token
        if not self._refresh_token:
            raise APIError("Unauthorized and no refresh token available")
        try:
            r = self.session.post(f"{self.base_url}/auth/refresh", json={"refresh_token": self._refresh_token}, timeout=self.timeout)
            r.raise_for_status()
            doc = r.json()
            access = doc.get("access_token")
            refresh = doc.get("refresh_token") or self._refresh_token
            if not access:
                raise APIError("Refresh did not return access_token")
            self.set_bearer_tokens(access, refresh)
        except Exception as e:
            raise APIError(f"Token refresh failed: {e}")
        # Retry once
        return self._request(endpoint, payload, _retry=False)

    def _request(self, endpoint: str, payload: Dict[str, Any], _retry: bool = True) -> Any:
        url = f"{self.base_url}{endpoint}"
        try:
            self._maybe_log("->", url, payload)
            response = self.session.post(url, json=payload, timeout=self.timeout)
            if response.status_code == 401 and _retry:
                return self._refresh_and_retry(endpoint, payload)
            response.raise_for_status()
            data = self._handle_json(response)
            self._maybe_log(str(response.status_code), url, data)
            return data
        except requests.exceptions.RequestException as e:
            raise APIError(f"HTTP request failed: {str(e)}")
        except ValueError as e:
            raise APIError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}")

    def health_check(self) -> Dict[str, Any]:
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, _retry: bool = True) -> Any:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params or {}, timeout=self.timeout)
            if response.status_code == 401 and _retry:
                # Try refresh then retry
                if not self._refresh_token:
                    response.raise_for_status()
                self._refresh_and_retry("/auth/refresh_passthrough", {})  # just to trigger refresh
                return self.get(endpoint, params=params, _retry=False)
            response.raise_for_status()
            return self._handle_json(response)
        except requests.exceptions.RequestException as e:
            raise APIError(f"HTTP request failed: {str(e)}")
        except ValueError as e:
            raise APIError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}")


__all__ = ["APIClient", "APIError", "APIResponse", "ConnectorEndpoint"]
