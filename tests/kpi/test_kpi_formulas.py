import math

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    interest_coverage_ratio,
    high_leverage_flag,
    icr_label,
    icr_warning,
    asset_turnover,
)
from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    capex_category,
    fcf_conversion_rate,
    capital_allocation_pattern,
)
from src.analytics.cagr import calculate_cagr


def test_net_profit_margin_normal_case():
    assert net_profit_margin(100, 500) == 20.0


def test_net_profit_margin_zero_sales_returns_none():
    assert net_profit_margin(100, 0) is None


def test_operating_profit_margin_normal_case():
    assert operating_profit_margin(80, 500) == 16.0


def test_return_on_equity_negative_equity_none():
    assert return_on_equity(50, -10, 0) is None


def test_return_on_capital_employed_normal_case():
    assert return_on_capital_employed(90, 200, 50, 100) == 25.71


def test_return_on_assets_zero_assets_none():
    assert return_on_assets(50, 0) is None


def test_debt_to_equity_debt_free_returns_zero():
    assert debt_to_equity(0, 100, 20) == 0


def test_interest_coverage_zero_interest_none():
    assert interest_coverage_ratio(100, 20, 0) is None


def test_interest_coverage_label_for_none():
    assert icr_label(None) == "Debt Free"


def test_high_leverage_flag_for_financials_is_false():
    assert high_leverage_flag(6.0, "Financials") is False


def test_asset_turnover_zero_assets_none():
    assert asset_turnover(100, 0) is None


def test_free_cash_flow_allows_negative_values():
    assert free_cash_flow(-10, -5) == -15


def test_cfo_quality_score_high_quality():
    assert cfo_quality_score(120, 90) == "High Quality"


def test_capex_intensity_category_asset_light():
    assert capex_category(2.0) == "Asset Light"


def test_fcf_conversion_rate_zero_operating_profit_none():
    assert fcf_conversion_rate(50, 0) is None


def test_capital_allocation_pattern_reinvestor():
    assert capital_allocation_pattern(10, -5, -2) == "Reinvestor"


def test_calculate_cagr_normal_case():
    value, flag = calculate_cagr(100, 121, 2)
    assert math.isclose(value, 10.0, abs_tol=0.01)
    assert flag == "NORMAL"


def test_calculate_cagr_turnaround_flag():
    value, flag = calculate_cagr(-10, 20, 2)
    assert value is None
    assert flag == "TURNAROUND"


def test_calculate_cagr_decline_to_loss_flag():
    value, flag = calculate_cagr(10, -5, 2)
    assert value is None
    assert flag == "DECLINE_TO_LOSS"


def test_calculate_cagr_zero_base_flag():
    value, flag = calculate_cagr(0, 5, 2)
    assert value is None
    assert flag == "ZERO_BASE"


def test_calculate_cagr_insufficient_flag():
    value, flag = calculate_cagr(10, 20, 0)
    assert value is None
    assert flag == "INSUFFICIENT"
