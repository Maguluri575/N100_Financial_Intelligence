"""
============================================================
Financial Ratio Engine
Sprint 2 - Day 08 & Day 09
Author : Hareesh
============================================================
"""

import os
import pandas as pd


# ============================================================
# Anomaly Logging
# ============================================================

def log_anomaly(message):
    os.makedirs("output", exist_ok=True)
    with open("output/ratio_edge_cases.log", "a", encoding="utf-8") as f:
        f.write(message + "\n")


# ============================================================
# Safe Division
# ============================================================

def safe_divide(numerator, denominator):
    if numerator is None or pd.isna(numerator):
        return None
    if denominator is None or pd.isna(denominator):
        return None
    if denominator == 0:
        return None
    return numerator / denominator


# ============================================================
# Net Profit Margin
# Formula:
# Net Profit / Sales × 100
# ============================================================

def net_profit_margin(net_profit, sales):
    value = safe_divide(net_profit, sales)
    if value is None:
        return None
    return round(value * 100, 2)


# ============================================================
# Operating Profit Margin
# Operating Profit / Sales × 100
# ============================================================

def operating_profit_margin(operating_profit, sales):
    value = safe_divide(operating_profit, sales)
    if value is None:
        return None
    return round(value * 100, 2)


# ============================================================
# Cross Check OPM
# ============================================================

def check_opm(computed_opm, source_opm):
    if computed_opm is None:
        return False
    if source_opm is None or pd.isna(source_opm):
        return False
    return abs(computed_opm - source_opm) > 1


# ============================================================
# Return on Equity (ROE)
#
# ROE = Net Profit / (Equity Capital + Reserves)
# Return None if equity <= 0
# ============================================================

def return_on_equity(net_profit, equity_capital, reserves):
    if net_profit is None or pd.isna(net_profit):
        return None

    eq_cap = equity_capital if (equity_capital is not None and not pd.isna(equity_capital)) else 0
    res = reserves if (reserves is not None and not pd.isna(reserves)) else 0
    equity = eq_cap + res

    if equity <= 0:
        return None

    return round((net_profit / equity) * 100, 2)


# ============================================================
# Return on Capital Employed
#
# ROCE = EBIT / (Equity + Reserves + Borrowings)
# EBIT = Operating Profit - Depreciation
# ============================================================

def return_on_capital_employed(operating_profit, *args):
    if operating_profit is None or pd.isna(operating_profit):
        return None

    if len(args) == 4:
        equity_capital, reserves, borrowings, depreciation = args
    elif len(args) == 3:
        equity_capital, reserves, borrowings = args
        depreciation = 0
    elif len(args) == 1:
        depreciation = args[0]
        equity_capital = 0
        reserves = 0
        borrowings = 0
    elif len(args) == 0:
        depreciation = 0
        equity_capital = 0
        reserves = 0
        borrowings = 0
    else:
        depreciation = args[0] if len(args) >= 1 else 0
        equity_capital = args[1] if len(args) >= 2 else 0
        reserves = args[2] if len(args) >= 3 else 0
        borrowings = args[3] if len(args) >= 4 else 0

    dep = depreciation if (depreciation is not None and not pd.isna(depreciation)) else 0
    ebit = operating_profit - dep

    eq_cap = equity_capital if (equity_capital is not None and not pd.isna(equity_capital)) else 0
    res = reserves if (reserves is not None and not pd.isna(reserves)) else 0
    borr = borrowings if (borrowings is not None and not pd.isna(borrowings)) else 0
    capital = eq_cap + res + borr

    if capital <= 0:
        return None

    return round((ebit / capital) * 100, 2)


# ============================================================
# Return on Assets
#
# Net Profit / Total Assets
# ============================================================

def return_on_assets(net_profit, total_assets):
    value = safe_divide(net_profit, total_assets)
    if value is None:
        return None
    return round(value * 100, 2)


# ============================================================
# Debt To Equity
#
# Borrowings / Equity
# Debt Free Companies return 0
# ============================================================

def debt_to_equity(borrowings, equity_capital, reserves):
    eq_cap = equity_capital if (equity_capital is not None and not pd.isna(equity_capital)) else 0
    res = reserves if (reserves is not None and not pd.isna(reserves)) else 0
    equity = eq_cap + res

    if borrowings == 0:
        return 0.0

    if equity <= 0:
        return None

    return round(borrowings / equity, 2)


# ============================================================
# High Leverage Flag
# ============================================================

def high_leverage_flag(de_ratio, sector):
    if de_ratio is None or pd.isna(de_ratio):
        return False
    if sector == "Financials":
        return False
    return de_ratio > 5


# ============================================================
# Interest Coverage Ratio
#
# (Operating Profit + Other Income) / Interest
# ============================================================

def interest_coverage_ratio(operating_profit, other_income, interest):
    op = operating_profit if (operating_profit is not None and not pd.isna(operating_profit)) else 0
    oth = other_income if (other_income is not None and not pd.isna(other_income)) else 0
    numerator = op + oth

    if interest is None or pd.isna(interest) or interest == 0:
        return None

    return round(numerator / interest, 2)


# Backward-compatible alias used by the engine

def interest_coverage(operating_profit, other_income, interest):
    return interest_coverage_ratio(operating_profit, other_income, interest)


# ============================================================
# ICR Label
# ============================================================

def icr_label(icr):
    if icr is None:
        return "Debt Free"
    return ""


# ============================================================
# ICR Warning
# ============================================================

def icr_warning(icr):
    if icr is None or pd.isna(icr):
        return False
    return icr < 1.5


# ============================================================
# Net Debt
#
# Borrowings - Investments
# ============================================================

def net_debt(borrowings, investments):
    borr = borrowings if (borrowings is not None and not pd.isna(borrowings)) else 0
    inv = investments if (investments is not None and not pd.isna(investments)) else 0
    return borr - inv


# ============================================================
# Asset Turnover
#
# Sales / Total Assets
# ============================================================

def asset_turnover(sales, total_assets):
    value = safe_divide(sales, total_assets)
    if value is None:
        return None
    return round(value, 2)


# ============================================================
# Book Value Per Share
# ============================================================

def book_value_per_share(equity_capital, reserves=0, face_value=None):
    equity = (equity_capital or 0) + (reserves or 0)
    if face_value is None or face_value == 0:
        return None
    shares = safe_divide(equity_capital, face_value)
    if shares is None or shares <= 0:
        return None
    return round(equity / shares, 2)


# ============================================================
# Earnings Per Share
# ============================================================

def earnings_per_share(net_profit, shares):
    value = safe_divide(net_profit, shares)
    if value is None:
        return None
    return round(value, 2)


# ============================================================
# Dividend Payout Ratio
#
# Dividend / Net Profit
# ============================================================

def dividend_payout_ratio(dividend, net_profit):
    value = safe_divide(dividend, net_profit)
    if value is None:
        return None
    return round(value * 100, 2)


    if value is None:
        return None

    return round(value * 100, 2)