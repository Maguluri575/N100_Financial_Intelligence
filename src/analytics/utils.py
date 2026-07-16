"""
============================================================
utils.py

Utility Functions
N100 Financial Intelligence Platform

Author : Hareesh
============================================================
"""

import pandas as pd
import sqlite3
import os


# ==========================================================
# Project Paths
# ==========================================================

DATA_FOLDER = "data"

DATABASE_FOLDER = "database"

DATABASE_NAME = "financial_intelligence.db"


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

def load_excel(file_name, sheet_name=0):

    path = os.path.join(DATA_FOLDER, file_name)

    df = pd.read_excel(path, sheet_name=sheet_name)

    df = clean_columns(df)

    return df


# ==========================================================
# Load Companies
# ==========================================================

def load_companies():

    return load_excel("companies.xlsx")


# ==========================================================
# Load Profit & Loss
# ==========================================================

def load_profit_loss():

    return load_excel("profitandloss.xlsx")


# ==========================================================
# Load Balance Sheet
# ==========================================================

def load_balance_sheet():

    return load_excel("balancesheet.xlsx")


# ==========================================================
# Load Cash Flow
# ==========================================================

def load_cashflow():

    return load_excel("cashflow.xlsx")


# ==========================================================
# Merge Financial Statements
# ==========================================================

def merge_financial_data():

    companies = load_companies()

    pnl = load_profit_loss()

    balance = load_balance_sheet()

    cashflow = load_cashflow()

    # Merge P&L + Balance Sheet

    df = pnl.merge(

        balance,

        on=["company_id", "year"],

        how="left"

    )

    # Merge Cash Flow

    df = df.merge(

        cashflow,

        on=["company_id", "year"],

        how="left"

    )

    # Merge Company Details

    df = df.merge(

        companies,

        on="company_id",

        how="left"

    )

    return df


# ==========================================================
# SQLite Connection
# ==========================================================

def get_connection():

    db_path = os.path.join(

        DATABASE_FOLDER,

        DATABASE_NAME

    )

    return sqlite3.connect(db_path)


# ==========================================================
# Save DataFrame to SQLite
# ==========================================================

def save_to_sqlite(df, table_name):

    conn = get_connection()

    df.to_sql(

        table_name,

        conn,

        if_exists="replace",

        index=False

    )

    conn.commit()

    conn.close()

    print(f"{table_name} saved successfully.")


# ==========================================================
# Load Table from SQLite
# ==========================================================

def load_table(table_name):

    conn = get_connection()

    query = f"SELECT * FROM {table_name}"

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# ==========================================================
# Export CSV
# ==========================================================

def export_csv(df, filename):

    output_folder = "output"

    os.makedirs(output_folder, exist_ok=True)

    path = os.path.join(

        output_folder,

        filename

    )

    df.to_csv(

        path,

        index=False

    )

    print(f"{filename} exported.")


# ==========================================================
# Display Summary
# ==========================================================

def summary(df):

    print("\n===========================")

    print("Rows :", len(df))

    print("Columns :", len(df.columns))

    print(df.columns.tolist())

    print("===========================\n")