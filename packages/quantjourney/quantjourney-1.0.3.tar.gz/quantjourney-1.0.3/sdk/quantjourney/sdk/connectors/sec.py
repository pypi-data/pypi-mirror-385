from ..client import ConnectorEndpoint


class SECEndpoint(ConnectorEndpoint):
    """SDK endpoints for SEC connector (aligned with API router)."""

    def get_company_filings(self, **params):
        return self._call('get_company_filings', **params)

    def get_institutional_holdings(self, **params):
        return self._call('get_institutional_holdings', **params)

    def get_quarterly_holdings_changes(self, **params):
        return self._call('get_quarterly_holdings_changes', **params)

    def get_insider_transactions(self, **params):
        return self._call('get_insider_transactions', **params)

    def get_cache_stats(self, **params):
        return self._call('get_cache_stats', **params)

    def get_quarterly_holdings_comparison(self, **params):
        return self._call('get_quarterly_holdings_comparison', **params)

    def get_quarterly_position_changes(self, **params):
        return self._call('get_quarterly_position_changes', **params)

    def get_institutional_portfolio_summary(self, **params):
        return self._call('get_institutional_portfolio_summary', **params)

    def get_company_facts(self, **params):
        return self._call('get_company_facts', **params)

    def get_financial_statements(self, **params):
        return self._call('get_financial_statements', **params)

    def get_company_concept(self, **params):
        return self._call('get_company_concept', **params)

    def search_filings(self, **params):
        return self._call('search_filings', **params)

    def search_companies(self, **params):
        return self._call('search_companies', **params)

    def get_recent_filings(self, **params):
        return self._call('get_recent_filings', **params)

    def get_form4_filings(self, **params):
        return self._call('get_form4_filings', **params)

    def get_beneficial_ownership(self, **params):
        return self._call('get_beneficial_ownership', **params)

    def get_company_submissions(self, **params):
        return self._call('get_company_submissions', **params)

    def get_company_concepts(self, **params):
        return self._call('get_company_concepts', **params)

    def get_frames(self, **params):
        return self._call('get_frames', **params)

    def get_company_metadata(self, **params):
        return self._call('get_company_metadata', **params)

    def search_entities(self, **params):
        return self._call('search_entities', **params)

    def get_filing_metadata(self, **params):
        return self._call('get_filing_metadata', **params)
