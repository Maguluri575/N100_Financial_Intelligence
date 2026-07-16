"""
============================================================
CAGR Engine
Sprint 2 - Day 10

Author : Hareesh
============================================================
"""

import pandas as pd
import numpy as np


# ============================================================
# CAGR Formula
#
# CAGR = ((Ending / Beginning)^(1/n) - 1) ×100
#
# Edge Cases
# ------------------------------------------------------------
# Positive -> Positive
# Positive -> Negative
# Negative -> Positive
# Negative -> Negative
# Zero Base
# Insufficient Years
# ============================================================

def calculate_cagr(start_value,
                   end_value,
                   years):

    # -----------------------------
    # Less Data / Invalid Years
    # -----------------------------

    if years is None or years <= 0:
        return None, "INSUFFICIENT"

    # -----------------------------
    # Missing / NaN Values
    # -----------------------------

    if start_value is None or pd.isna(start_value):
        return None, "INSUFFICIENT"

    if end_value is None or pd.isna(end_value):
        return None, "INSUFFICIENT"

    # -----------------------------
    # Zero Base
    # -----------------------------

    if start_value == 0:
        return None, "ZERO_BASE"

    # -----------------------------
    # Positive -> Negative
    # -----------------------------

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    # -----------------------------
    # Negative -> Positive / Zero
    # -----------------------------

    if start_value < 0 and end_value >= 0:
        return None, "TURNAROUND"

    # -----------------------------
    # Negative -> Negative
    # -----------------------------

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    # -----------------------------
    # Normal CAGR
    # -----------------------------
    try:
        cagr = ((end_value / start_value) ** (1 / years) - 1) * 100
        return round(cagr, 2), "NORMAL"
    except Exception:
        return None, "INSUFFICIENT"


# ============================================================
# Revenue CAGR
# ============================================================

def revenue_cagr(start_revenue,
                 end_revenue,
                 years):

    return calculate_cagr(start_revenue,
                          end_revenue,
                          years)


# ============================================================
# PAT CAGR
# ============================================================

def pat_cagr(start_pat,
             end_pat,
             years):

    return calculate_cagr(start_pat,
                          end_pat,
                          years)


# ============================================================
# EPS CAGR
# ============================================================

def eps_cagr(start_eps,
             end_eps,
             years):

    return calculate_cagr(start_eps,
                          end_eps,
                          years)


# ============================================================
# Multiple Year CAGR
# Creates
# 3 Year
# 5 Year
# 10 Year
# ============================================================

def generate_all_cagr(start_value,
                      end_value):

    result = {}

    for yr in [3, 5, 10]:

        value, flag = calculate_cagr(
            start_value,
            end_value,
            yr
        )

        result[f"{yr}yr_value"] = value
        result[f"{yr}yr_flag"] = flag

    return result


# ============================================================
# Company CAGR Table
# ============================================================

def build_cagr_table(df,
                     value_column):

    """
    Expected DataFrame

    company_id
    year
    revenue / PAT / EPS

    """

    results = []

    companies = df["company_id"].unique()

    for company in companies:

        temp = df[df["company_id"] == company]

        temp = temp.sort_values("year")

        if len(temp) < 2:
            continue

        start = temp.iloc[0][value_column]
        end = temp.iloc[-1][value_column]

        total_years = temp.iloc[-1]["year"] - temp.iloc[0]["year"]

        value, flag = calculate_cagr(
            start,
            end,
            total_years
        )

        results.append({

            "company_id": company,

            "start_value": start,

            "end_value": end,

            "years": total_years,

            "cagr": value,

            "flag": flag

        })

    return pd.DataFrame(results)


# ============================================================
# CAGR Summary
# ============================================================

def print_summary(df):

    print("\n========== CAGR SUMMARY ==========\n")

    print(df.head())

    print("\nTotal Companies :", len(df))

    print("\nFlag Count")

    print(df["flag"].value_counts())

    print("\n=================================\n")