"""
=========================================================
load_data.py

ETL Pipeline
N100 Financial Intelligence Platform

Author : Hareesh
=========================================================
"""

import os
import pandas as pd

# ==========================================================
# Data Folder
# ==========================================================

DATA_FOLDER = "data"

# ==========================================================
# Clean Column Names
# ==========================================================

def clean_columns(df):

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("%", "pct")
        .str.replace("-", "_")
    )

    return df


# ==========================================================
# Load Excel
# ==========================================================

def load_excel(file_name):

    file_path = os.path.join(DATA_FOLDER, file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_name} not found.")

    df = pd.read_excel(file_path, header=1)

    df = clean_columns(df)

    return df


import re

def normalize_year(val):
    if val is None or pd.isna(val):
        return "PARSE_ERROR"
    
    val_str = str(val).strip()
    
    if re.match(r"^\d{4}-\d{2}$", val_str):
        return val_str
        
    cleaned = re.sub(r"[-_\s]+", " ", val_str)
    
    # Month YYYY pattern (e.g. Dec 2012, Mar 2023 15)
    m = re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\b", cleaned, re.IGNORECASE)
    if m:
        month_name = m.group(1).lower()[:3]
        year = m.group(2)
        month_map = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
            "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"
        }
        return f"{year}-{month_map[month_name]}"
        
    # Month YY pattern (e.g. Mar 23, Mar-23, Dec-22)
    m = re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{2})\b", cleaned, re.IGNORECASE)
    if m:
        month_name = m.group(1).lower()[:3]
        year = m.group(2)
        full_year = "20" + year
        month_map = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
            "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"
        }
        return f"{full_year}-{month_map[month_name]}"
        
    # YYYY pattern (e.g. 2023)
    m = re.search(r"\b(\d{4})\b", cleaned)
    if m:
        return f"{m.group(1)}-03"
        
    # FY YY pattern (e.g. FY23)
    m = re.search(r"\bFY\s*(\d{2,4})\b", cleaned, re.IGNORECASE)
    if m:
        yr = m.group(1)
        if len(yr) == 2:
            yr = "20" + yr
        return f"{yr}-03"
        
    return "PARSE_ERROR"


def log_parse_failure(file_name, raw_value, company_id):
    os.makedirs("output", exist_ok=True)
    failures_file = os.path.join("output", "parse_failures.csv")
    new_row = pd.DataFrame([{
        "file": file_name,
        "raw_value": raw_value,
        "company_id": company_id
    }])
    if not os.path.exists(failures_file):
        new_row.to_csv(failures_file, index=False)
    else:
        new_row.to_csv(failures_file, mode="a", header=False, index=False)


def process_years(df, file_name):
    normalized = []
    for idx, row in df.iterrows():
        raw_year = row["year"]
        norm_year = normalize_year(raw_year)
        if norm_year == "PARSE_ERROR":
            log_parse_failure(file_name, raw_year, row["company_id"])
        normalized.append(norm_year)
    df["year"] = normalized
    df = df[df["year"] != "PARSE_ERROR"].copy()
    return df


# ==========================================================
# Load Files
# ==========================================================

def load_companies():
    print("Loading companies.xlsx")
    return load_excel("companies.xlsx")


def load_profit_loss():
    print("Loading profitandloss.xlsx")
    df = load_excel("profitandloss.xlsx")
    df = process_years(df, "profitandloss.xlsx")
    return df


def load_balance_sheet():
    print("Loading balancesheet.xlsx")
    df = load_excel("balancesheet.xlsx")
    df = process_years(df, "balancesheet.xlsx")
    return df


def load_cashflow():
    print("Loading cashflow.xlsx")
    df = load_excel("cashflow.xlsx")
    df = process_years(df, "cashflow.xlsx")
    return df


def load_sectors():
    print("Loading sectors.xlsx")
    file_path = os.path.join(DATA_FOLDER, "sectors.xlsx")
    if not os.path.exists(file_path):
        raise FileNotFoundError("sectors.xlsx not found.")
    df = pd.read_excel(file_path, header=0)
    df = clean_columns(df)
    return df


# ==========================================================
# Merge Financial Data
# ==========================================================

def merge_financial_data():

    companies = load_companies()
    profit_loss = load_profit_loss()
    balance_sheet = load_balance_sheet()
    cashflow = load_cashflow()

    # Remove duplicate row IDs
    profit_loss.drop(columns=["id"], inplace=True, errors="ignore")
    balance_sheet.drop(columns=["id"], inplace=True, errors="ignore")
    cashflow.drop(columns=["id"], inplace=True, errors="ignore")

    print("\nMerging Profit & Loss + Balance Sheet...")

    merged = pd.merge(
        profit_loss,
        balance_sheet,
        on=["company_id", "year"],
        how="left"
    )

    print("Merging Cash Flow...")

    merged = pd.merge(
        merged,
        cashflow,
        on=["company_id", "year"],
        how="left"
    )

    print("Merging Company Master...")

    merged = pd.merge(
        merged,
        companies,
        left_on="company_id",
        right_on="id",
        how="left",
        suffixes=("", "_company")
    )

    # Remove duplicate company id column
    if "id_company" in merged.columns:
        merged.drop(columns=["id_company"], inplace=True)

    print("Merging Sector Information...")
    sectors = load_sectors()
    merged = pd.merge(
        merged,
        sectors[["company_id", "broad_sector", "sub_sector"]],
        on="company_id",
        how="left"
    )

    print("\n====================================")
    print("Merge Completed Successfully")
    print("====================================")

    print("Rows :", len(merged))
    print("Columns :", len(merged.columns))

    print("\nMerged Columns:")
    print(list(merged.columns))

    return merged


# ==========================================================
# Data Quality
# ==========================================================

def data_quality(df):

    print("\n====================================")
    print("DATA QUALITY REPORT")
    print("====================================")

    print("Rows :", len(df))
    print("Columns :", len(df.columns))

    print("\nMissing Values")
    print(df.isnull().sum())

    print("\nDuplicate Rows :", df.duplicated().sum())


# ==========================================================
# Save CSV
# ==========================================================

def save_merged_dataset(df):

    os.makedirs("output", exist_ok=True)

    output_file = "output/merged_financial_data.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print("\nMerged Dataset Saved Successfully")
    print(output_file)


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    merged_df = merge_financial_data()

    data_quality(merged_df)

    save_merged_dataset(merged_df)