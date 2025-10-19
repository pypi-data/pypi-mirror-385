from ..client import ConnectorEndpoint


class OPENFIGIEndpoint(ConnectorEndpoint):
    """SDK endpoints for OPENFIGI connector."""

    def get_available_values(self, **params):
        return self._call('get_available_values', **params)

    def get_exchange_info(self, **params):
        return self._call('get_exchange_info', **params)

    def get_figi_data(self, **params):
        return self._call('get_figi_data', **params)

    def get_instrument_metadata(self, **params):
        return self._call('get_instrument_metadata', **params)

    def get_market_sector(self, **params):
        return self._call('get_market_sector', **params)

    def get_options_chain(self, **params):
        return self._call('get_options_chain', **params)

    def get_sector_securities(self, **params):
        return self._call('get_sector_securities', **params)

    def get_security_info(self, **params):
        return self._call('get_security_info', **params)

    def get_security_type(self, **params):
        return self._call('get_security_type', **params)

    def search_by_name(self, **params):
        return self._call('search_by_name', **params)

    def search_by_ticker(self, **params):
        return self._call('search_by_ticker', **params)

    def search_securities(self, **params):
        return self._call('search_securities', **params)

