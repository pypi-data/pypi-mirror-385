# QuantJourney SDK package root
from importlib import metadata as _metadata

# Public re-exports for convenience
from .sdk import QuantJourney, QuantJourneyAPI  # noqa: F401

try:
    __version__ = _metadata.version("quantjourney")
except Exception:  # pragma: no cover
    __version__ = "0+unknown"

__all__ = [
    "sdk",
    "QuantJourney",
    "QuantJourneyAPI",
    "__version__",
]
