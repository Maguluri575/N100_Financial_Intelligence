import os
import pandas as pd

from src.analytics.ratios import (
    safe_divide,
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning,
    net_debt,
    asset_turnover,
    book_value_per_share,
    earnings_per_share,
    dividend_payout_ratio,
    log_anomaly,
)
from src.analytics.cagr import calculate_cagr
from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    cfo_quality_score_from_ratio,
    capex_intensity,
    capex_category,
    fcf_conversion_rate,
    capital_allocation_pattern,
    generate_capital_report,
)


# ==========================================================
# Compute Financial Ratios
# ==========================================================

def compute_financial_ratios(df):
    output = df.sort_values(["company_id", "year"]).copy()
    output["year_num"] = pd.to_datetime(output["year"], format="%b %Y", errors="coerce").dt.year
    output["year_num"] = output["year_num"].fillna(0)

    print("Calculating Profitability Ratios...")
    output["net_profit_margin_pct"] = output.apply(
        lambda x: net_profit_margin(x["net_profit"], x["sales"]), axis=1
    )

    output["operating_profit_margin_pct"] = output.apply(
        lambda x: operating_profit_margin(x["operating_profit"], x["sales"]), axis=1
    )

    output["return_on_equity_pct"] = output.apply(
        lambda x: return_on_equity(x["net_profit"], x["equity_capital"], x["reserves"]), axis=1
    )

    output["roce_pct"] = output.apply(
        lambda x: return_on_capital_employed(
            x["operating_profit"], x["depreciation"], x["equity_capital"], x["reserves"], x["borrowings"]
        ),
        axis=1,
    )

    output["roce_source_pct"] = output["roce_percentage"]
    output["roa_pct"] = output.apply(
        lambda x: return_on_assets(x["net_profit"], x["total_assets"]), axis=1
    )

    print("Calculating Leverage Ratios...")
    output["debt_to_equity"] = output.apply(
        lambda x: debt_to_equity(x["borrowings"], x["equity_capital"], x["reserves"]), axis=1
    )
    output["high_leverage_flag"] = output.apply(
        lambda x: high_leverage_flag(x["debt_to_equity"], x["broad_sector"]), axis=1
    )
    output["interest_coverage"] = output.apply(
        lambda x: interest_coverage_ratio(x["operating_profit"], x["other_income"], x["interest"]), axis=1
    )
    output["icr_label"] = output["interest_coverage"].apply(icr_label)
    output["icr_warning_flag"] = output["interest_coverage"].apply(icr_warning)
    output["net_debt"] = output.apply(
        lambda x: net_debt(x["borrowings"], x["investments"]), axis=1
    )
    output["asset_turnover"] = output.apply(
        lambda x: asset_turnover(x["sales"], x["total_assets"]), axis=1
    )
    output["book_value_per_share"] = output.apply(
        lambda x: book_value_per_share(x["equity_capital"], x["reserves"], x["face_value"]), axis=1
    )
    output["earnings_per_share"] = output.apply(
        lambda x: earnings_per_share(x["net_profit"], x["face_value"]), axis=1
    )
    output["dividend_payout_ratio_pct"] = output.apply(
        lambda x: dividend_payout_ratio(x["dividend_payout"], x["net_profit"]), axis=1
    )
    output["total_debt_cr"] = output.apply(
        lambda x: round((x["borrowings"] / x["total_assets"]) * 100, 2)
        if pd.notna(x["total_assets"]) and x["total_assets"] != 0 else None,
        axis=1,
    )

    print("Calculating Cash Flow KPIs...")
    output["free_cash_flow_cr"] = output.apply(
        lambda x: free_cash_flow(x["operating_activity"], x["investing_activity"]), axis=1
    )
    output["capex_cr"] = output.apply(
        lambda x: capex_intensity(x["investing_activity"], x["sales"]), axis=1
    )
    output["capex_category"] = output["capex_cr"].apply(capex_category)
    output["fcf_conversion_pct"] = output.apply(
        lambda x: fcf_conversion_rate(
            free_cash_flow(x["operating_activity"], x["investing_activity"]), x["operating_profit"]
        ),
        axis=1,
    )
    output["cash_from_operations_cr"] = output.apply(
        lambda x: round((x["operating_activity"] / x["sales"]) * 100, 2)
        if pd.notna(x["sales"]) and x["sales"] != 0 else None,
        axis=1,
    )

    output["cfo_pat_ratio"] = output.apply(
        lambda x: safe_divide(x["operating_activity"], x["net_profit"]), axis=1
    )
    output["cfo_pat_ratio_5yr_avg"] = output.groupby("company_id")["cfo_pat_ratio"].transform(
        lambda x: x.rolling(window=5, min_periods=1).mean()
    )
    output["cfo_quality_score"] = output["cfo_pat_ratio_5yr_avg"].apply(cfo_quality_score_from_ratio)
    output["capital_allocation_pattern"] = output.apply(
        lambda x: capital_allocation_pattern(
            x["operating_activity"],
            x["investing_activity"],
            x["financing_activity"],
            x["cfo_quality_score"],
        ),
        axis=1,
    )

    output["opm_crosscheck_flag"] = output.apply(
        lambda x: x["operating_profit_margin_pct"] is not None and x["opm_percentage"] is not None and abs(x["operating_profit_margin_pct"] - x["opm_percentage"]) > 1,
        axis=1,
    )

    output["composite_quality_score"] = output.apply(
        lambda x: round(
            (
                (x["net_profit_margin_pct"] or 0)
                + (x["return_on_equity_pct"] or 0)
                + (x["roa_pct"] or 0)
                + (x["free_cash_flow_cr"] or 0)
            )
            / 4,
            2,
        ),
        axis=1,
    )

    os.makedirs("output", exist_ok=True)
    with open("output/ratio_edge_cases.log", "w", encoding="utf-8") as log_file:
        log_file.write("ratio edge case log\n")
        log_file.write("===================\n")
        for _, row in output.iterrows():
            if row["opm_crosscheck_flag"]:
                log_file.write(
                    f"company_id={row['company_id']} year={row['year']} broad_sector={row['broad_sector']} "
                    f"computed_opm={row['operating_profit_margin_pct']} source_opm={row['opm_percentage']} "
                    f"category=formula discrepancy\n"
                )
            if pd.notna(row["roce_pct"]) and pd.notna(row["roce_source_pct"]) and abs(row["roce_pct"] - row["roce_source_pct"]) > 5:
                log_file.write(
                    f"company_id={row['company_id']} year={row['year']} broad_sector={row['broad_sector']} "
                    f"computed_roce={row['roce_pct']} source_roce={row['roce_source_pct']} category=formula discrepancy\n"
                )

    return output


# ==========================================================
# CAGR ENGINE
# ==========================================================

def add_cagr_metrics(df):
    result = []
    grouped = df.groupby("company_id")

    for company, data in grouped:
        data = data.sort_values("year_num").copy()

        data["revenue_cagr_3yr"] = None
        data["revenue_cagr_5yr"] = None
        data["revenue_cagr_10yr"] = None
        data["revenue_cagr_3yr_flag"] = None
        data["revenue_cagr_5yr_flag"] = None
        data["revenue_cagr_10yr_flag"] = None

        data["pat_cagr_3yr"] = None
        data["pat_cagr_5yr"] = None
        data["pat_cagr_10yr"] = None
        data["pat_cagr_3yr_flag"] = None
        data["pat_cagr_5yr_flag"] = None
        data["pat_cagr_10yr_flag"] = None

        data["eps_cagr_3yr"] = None
        data["eps_cagr_5yr"] = None
        data["eps_cagr_10yr"] = None
        data["eps_cagr_3yr_flag"] = None
        data["eps_cagr_5yr_flag"] = None
        data["eps_cagr_10yr_flag"] = None

        if len(data) >= 6:
            start = data.iloc[0]
            end = data.iloc[-1]
            for window in [3, 5, 10]:
                revenue = calculate_cagr(start["sales"], end["sales"], window)
                pat = calculate_cagr(start["net_profit"], end["net_profit"], window)
                eps = calculate_cagr(start["eps"], end["eps"], window)

                data.loc[data.index[-1], f"revenue_cagr_{window}yr"] = revenue[0]
                data.loc[data.index[-1], f"revenue_cagr_{window}yr_flag"] = revenue[1]
                data.loc[data.index[-1], f"pat_cagr_{window}yr"] = pat[0]
                data.loc[data.index[-1], f"pat_cagr_{window}yr_flag"] = pat[1]
                data.loc[data.index[-1], f"eps_cagr_{window}yr"] = eps[0]
                data.loc[data.index[-1], f"eps_cagr_{window}yr_flag"] = eps[1]

        result.append(data)

    return pd.concat(result, ignore_index=False)


# ==========================================================
# RUN ENGINE
# ==========================================================

def run_ratio_engine(merged_dataframe):
    print("=" * 60)
    print("FINANCIAL RATIO ENGINE")
    print("=" * 60)

    df = compute_financial_ratios(merged_dataframe)
    print("Calculating CAGR Metrics...")
    df = add_cagr_metrics(df)

    generate_capital_report(df)
    print("Financial Ratio Engine Completed Successfully.")
    return df