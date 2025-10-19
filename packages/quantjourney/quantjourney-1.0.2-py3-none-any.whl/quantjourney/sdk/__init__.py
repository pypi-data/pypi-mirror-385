"""
QuantJourney SDK (package)

Provides `QuantJourneyAPI` client and per-connector endpoint classes under
`quantjourney.sdk.connectors`.

Import path remains stable for users/tests:
    from quantjourney.sdk import QuantJourneyAPI
"""

import os
from .client import APIClient, APIError  # re-export for convenience
from .client import ConnectorEndpoint  # for custom extensions
from .registry import SDK_CONNECTORS
from .auth import AuthClient

from importlib import import_module
from typing import Any, Optional, Dict


class DomainProxy:
    """Dynamic domain proxy allowing qj.<domain>[.<subdomain>].<method>(...) calls.

    Examples:
        qj.equities.get_pricing(symbol="AAPL")
        qj.equities.fundamentals.get_income_statement(symbol="AAPL")
    """

    def __init__(self, api_client, domain_path: str):
        self._api_client = api_client
        self._domain_path = domain_path  # e.g., "equities" or "equities.fundamentals"

    def __getattr__(self, name: str):
        # If attribute looks like a callable method (get_/search_/list_/fetch_),
        # return a function that posts to /d/<domain_path>.<name>. Otherwise, treat
        # as subdomain and return another DomainProxy.
        if name.startswith(("get_", "search_", "list_", "fetch_")):
            route = f"{self._domain_path}.{name}"

            def _call(**payload):
                return self._api_client._request(endpoint=f"/d/{route}", payload=payload)

            return _call
        # subdomain chaining
        return DomainProxy(self._api_client, f"{self._domain_path}.{name}")


class QuantJourneyAPI:
    """QuantJourney HTTP SDK Client (aggregator with lazy connector loading)."""

    def __init__(self, api_url: str = "http://localhost:8001",
                 api_key: Optional[str] = None,
                 token: Optional[str] = None,
                 timeout: int = 30,
                 tenant_id: Optional[str] = None):
        # token is an alias for api_key for friendlier ergonomics
        if api_key is None and token is not None:
            api_key = token
        self._client = APIClient(base_url=api_url, api_key=api_key, timeout=timeout, tenant_id=tenant_id)
        self._endpoints: Dict[str, Any] = {}
        self._auth = AuthClient(self._client)

    @classmethod
    def from_env(cls) -> "QuantJourneyAPI":
        api = os.getenv("QJ_API", "http://localhost:8001").rstrip("/")
        key = os.getenv("QJ_API_KEY") or os.getenv("QJ_ACCESS_TOKEN") or os.getenv("QJ_TOKEN")
        tid = os.getenv("QJ_TENANT_ID")
        user = os.getenv("QJ_USER_ID")
        pwd = os.getenv("QJ_PASSWORD")
        inst = cls(api_url=api, api_key=key, tenant_id=tid)
        # If no key but have creds, login
        if not key and tid and user and pwd:
            inst.auth.login(tenant_id=tid, user_id=user, password=pwd)
        return inst

    # --- Lazy properties for common connectors used in tests ---
    @property
    def eod(self):
        return self._get_endpoint("eod")

    @property
    def fmp(self):
        return self._get_endpoint("fmp")

    @property
    def fred(self):
        return self._get_endpoint("fred")

    @property
    def yf(self):
        return self._get_endpoint("yf")

    @property
    def openfigi(self):
        return self._get_endpoint("openfigi")

    @property
    def sec(self):
        return self._get_endpoint("sec")

    @property
    def cboe(self):
        return self._get_endpoint("cboe")

    @property
    def ccxt(self):
        return self._get_endpoint("ccxt")

    @property
    def imf(self):
        return self._get_endpoint("imf")

    @property
    def cnnf(self):
        return self._get_endpoint("cnnf")

    @property
    def cftc(self):
        return self._get_endpoint("cftc")

    @property
    def ff(self):
        return self._get_endpoint("ff")

    @property
    def oecd(self):
        return self._get_endpoint("oecd")

    @property
    def multpl(self):
        return self._get_endpoint("multpl")

    @property
    def insider(self):
        return self._get_endpoint("insider")

    @property
    def ratios(self):
        # Simple wrapper over /ratios endpoints (available + series)
        return _RatiosClient(self._client)

    @property
    def bt(self):
        return self._get_endpoint("bt")

    @property
    def analytics(self):
        return self._get_endpoint("analytics")

    def admin(self):
        return self._get_endpoint("admin")

    @property
    def universe(self):
        return self._get_endpoint("universe")

    # --- Utilities ---
    def _get_endpoint(self, key: str):
        ep = self._endpoints.get(key)
        if ep is not None:
            return ep
        spec = SDK_CONNECTORS.get(key)
        if not spec:
            raise AttributeError(f"Connector '{key}' not registered in SDK")
        module_path, class_name = spec.split(":", 1)
        mod = import_module(module_path)
        cls = getattr(mod, class_name)
        inst = cls(self._client, key)
        self._endpoints[key] = inst
        return inst

    def health(self) -> Dict[str, Any]:
        return self._client.health_check()

    def __repr__(self) -> str:
        return f"QuantJourneyAPI(url={self._client.base_url})"

    # Domain dynamic access (fallback): any unknown attribute becomes a domain proxy.
    def __getattr__(self, name: str):
        # Avoid catching dunder attrs
        if name.startswith("__"):
            raise AttributeError(name)
        return DomainProxy(self._client, name)

    # Auth facade
    @property
    def auth(self) -> AuthClient:
        return self._auth

__all__ = ["QuantJourneyAPI", "APIClient", "APIError", "ConnectorEndpoint"]


# Backward/forward-compatible alias: QuantJourney
class QuantJourney(QuantJourneyAPI):
    """Alias for QuantJourneyAPI for simpler imports/naming."""
    pass


class _RatiosClient:
    def __init__(self, api_client: APIClient):
        self._api = api_client

    def available(self, source: str = "eod"):
        return self._api._request(endpoint=f"/ratios/available?source={source}", payload={})

    def series(self, ratio: str, ticker: str, exchange: str = "US", source: str = "eod",
               start: str = None, end: str = None, compute: bool = False, period: str = "q"):
        # build query string
        params = [f"ratio={ratio}", f"ticker={ticker}", f"exchange={exchange}", f"source={source}", f"period={period}", f"compute={'true' if compute else 'false'}"]
        if start:
            params.append(f"start={start}")
        if end:
            params.append(f"end={end}")
        qs = "&".join(params)
        return self._api._request(endpoint=f"/ratios/series?{qs}", payload={})

__all__.append("QuantJourney")
