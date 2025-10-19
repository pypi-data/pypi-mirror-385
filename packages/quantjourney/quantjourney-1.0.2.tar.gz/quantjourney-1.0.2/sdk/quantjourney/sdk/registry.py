"""SDK connector registry for lazy loading.

Maps connector key -> "module_path:ClassName"
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional
import json


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        return {}


def _load_routers_spec() -> Optional[Dict[str, bool]]:
    """Load enabled connectors from config.

    Prefers project-level `_config/routers.(yaml|json)` with `routers` map; falls
    back to package-local `quantjourney/sdk/routers.yaml` with `connectors` map.
    Returns a normalized dict of {connector: enabled_bool} or None if not found.
    """
    # Project-level search
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [
        repo_root / "_config" / "routers.yaml",
        repo_root / "_config" / "routers.json",
        Path.cwd() / "_config" / "routers.yaml",
        Path.cwd() / "_config" / "routers.json",
    ]
    for p in candidates:
        try:
            if not p.exists():
                continue
            if p.suffix.lower() in (".yaml", ".yml"):
                import yaml  # type: ignore
                raw = yaml.safe_load(p.read_text()) or {}
            else:
                raw = json.loads(p.read_text())
            if not isinstance(raw, dict):
                continue
            routers = raw.get("routers")
            if isinstance(routers, dict) and routers:
                return {str(k): bool(v) if isinstance(v, bool) else str(v).strip().lower() in {"1","true","yes"}
                        for k, v in routers.items()}
        except Exception:
            continue

    # Package-local fallback
    here = Path(__file__).resolve().parent
    yml = here / "routers.yaml"
    try:
        data = _load_yaml(yml)
        if isinstance(data, dict):
            cons = data.get("connectors", {})
            if isinstance(cons, dict) and cons:
                return {str(k): bool(v) for k, v in cons.items()}
    except Exception:
        pass
    return None


def _build_from_yaml() -> Dict[str, str]:
    routers_map = _load_routers_spec() or {}
    if not routers_map:
        return {}

    class_name_map = {
        "eod": "EODEndpoint",
        "fmp": "FMPEndpoint",
        "fred": "FREDEndpoint",
        "yf": "YFEndpoint",
        "openfigi": "OPENFIGIEndpoint",
        "sec": "SECEndpoint",
        "cboe": "CBOEEndpoint",
        "ccxt": "CCXTEndpoint",
        "imf": "IMFEndpoint",
        "cnnf": "CNNFEndpoint",
        "cftc": "CFTCEndpoint",
        "ff": "FFEndpoint",
        "oecd": "OECEndpoint",
        "multpl": "MULTPLEndpoint",
        "insider": "INSIDEREndpoint",
        "bt": "BTEndpoint",
        "analytics": "ANALYTICSEndpoint",
        "universe": "UNIVERSEEndpoint",
        # Add others here as SDK wrappers are added
    }

    out: Dict[str, str] = {}
    for key, enabled in routers_map.items():
        if not enabled:
            continue
        mod = f"quantjourney.sdk.connectors.{key}"
        cls = class_name_map.get(key)
        if not cls:
            # Skip unknown until wrapper exists
            continue
        out[key] = f"{mod}:{cls}"
    return out


_default = {
    "eod": "quantjourney.sdk.connectors.eod:EODEndpoint",
    "fmp": "quantjourney.sdk.connectors.fmp:FMPEndpoint",
    "fred": "quantjourney.sdk.connectors.fred:FREDEndpoint",
    "yf": "quantjourney.sdk.connectors.yf:YFEndpoint",
    "openfigi": "quantjourney.sdk.connectors.openfigi:OPENFIGIEndpoint",
    "sec": "quantjourney.sdk.connectors.sec:SECEndpoint",
    "cboe": "quantjourney.sdk.connectors.cboe:CBOEEndpoint",
    "ccxt": "quantjourney.sdk.connectors.ccxt:CCXTEndpoint",
    "imf": "quantjourney.sdk.connectors.imf:IMFEndpoint",
    "cnnf": "quantjourney.sdk.connectors.cnnf:CNNFEndpoint",
    "cftc": "quantjourney.sdk.connectors.cftc:CFTCEndpoint",
    "ff": "quantjourney.sdk.connectors.ff:FFEndpoint",
    "oecd": "quantjourney.sdk.connectors.oecd:OECEndpoint",
    "multpl": "quantjourney.sdk.connectors.multpl:MULTPLEndpoint",
    "insider": "quantjourney.sdk.connectors.insider:INSIDEREndpoint",
    "bt": "quantjourney.sdk.connectors.bt:BTEndpoint",
    "analytics": "quantjourney.sdk.connectors.analytics:ANALYTICSEndpoint",
    "universe": "quantjourney.sdk.connectors.universe:UNIVERSEEndpoint",
}

SDK_CONNECTORS: Dict[str, str] = _build_from_yaml() or _default

__all__ = ["SDK_CONNECTORS"]
