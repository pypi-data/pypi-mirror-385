# QuantJourney SDK (HTTP Client)

Lightweight, modular Python SDK for calling the QuantJourney FastAPI server.

Features
- Lazy connector attachment (e.g., `qj.eod` is created on first access)
- Dynamic method fallback: any `get_*` / `search_*` method name is accepted and posted to the server (no stub required)
- Registry driven by YAML: `quantjourney/sdk/routers.yaml`
- Backward-compatible alias `QuantJourney` for `QuantJourneyAPI`

Quick start
```python
from quantjourney.sdk import QuantJourney

qj = QuantJourney(api_url="http://localhost:8001", tenant_id="jakub")
data = qj.eod.get_historical_prices(symbols=["AAPL"], start_date="2025-01-01", end_date="2025-02-01", frequency="1d", exchanges=["US"])  # dict
```

Configuration
- `quantjourney/sdk/routers.yaml` controls which connectors the SDK exposes.
  - Example:
    ```yaml
    connectors:
      eod: true
      fmp: true
      fred: true
      yf: true
    ```

Notes
- The SDK is provider-agnostic. Domain APIs (e.g., `equities.get_pricing`) will be layered on top later.
- For wide coverage, tests use connector analysis JSON to auto-fill required params.
- Optional auth/tenant headers: pass `api_key` (Bearer) and/or `tenant_id` (X-Tenant-Id) to match server auth mode.

Auth helpers
- Use `qj.auth.login(tenant_id, user_id, password)` to obtain tokens from `/auth/login`.
- Tokens are stored in the client and auto-refreshed on 401 via `/auth/refresh` (if refresh token present).
- You can also construct from env: `QuantJourney.from_env()` reads `QJ_API`, `QJ_API_KEY` (or `QJ_ACCESS_TOKEN`), `QJ_TENANT_ID`, and optionally `QJ_USER_ID`/`QJ_PASSWORD` to login.

Higher-level clients
- `qj.bt.prepare_frames(...)` returns `(prices, metrics, parameters, nav, meta)` as pandas objects.
- `qj.analytics.hv(dataset_id=...)` returns a pandas DataFrame reconstructed from payload.
