from ..client import ConnectorEndpoint


class FREDEndpoint(ConnectorEndpoint):
    """SDK endpoints for FRED connector."""

    def get_all_fred_data_sources(self, **params):
        return self._call('get_all_fred_data_sources', **params)

    def get_all_fred_data_tags(self, **params):
        return self._call('get_all_fred_data_tags', **params)

    def get_all_fred_releases(self, **params):
        return self._call('get_all_fred_releases', **params)

    def get_all_fred_series_by_tags(self, **params):
        return self._call('get_all_fred_series_by_tags', **params)

    def get_available_economic_indicators(self, **params):
        return self._call('get_available_economic_indicators', **params)

    def get_available_fed_balance_sheet_items(self, **params):
        return self._call('get_available_fed_balance_sheet_items', **params)

    def get_available_h41_series(self, **params):
        return self._call('get_available_h41_series', **params)

    def get_available_market_rates(self, **params):
        return self._call('get_available_market_rates', **params)

    def get_average_hourly_earnings(self, **params):
        return self._call('get_average_hourly_earnings', **params)

    def get_building_permits(self, **params):
        return self._call('get_building_permits', **params)

    def get_business_inventories(self, **params):
        return self._call('get_business_inventories', **params)

    def get_cache_stats(self, **params):
        return self._call('get_cache_stats', **params)

    def get_capacity_utilization(self, **params):
        return self._call('get_capacity_utilization', **params)

    def get_categories(self, **params):
        return self._call('get_categories', **params)

    def get_consumer_confidence(self, **params):
        return self._call('get_consumer_confidence', **params)

    def get_cpi(self, **params):
        return self._call('get_cpi', **params)

    def get_current_account_balance(self, **params):
        return self._call('get_current_account_balance', **params)

    def get_durable_goods_orders(self, **params):
        return self._call('get_durable_goods_orders', **params)

    def get_effective_federal_funds_rate(self, **params):
        return self._call('get_effective_federal_funds_rate', **params)

    def get_fed_agency_debt_securities(self, **params):
        return self._call('get_fed_agency_debt_securities', **params)

    def get_fed_currency_in_circulation(self, **params):
        return self._call('get_fed_currency_in_circulation', **params)

    def get_fed_funds_rate(self, **params):
        return self._call('get_fed_funds_rate', **params)

    def get_fed_loans_total(self, **params):
        return self._call('get_fed_loans_total', **params)

    def get_fed_mortgage_backed_securities(self, **params):
        return self._call('get_fed_mortgage_backed_securities', **params)

    def get_fed_primary_credit(self, **params):
        return self._call('get_fed_primary_credit', **params)

    def get_fed_reserve_balances(self, **params):
        return self._call('get_fed_reserve_balances', **params)

    def get_fed_reverse_repo_agreements(self, **params):
        return self._call('get_fed_reverse_repo_agreements', **params)

    def get_fed_securities_held_outright(self, **params):
        return self._call('get_fed_securities_held_outright', **params)

    def get_fed_total_assets(self, **params):
        return self._call('get_fed_total_assets', **params)

    def get_fed_treasury_bills(self, **params):
        return self._call('get_fed_treasury_bills', **params)

    def get_fed_treasury_general_account(self, **params):
        return self._call('get_fed_treasury_general_account', **params)

    def get_fed_treasury_inflation_indexed(self, **params):
        return self._call('get_fed_treasury_inflation_indexed', **params)

    def get_fed_treasury_notes_bonds_nominal(self, **params):
        return self._call('get_fed_treasury_notes_bonds_nominal', **params)

    def get_fed_treasury_securities(self, **params):
        return self._call('get_fed_treasury_securities', **params)

    def get_fred_data_series_by_id(self, **params):
        return self._call('get_fred_data_series_by_id', **params)

    def get_gdp(self, **params):
        return self._call('get_gdp', **params)

    def get_gdp_growth(self, **params):
        return self._call('get_gdp_growth', **params)

    def get_gdp_per_capita(self, **params):
        return self._call('get_gdp_per_capita', **params)

    def get_gdp_per_capita_ppp(self, **params):
        return self._call('get_gdp_per_capita_ppp', **params)

    def get_gdp_usd(self, **params):
        return self._call('get_gdp_usd', **params)

    def get_gnp(self, **params):
        return self._call('get_gnp', **params)

    def get_gross_private_domestic_investment(self, **params):
        return self._call('get_gross_private_domestic_investment', **params)

    def get_housing_starts(self, **params):
        return self._call('get_housing_starts', **params)

    def get_industrial_production(self, **params):
        return self._call('get_industrial_production', **params)

    def get_inflation_rate(self, **params):
        return self._call('get_inflation_rate', **params)

    def get_inflation_rate_cpi(self, **params):
        return self._call('get_inflation_rate_cpi', **params)

    def get_manufacturers_new_orders(self, **params):
        return self._call('get_manufacturers_new_orders', **params)

    def get_money_supply_m1(self, **params):
        return self._call('get_money_supply_m1', **params)

    def get_money_supply_m2(self, **params):
        return self._call('get_money_supply_m2', **params)

    def get_money_supply_m2_seasonally_adjusted(self, **params):
        return self._call('get_money_supply_m2_seasonally_adjusted', **params)

    def get_nonfarm_payrolls(self, **params):
        return self._call('get_nonfarm_payrolls', **params)

    def get_personal_consumption_expenditures(self, **params):
        return self._call('get_personal_consumption_expenditures', **params)

    def get_personal_savings_rate(self, **params):
        return self._call('get_personal_savings_rate', **params)

    def get_pmi(self, **params):
        return self._call('get_pmi', **params)

    def get_ppi(self, **params):
        return self._call('get_ppi', **params)

    def get_private_inventories(self, **params):
        return self._call('get_private_inventories', **params)

    def get_productivity(self, **params):
        return self._call('get_productivity', **params)

    def get_producer_price_index(self, **params):
        return self._call('get_producer_price_index', **params)

    def get_real_gdp(self, **params):
        return self._call('get_real_gdp', **params)

    def get_real_gdp_per_capita(self, **params):
        return self._call('get_real_gdp_per_capita', **params)

    def get_retail_sales(self, **params):
        return self._call('get_retail_sales', **params)

    def get_ten_year_treasury_rate(self, **params):
        return self._call('get_ten_year_treasury_rate', **params)

    def get_total_vehicle_sales(self, **params):
        return self._call('get_total_vehicle_sales', **params)

    def get_treasury_repo_rate(self, **params):
        return self._call('get_treasury_repo_rate', **params)

    def get_unemployment_rate(self, **params):
        return self._call('get_unemployment_rate', **params)

    def get_velocity_of_money(self, **params):
        return self._call('get_velocity_of_money', **params)

    def search_dealer_positioning_data(self, **params):
        return self._call('search_dealer_positioning_data', **params)

    def search_fred_for_series(self, **params):
        return self._call('search_fred_for_series', **params)

    def search_ofr_primary_dealer_data(self, **params):
        return self._call('search_ofr_primary_dealer_data', **params)

    def search_repo_market_data(self, **params):
        return self._call('search_repo_market_data', **params)

    def search_series(self, **params):
        return self._call('search_series', **params)

