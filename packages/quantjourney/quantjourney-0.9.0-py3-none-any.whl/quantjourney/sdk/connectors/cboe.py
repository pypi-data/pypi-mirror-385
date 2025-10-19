from typing import Dict, Any
from ..client import ConnectorEndpoint


class CBOEEndpoint(ConnectorEndpoint):
    """SDK endpoints for CBOE connector (aligned with API router)."""

    def get_underlying_quote(self, **params) -> Dict[str, Any]:
        return self._call('get_underlying_quote', **params)

    def get_options_expirations(self, **params) -> Dict[str, Any]:
        return self._call('get_options_expirations', **params)

    def get_options_chain(self, **params) -> Dict[str, Any]:
        return self._call('get_options_chain', **params)

    def get_historical_trades(self, **params) -> Dict[str, Any]:
        return self._call('get_historical_trades', **params)

    def get_trading_days(self, **params) -> Dict[str, Any]:
        return self._call('get_trading_days', **params)

    def get_vix_data(self, **params) -> Dict[str, Any]:
        return self._call('get_vix_data', **params)

    def get_vvix_data(self, **params) -> Dict[str, Any]:
        return self._call('get_vvix_data', **params)

    def get_skew_index_data(self, **params) -> Dict[str, Any]:
        return self._call('get_skew_index_data', **params)

    def get_vix_term_structure(self, **params) -> Dict[str, Any]:
        return self._call('get_vix_term_structure', **params)

    def get_futures_data(self, **params) -> Dict[str, Any]:
        return self._call('get_futures_data', **params)

    def get_options_volume(self, **params) -> Dict[str, Any]:
        return self._call('get_options_volume', **params)

    def get_real_time_prices(self, **params) -> Dict[str, Any]:
        return self._call('get_real_time_prices', **params)
