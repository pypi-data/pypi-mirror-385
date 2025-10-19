from .client import ConnectorEndpoint


class INSIDEREndpoint(ConnectorEndpoint):
    """SDK endpoints for Insider service."""

    def scan(self, **params):
        return self._call('scan', **params)

    def new(self, **params):
        return self._call('new', **params)

    def summary(self, **params):
        return self._call('summary', **params)

    def latest_trades(self, **params):
        return self._call('latest_trades', **params)

    def summary_universe(self, **params):
        return self._call('summary_universe', **params)
