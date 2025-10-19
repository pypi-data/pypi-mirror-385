from typing import Any, Dict, Optional
from ..client import ConnectorEndpoint


class EODEndpoint(ConnectorEndpoint):
    """SDK endpoints for EOD connector."""

    def get_balance_sheet_statement(self, **params):
        return self._call('get_balance_sheet_statement', **params)

    def get_book_value(self, **params):
        return self._call('get_book_value', **params)

    def get_cash_flow_statement(self, **params):
        return self._call('get_cash_flow_statement', **params)

    def get_company_info(self, **params):
        return self._call('get_company_info', **params)

    def get_current_ratio_ttm(self, **params):
        return self._call('get_current_ratio_ttm', **params)

    def get_debt_to_equity_ttm(self, **params):
        return self._call('get_debt_to_equity_ttm', **params)

    def get_diluted_eps_ttm(self, **params):
        return self._call('get_diluted_eps_ttm', **params)

    def get_dividend_share(self, **params):
        return self._call('get_dividend_share', **params)

    def get_dividend_yield_ttm(self, **params):
        return self._call('get_dividend_yield_ttm', **params)

    def get_ebitda(self, **params):
        return self._call('get_ebitda', **params)

    def get_enterprise_value_ebitda(self, **params):
        return self._call('get_enterprise_value_ebitda', **params)

    def get_enterprise_value_revenue(self, **params):
        return self._call('get_enterprise_value_revenue', **params)

    def get_enterprise_value_ttm(self, **params):
        return self._call('get_enterprise_value_ttm', **params)

    def get_eps(self, **params):
        return self._call('get_eps', **params)

    def get_eps_estimate_current_quarter(self, **params):
        return self._call('get_eps_estimate_current_quarter', **params)

    def get_eps_estimate_current_year(self, **params):
        return self._call('get_eps_estimate_current_year', **params)

    def get_eps_estimate_next_quarter(self, **params):
        return self._call('get_eps_estimate_next_quarter', **params)

    def get_eps_estimate_next_year(self, **params):
        return self._call('get_eps_estimate_next_year', **params)

    def get_exchange_list(self, **params):
        return self._call('get_exchange_list', **params)

    def get_exchange_symbols(self, **params):
        return self._call('get_exchange_symbols', **params)

    def get_financial_metric(self, **params):
        return self._call('get_financial_metric', **params)

    def get_forex_intraday_prices(self, **params):
        return self._call('get_forex_intraday_prices', **params)

    def get_forward_pe(self, **params):
        return self._call('get_forward_pe', **params)

    def get_free_cash_flow_yield_ttm(self, **params):
        return self._call('get_free_cash_flow_yield_ttm', **params)

    def get_fundamental_data(self, **params):
        return self._call('get_fundamental_data', **params)

    def get_futures_contracts(self, **params):
        return self._call('get_futures_contracts', **params)

    def get_futures_expiration_dates(self, **params):
        return self._call('get_futures_expiration_dates', **params)

    def get_futures_pricing(self, **params):
        return self._call('get_futures_pricing', **params)

    def get_gross_profit_margin_ttm(self, **params):
        return self._call('get_gross_profit_margin_ttm', **params)

    def get_gross_profit_ttm(self, **params):
        return self._call('get_gross_profit_ttm', **params)

    def get_historical_prices(self, **params):
        return self._call('get_historical_prices', **params)

    def get_income_statement(self, **params):
        return self._call('get_income_statement', **params)

    def get_interest_coverage_ttm(self, **params):
        return self._call('get_interest_coverage_ttm', **params)

    def get_intraday_prices(self, **params):
        return self._call('get_intraday_prices', **params)

    def get_macro_borrow_rates(self, **params):
        return self._call('get_macro_borrow_rates', **params)

    def get_macro_indicators(self, **params):
        return self._call('get_macro_indicators', **params)

    def get_macro_releases(self, **params):
        return self._call('get_macro_releases', **params)

    def get_market_cap(self, **params):
        return self._call('get_market_cap', **params)

    def get_market_cap_mln(self, **params):
        return self._call('get_market_cap_mln', **params)

    def get_most_recent_quarter(self, **params):
        return self._call('get_most_recent_quarter', **params)

    def get_operating_margin_ttm(self, **params):
        return self._call('get_operating_margin_ttm', **params)

    def get_osebx_instruments(self, **params):
        return self._call('get_osebx_instruments', **params)

    def get_pe_ratio(self, **params):
        return self._call('get_pe_ratio', **params)

    def get_peg_ratio(self, **params):
        return self._call('get_peg_ratio', **params)

    def get_price_to_book_mrq(self, **params):
        return self._call('get_price_to_book_mrq', **params)

    def get_price_to_book_ttm(self, **params):
        return self._call('get_price_to_book_ttm', **params)

    def get_price_to_sales_ratio_ttm(self, **params):
        return self._call('get_price_to_sales_ratio_ttm', **params)

    def get_profit_margin(self, **params):
        return self._call('get_profit_margin', **params)

    def get_quarterly_earnings_growth_yoy(self, **params):
        return self._call('get_quarterly_earnings_growth_yoy', **params)

    def get_quarterly_revenue_growth_yoy(self, **params):
        return self._call('get_quarterly_revenue_growth_yoy', **params)

    def get_quick_ratio_ttm(self, **params):
        return self._call('get_quick_ratio_ttm', **params)

    def get_real_time_prices(self, **params):
        return self._call('get_real_time_prices', **params)

    def get_return_on_assets_ttm(self, **params):
        return self._call('get_return_on_assets_ttm', **params)

    def get_return_on_equity_ttm(self, **params):
        return self._call('get_return_on_equity_ttm', **params)

    def get_revenue_per_share_ttm(self, **params):
        return self._call('get_revenue_per_share_ttm', **params)

    def get_revenue_ttm(self, **params):
        return self._call('get_revenue_ttm', **params)

    def get_roic_ttm(self, **params):
        return self._call('get_roic_ttm', **params)

    def get_shares_stats(self, **params):
        return self._call('get_shares_stats', **params)

    def get_trailing_pe(self, **params):
        return self._call('get_trailing_pe', **params)

    def get_key_statistics(self, **params):
        return self._call('get_key_statistics', **params)

    def get_last_dividend(self, **params):
        return self._call('get_last_dividend', **params)

    def get_market_cap_mln(self, **params):
        return self._call('get_market_cap_mln', **params)

    def get_nasdaq_100_index(self, **params):
        return self._call('get_nasdaq_100_index', **params)

    def get_net_debt_to_ebitda_ttm(self, **params):
        return self._call('get_net_debt_to_ebitda_ttm', **params)

    def get_net_income_per_share_ttm(self, **params):
        return self._call('get_net_income_per_share_ttm', **params)

    def get_net_profit_margin_ttm(self, **params):
        return self._call('get_net_profit_margin_ttm', **params)

    def get_operating_cash_flow_per_share_ttm(self, **params):
        return self._call('get_operating_cash_flow_per_share_ttm', **params)

    def get_operating_profit_margin_ttm(self, **params):
        return self._call('get_operating_profit_margin_ttm', **params)

    def get_payout_ratio_ttm(self, **params):
        return self._call('get_payout_ratio_ttm', **params)

    def get_pb_ratio_ttm(self, **params):
        return self._call('get_pb_ratio_ttm', **params)

    def get_pe_ratio_ttm(self, **params):
        return self._call('get_pe_ratio_ttm', **params)

    def get_price_earnings_to_growth_ratio_ttm(self, **params):
        return self._call('get_price_earnings_to_growth_ratio_ttm', **params)

    def get_price_to_sales_ttm(self, **params):
        return self._call('get_price_to_sales_ttm', **params)

