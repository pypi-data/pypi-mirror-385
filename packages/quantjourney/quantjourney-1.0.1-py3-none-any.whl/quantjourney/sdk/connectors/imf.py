from ..client import ConnectorEndpoint


class IMFEndpoint(ConnectorEndpoint):
    """SDK endpoints for IMF connector (aligned with API router)."""

    def get_trade_data(self, **params):
        return self._call('get_trade_data', **params)

    def get_trade_balance_data(self, **params):
        return self._call('get_trade_balance_data', **params)

    def get_economic_indicators(self, **params):
        return self._call('get_economic_indicators', **params)

    def get_gdp_data(self, **params):
        return self._call('get_gdp_data', **params)

    def get_inflation_data(self, **params):
        return self._call('get_inflation_data', **params)

    def get_cpi_data(self, **params):
        return self._call('get_cpi_data', **params)

    def get_unemployment_data(self, **params):
        return self._call('get_unemployment_data', **params)

    def get_current_account_data(self, **params):
        return self._call('get_current_account_data', **params)

    def get_country_codes(self, **params):
        return self._call('get_country_codes', **params)

    def get_available_indicators(self, **params):
        return self._call('get_available_indicators', **params)

    def get_available_bop_indicators(self, **params):
        return self._call('get_available_bop_indicators', **params)

    def get_available_trade_indicators(self, **params):
        return self._call('get_available_trade_indicators', **params)

    def get_available_weo_indicators(self, **params):
        return self._call('get_available_weo_indicators', **params)

    def get_available_fsi_indicators(self, **params):
        return self._call('get_available_fsi_indicators', **params)

    def get_cache_stats(self, **params):
        return self._call('get_cache_stats', **params)
