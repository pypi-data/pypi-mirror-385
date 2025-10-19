from ..client import ConnectorEndpoint


class FMPEndpoint(ConnectorEndpoint):
    """SDK endpoints for FMP connector."""

    def get_analyst_recommendations(self, **params):
        return self._call('get_analyst_recommendations', **params)

    def get_balance_sheet_statement(self, **params):
        return self._call('get_balance_sheet_statement', **params)

    def get_beta(self, **params):
        return self._call('get_beta', **params)

    def get_book_value(self, **params):
        return self._call('get_book_value', **params)

    def get_book_value_per_share_ttm(self, **params):
        return self._call('get_book_value_per_share_ttm', **params)

    def get_cash_flow_statement(self, **params):
        return self._call('get_cash_flow_statement', **params)

    def get_cash_per_share_ttm(self, **params):
        return self._call('get_cash_per_share_ttm', **params)

    def get_cash_ratio_ttm(self, **params):
        return self._call('get_cash_ratio_ttm', **params)

    def get_cik_mapper_by_company(self, **params):
        return self._call('get_cik_mapper_by_company', **params)

    def get_cik_mapper_by_name(self, **params):
        return self._call('get_cik_mapper_by_name', **params)

    def get_company_profile(self, **params):
        return self._call('get_company_profile', **params)

    def get_current_ratio_ttm(self, **params):
        return self._call('get_current_ratio_ttm', **params)

    def get_debt_ratio_ttm(self, **params):
        return self._call('get_debt_ratio_ttm', **params)

    def get_debt_to_assets_ttm(self, **params):
        return self._call('get_debt_to_assets_ttm', **params)

    def get_debt_to_equity_ratio_ttm(self, **params):
        return self._call('get_debt_to_equity_ratio_ttm', **params)

    def get_debt_to_equity_ttm(self, **params):
        return self._call('get_debt_to_equity_ttm', **params)

    def get_diluted_eps_ttm(self, **params):
        return self._call('get_diluted_eps_ttm', **params)

    def get_dividend_share(self, **params):
        return self._call('get_dividend_share', **params)

    def get_dividend_yield_ttm(self, **params):
        return self._call('get_dividend_yield_ttm', **params)

    def get_earnings_calendar(self, **params):
        return self._call('get_earnings_calendar', **params)

    def get_earnings_yield_ttm(self, **params):
        return self._call('get_earnings_yield_ttm', **params)

    def get_enterprise_value(self, **params):
        return self._call('get_enterprise_value', **params)

    def get_enterprise_value_ebit(self, **params):
        return self._call('get_enterprise_value_ebit', **params)

    def get_enterprise_value_ebitda(self, **params):
        return self._call('get_enterprise_value_ebitda', **params)

    def get_enterprise_value_multiple_ttm(self, **params):
        return self._call('get_enterprise_value_multiple_ttm', **params)

    def get_enterprise_value_over_ebitda_ttm(self, **params):
        return self._call('get_enterprise_value_over_ebitda_ttm', **params)

    def get_enterprise_value_revenue(self, **params):
        return self._call('get_enterprise_value_revenue', **params)

    def get_enterprise_value_ttm(self, **params):
        return self._call('get_enterprise_value_ttm', **params)

    def get_eps(self, **params):
        return self._call('get_eps', **params)

    def get_ev_to_sales_ttm(self, **params):
        return self._call('get_ev_to_sales_ttm', **params)

    def get_exchange_wide_data(self, **params):
        return self._call('get_exchange_wide_data', **params)

    def get_financial_ratios_ttm(self, **params):
        return self._call('get_financial_ratios_ttm', **params)

    def get_free_cash_flow_per_share_ttm(self, **params):
        return self._call('get_free_cash_flow_per_share_ttm', **params)

    def get_free_cash_flow_yield_ttm(self, **params):
        return self._call('get_free_cash_flow_yield_ttm', **params)

    def get_graham_number_ttm(self, **params):
        return self._call('get_graham_number_ttm', **params)

    def get_gross_profit_margin_ttm(self, **params):
        return self._call('get_gross_profit_margin_ttm', **params)

    def get_historical_prices(self, **params):
        return self._call('get_historical_prices', **params)

    def get_income_statement(self, **params):
        return self._call('get_income_statement', **params)

    def get_insider_trading(self, **params):
        return self._call('get_insider_trading', **params)

    def get_insider_trading_rss_feed(self, **params):
        return self._call('get_insider_trading_rss_feed', **params)

    def get_interest_coverage_ttm(self, **params):
        return self._call('get_interest_coverage_ttm', **params)

    def get_intraday_prices(self, **params):
        return self._call('get_intraday_prices', **params)

    def get_key_metrics_ttm(self, **params):
        return self._call('get_key_metrics_ttm', **params)

    def get_last_dividend(self, **params):
        return self._call('get_last_dividend', **params)

    def get_live_prices(self, **params):
        return self._call('get_live_prices', **params)

    def get_market_cap(self, **params):
        return self._call('get_market_cap', **params)

    def get_market_cap_mln(self, **params):
        return self._call('get_market_cap_mln', **params)

    def get_market_movers(self, **params):
        return self._call('get_market_movers', **params)

    def get_net_debt_to_ebitda_ttm(self, **params):
        return self._call('get_net_debt_to_ebitda_ttm', **params)

    def get_net_income_per_share_ttm(self, **params):
        return self._call('get_net_income_per_share_ttm', **params)

    def get_net_profit_margin_ttm(self, **params):
        return self._call('get_net_profit_margin_ttm', **params)

    def get_operating_cash_flow_per_share_ttm(self, **params):
        return self._call('get_operating_cash_flow_per_share_ttm', **params)

    def get_operating_margin_ttm(self, **params):
        return self._call('get_operating_margin_ttm', **params)

    def get_operating_profit_margin_ttm(self, **params):
        return self._call('get_operating_profit_margin_ttm', **params)

    def get_payout_ratio_ttm(self, **params):
        return self._call('get_payout_ratio_ttm', **params)

    def get_pb_ratio(self, **params):
        return self._call('get_pb_ratio', **params)

    def get_pb_ratio_ttm(self, **params):
        return self._call('get_pb_ratio_ttm', **params)

    def get_pe_ratio(self, **params):
        return self._call('get_pe_ratio', **params)

    def get_pe_ratio_ttm(self, **params):
        return self._call('get_pe_ratio_ttm', **params)

    def get_peg_ratio(self, **params):
        return self._call('get_peg_ratio', **params)

    def get_price_earnings_to_growth_ratio_ttm(self, **params):
        return self._call('get_price_earnings_to_growth_ratio_ttm', **params)

    def get_price_target_summary(self, **params):
        return self._call('get_price_target_summary', **params)

    def get_price_targets(self, **params):
        return self._call('get_price_targets', **params)

    def get_price_to_book_ttm(self, **params):
        return self._call('get_price_to_book_ttm', **params)

    def get_price_to_sales_ratio_ttm(self, **params):
        return self._call('get_price_to_sales_ratio_ttm', **params)

    def get_price_to_sales_ttm(self, **params):
        return self._call('get_price_to_sales_ttm', **params)

    def get_profit_margin(self, **params):
        return self._call('get_profit_margin', **params)

    def get_ps_ratio(self, **params):
        return self._call('get_ps_ratio', **params)

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

    def get_roic_ttm(self, **params):
        return self._call('get_roic_ttm', **params)

    def get_shareholders_equity_per_share_ttm(self, **params):
        return self._call('get_shareholders_equity_per_share_ttm', **params)

    def get_shares_stats(self, **params):
        return self._call('get_shares_stats', **params)

    def get_shares_stats_mln(self, **params):
        return self._call('get_shares_stats_mln', **params)

    def get_stock_screener(self, **params):
        return self._call('get_stock_screener', **params)

    def get_tangible_book_value_per_share_ttm(self, **params):
        return self._call('get_tangible_book_value_per_share_ttm', **params)

    def get_trailing_pe(self, **params):
        return self._call('get_trailing_pe', **params)

    def get_upgrades_downgrades(self, **params):
        return self._call('get_upgrades_downgrades', **params)

