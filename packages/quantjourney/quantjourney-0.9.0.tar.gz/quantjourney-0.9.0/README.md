# QuantJourney SDK

Lightweight Python SDK for calling the QuantJourney API server.

Features
- Login/refresh helpers (JWT)
- Lazy connector proxies (eod/fmp/sec/openfigi/fred/imf/cboe/ccxt/...)
- High-level helpers for Backtester/Analytics/Admin/Universe
- DataFrame helpers to reconstruct server payloads

Quick Start
```python
from quantjourney.sdk import QuantJourney

qj = QuantJourney(api_url="http://localhost:8001", tenant_id="jakub")
qj.auth.login(tenant_id="jakub", user_id="alice", password="secret")

prices = qj.eod.get_historical_prices(symbols=["AAPL"], start_date="2024-01-01", end_date="2024-02-01", frequency="1d", exchanges=["US"])  # dict

# Backtester helper returning DataFrames
prices_df, metrics_df, params_df, nav_s, meta = qj.bt.prepare_frames(
  provider={"source":"fmp","granularity":"1d"},
  trading_range={"start":"2024-01-01","end":"2024-02-01"},
  instruments=["AAPL"],
  persist=True,
)
```

Auth via ENV
```bash
export QJ_API=http://localhost:8001
export QJ_TENANT_ID=jakub
export QJ_USER_ID=alice
export QJ_PASSWORD=secret
```
```python
from quantjourney.sdk import QuantJourney
qj = QuantJourney.from_env()
print(qj.admin.routers())
```

Build & Publish
```bash
poetry install
poetry build
# twine upload dist/*
```

