# Admin SDK Split

This repository contains two SDK surfaces:
- Public SDK (`quantjourney.sdk`) – published to PyPI. Includes the Auth helper and all end‑user data connectors.
- Admin SDK (`quantjourney.sdkadmin`) – private namespace packaged from this repo by scripts; exposes operational Admin routes.

Notes
- Auth remains in the public SDK: `qj.auth.login`, `qj.auth.refresh`, `qj.auth.whoami` call `/auth/*`.
- Admin endpoints are not shipped in the public package; they are provided via the private Admin SDK. In this source tree you will still see the Admin connector for local/dev, but it is stripped out at publish time.

Public SDK (here)
- Auth endpoints (available in `quantjourney.sdk`):
  - POST `/auth/login`
  - POST `/auth/refresh`
  - GET `/auth/whoami`

Private Admin SDK (sdkadmin)
- Admin router endpoints (exposed via `quantjourney.sdkadmin.QuantJourneyAdmin.admin`):
  - GET `/admin/routers`
  - GET `/admin/tenants`
  - GET `/admin/tenants/{tenant_id}`
  - GET `/admin/logging`
  - GET `/admin/health/summary`
  - GET `/admin/connectors/available`
  - GET `/admin/secrets` (redacted listing)
  - GET `/admin/secrets/effective` (presence + redacted preview)
  - POST `/admin/secrets` (upsert)
  - POST `/admin/secrets/delete` (delete)

Implementation details
- Source of truth (this repo):
  - Admin connector class: `quantjourney/sdk/connectors/admin.py` (local/dev only)
  - Auth helper: `quantjourney/sdk/auth.py`
  - Client: `quantjourney/sdk/client.py`
- Packaging split is enforced by `scripts/sdk/make_sdk.sh`:
  - Public export removes Admin from the SDK (drops `connectors/admin.py`, registry mapping, `qj.admin` property, and README references).
  - A private Admin package is scaffolded under `sdkadmin/` with `QuantJourneyAdmin` that reuses the public client and auth.

Usage examples
- Public SDK:
  ```python
  from quantjourney.sdk import QuantJourney
  qj = QuantJourney(api_url="http://localhost:8001", tenant_id="jakub")
  qj.auth.login(tenant_id="jakub", user_id="admin", password="...")
  print(qj.auth.whoami())
  ```
- Admin SDK (private):
  ```python
  from quantjourney.sdkadmin import QuantJourneyAdmin
  qa = QuantJourneyAdmin(api_url="http://localhost:8001", token="<ACCESS_TOKEN>")
  print(qa.admin.routers())
  print(qa.admin.secrets_effective(connectors="eod,fmp"))
  ```

Security
- Secrets routes require `admin` role or appropriate scopes (e.g., `admin:secrets.read`, `admin:secrets.write`). Tokens are issued via `/auth/login` and carry roles/scopes in claims.
