from ..client import ConnectorEndpoint


class CCXTEndpoint(ConnectorEndpoint):
    """SDK endpoints for CCXT connector."""

    def get_historical_prices(self, **params):
        return self._call('get_historical_prices', **params)

