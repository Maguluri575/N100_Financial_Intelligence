"""
============================================================
Cash Flow KPI Engine
Sprint 2 - Day 11

Author : Hareesh
============================================================
"""

import pandas as pd
import numpy as np


# ============================================================
# Safe Division
# ============================================================

import os

def safe_divide(numerator, denominator):

    if numerator is None or pd.isna(numerator):
        return None

    if denominator is None or pd.isna(denominator):
        return None

    if denominator == 0:
        return None

    return numerator / denominator


# ============================================================
# Free Cash Flow
#
# FCF = CFO + CFI
#
# (CFI is normally negative)
# ============================================================

def free_cash_flow(operating_activity,
                   investing_activity):

    return operating_activity + investing_activity


# ============================================================
# CFO / PAT Ratio
# ============================================================

def cfo_pat_ratio(cfo, pat):

    value = safe_divide(cfo, pat)

    if value is None:
        return None

    return round(value, 2)


# ============================================================
# CFO Quality Score (Single Year)
# ============================================================

def cfo_quality_score(cfo, pat):

    ratio = cfo_pat_ratio(cfo, pat)

    if ratio is None:
        return None

    if ratio > 1:

        return "High Quality"

    elif ratio >= 0.5:

        return "Moderate"

    else:

        return "Accrual Risk"


# ============================================================
# CFO Quality Score from Ratio (Averaged/Rolling)
# ============================================================

def cfo_quality_score_from_ratio(avg_ratio):

    if avg_ratio is None or pd.isna(avg_ratio):
        return None

    if avg_ratio > 1.0:

        return "High Quality"

    elif avg_ratio >= 0.5:

        return "Moderate"

    else:

        return "Accrual Risk"


# ============================================================
# CapEx Intensity
#
# abs(CFI)/Sales ×100
# ============================================================

def capex_intensity(investing_activity,
                    sales):

    value = safe_divide(
        abs(investing_activity),
        sales
    )

    if value is None:
        return None

    return round(value * 100, 2)


# ============================================================
# CapEx Category
# ============================================================

def capex_category(capex_pct):

    if capex_pct is None:
        return None

    if capex_pct < 3:

        return "Asset Light"

    elif capex_pct <= 8:

        return "Moderate"

    else:

        return "Capital Intensive"


# ============================================================
# FCF Conversion
#
# FCF / Operating Profit
# ============================================================

def fcf_conversion_rate(fcf,
                        operating_profit):

    value = safe_divide(
        fcf,
        operating_profit
    )

    if value is None:
        return None

    return round(value * 100, 2)


# ============================================================
# Sign Function
# ============================================================

def sign(value):

    if value >= 0:
        return "+"

    return "-"


# ============================================================
# Capital Allocation Pattern
# ============================================================

def capital_allocation_pattern(
        cfo,
        cfi,
        cff,
        quality=None):

    s1 = sign(cfo)
    s2 = sign(cfi)
    s3 = sign(cff)

    pattern = (s1, s2, s3)

    # ------------------------------------------------

    if pattern == ("+", "-", "-"):

        if quality == "High Quality":

            return "Shareholder Returns"

        return "Reinvestor"

    elif pattern == ("+", "+", "-"):

        return "Liquidating Assets"

    elif pattern == ("-", "+", "+"):

        return "Distress Signal"

    elif pattern == ("-", "-", "+"):

        return "Growth Funded by Debt"

    elif pattern == ("+", "+", "+"):

        return "Cash Accumulator"

    elif pattern == ("-", "-", "-"):

        return "Pre-Revenue"

    elif pattern == ("+", "-", "+"):

        return "Mixed"

    else:

        return "Other"


# ============================================================
# Generate Capital Allocation Report
# ============================================================

def generate_capital_report(df):

    results = []

    # Sort to ensure rolling window calculation is chronologically correct
    df_sorted = df.sort_values(["company_id", "year"]).copy()

    df_sorted["cfo_pat_ratio"] = df_sorted.apply(
        lambda r: safe_divide(r["operating_activity"], r["net_profit"]),
        axis=1
    )

    df_sorted["cfo_pat_ratio_5yr_avg"] = df_sorted.groupby("company_id")["cfo_pat_ratio"].transform(
        lambda x: x.rolling(window=5, min_periods=1).mean()
    )

    for _, row in df_sorted.iterrows():

        avg_ratio = row["cfo_pat_ratio_5yr_avg"]
        quality = cfo_quality_score_from_ratio(avg_ratio)

        label = capital_allocation_pattern(

            row["operating_activity"],

            row["investing_activity"],

            row["financing_activity"],

            quality

        )

        results.append({

            "company_id": row["company_id"],

            "year": row["year"],

            "cfo_sign": sign(row["operating_activity"]),

            "cfi_sign": sign(row["investing_activity"]),

            "cff_sign": sign(row["financing_activity"]),

            "pattern_label": label

        })

    report = pd.DataFrame(results)

    os.makedirs("output", exist_ok=True)

    report.to_csv(

        "output/capital_allocation.csv",

        index=False

    )

    print(

        "\nCapital Allocation Report Saved"

    )

    return report


# ============================================================
# Summary
# ============================================================

def print_summary(report):

    print("\n========== CAPITAL ALLOCATION ==========\n")

    print(report.head())

    print("\nPattern Count")

    print(report["pattern_label"].value_counts())

    print("\n========================================\n")