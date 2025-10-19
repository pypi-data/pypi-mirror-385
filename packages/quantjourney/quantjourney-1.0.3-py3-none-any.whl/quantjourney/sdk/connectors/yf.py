from typing import Any, Dict, List, Optional, Union
from ..client import ConnectorEndpoint


class YFEndpoint(ConnectorEndpoint):
    """Yahoo Finance endpoints with friendly argument mapping.

    Notes:
    - Server expects `symbols` (str | List[str]) for batch-friendly methods.
    - These helpers accept either `symbol` or `symbols` and normalize to `symbols`.
    """

    @staticmethod
    def _norm_symbols(symbol: Optional[str] = None,
                      symbols: Optional[Union[str, List[str]]] = None) -> Union[str, List[str]]:
        if symbols is not None:
            return symbols
        if symbol is None:
            raise ValueError("symbol or symbols is required")
        return symbol

    def get_historical_prices(
        self,
        symbol: Optional[str] = None,
        symbols: Optional[Union[str, List[str]]] = None,
        start_date: str = "",
        end_date: str = "",
        frequency: str = "1d",
        exchanges: Optional[Union[str, List[str]]] = None,
    ) -> Any:
        payload: Dict[str, Any] = {
            "symbols": self._norm_symbols(symbol=symbol, symbols=symbols),
            "start_date": start_date,
            "end_date": end_date,
            "frequency": frequency,
        }
        if exchanges is not None:
            payload["exchanges"] = exchanges
        return self._call("get_historical_prices", **payload)

    def get_real_time_prices(
        self,
        symbol: Optional[str] = None,
        symbols: Optional[Union[str, List[str]]] = None,
        exchange: Optional[str] = "US",
    ) -> Any:
        payload: Dict[str, Any] = {
            "symbols": self._norm_symbols(symbol=symbol, symbols=symbols),
        }
        if exchange is not None:
            payload["exchange"] = exchange
        return self._call("get_real_time_prices", **payload)

    def get_intraday_prices(
        self,
        symbol: Optional[str] = None,
        symbols: Optional[Union[str, List[str]]] = None,
        start_time: str = "",
        end_time: str = "",
        frequency: str = "5m",
        exchanges: Optional[Union[str, List[str]]] = None,
    ) -> Any:
        payload: Dict[str, Any] = {
            "symbols": self._norm_symbols(symbol=symbol, symbols=symbols),
            "start_time": start_time,
            "end_time": end_time,
            "frequency": frequency,
        }
        if exchanges is not None:
            payload["exchanges"] = exchanges
        return self._call("get_intraday_prices", **payload)
