"""
Main Entry Point
N100 Financial Intelligence Platform
"""

from src.etl.load_data import merge_financial_data
from src.analytics.ratio_engine import run_ratio_engine
from src.database.sqlite_manager import SQLiteManager


def main():

    print("=" * 60)
    print("N100 FINANCIAL INTELLIGENCE PLATFORM")
    print("=" * 60)

    print("\nLoading Data...")

    merged_df = merge_financial_data()

    print("\nRunning Ratio Engine...")

    ratio_df = run_ratio_engine(merged_df)

    print("\nSelecting KPI Columns for Save...")

    kpi_columns = [
        "company_id",
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "roce_pct",
        "roa_pct",
        "debt_to_equity",
        "high_leverage_flag",
        "interest_coverage",
        "icr_label",
        "icr_warning_flag",
        "net_debt",
        "asset_turnover",
        "free_cash_flow_cr",
        "capex_cr",
        "capex_intensity_pct",
        "fcf_conversion_pct",
        "cfo_quality_score",
        "capital_allocation_pattern",
        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",
        "total_debt_cr",
        "cash_from_operations_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score"
    ]

    # Filter to only keep columns that actually exist in the dataframe
    save_df = ratio_df[[col for col in kpi_columns if col in ratio_df.columns]].copy()

    print("\nSaving into SQLite...")

    db = SQLiteManager()

    db.save_dataframe(
        save_df,
        "financial_ratios"
    )

    print("\nExporting CSV...")

    save_df.to_csv(
        "output/financial_ratios.csv",
        index=False
    )

    db.close()

    print("\nSprint 2 Completed Successfully")


if __name__ == "__main__":
    main()