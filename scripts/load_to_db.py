"""
load_to_db.py
--------------
Bluestock Fintech MF Capstone — Day 2, Task 5

Usage:
    python scripts/load_to_db.py
"""

import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

PROCESSED_DIR = os.path.join("data", "processed")
DB_DIR = os.path.join("data", "db")
DB_PATH = os.path.join(DB_DIR, "bluestock_mf.db")
SCHEMA_PATH = os.path.join("sql", "schema.sql")

LOAD_PLAN = [
    ("clean_fund_master.csv", "dim_fund", None),
    ("clean_nav.csv", "fact_nav", ["amfi_code", "date", "nav", "daily_return_pct"]),
    ("clean_transactions.csv", "fact_transactions",
     ["investor_id", "transaction_date", "amfi_code", "transaction_type", "amount_inr",
      "state", "city", "city_tier", "age_group", "gender", "annual_income_lakh",
      "payment_mode", "kyc_status"]),
    ("clean_performance.csv", "fact_performance", None),
    ("clean_portfolio_holdings.csv", "fact_portfolio", None),
    ("clean_aum_by_fund_house.csv", "fact_aum", None),
    ("clean_monthly_sip_inflows.csv", "fact_sip_industry", None),
    ("clean_category_inflows.csv", "fact_category_inflows", None),
    ("clean_industry_folio_count.csv", "fact_industry_folio", None),
    ("clean_benchmark_indices.csv", "fact_benchmark", None),
]


def build_dim_date(engine):
    nav = pd.read_csv(os.path.join(PROCESSED_DIR, "clean_nav.csv"), usecols=["date"])
    dates = pd.to_datetime(nav["date"].unique())
    dim_date = pd.DataFrame({"date": sorted(dates)})
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["month"] = dim_date["date"].dt.month
    dim_date["quarter"] = dim_date["date"].dt.quarter
    dim_date["is_weekday"] = (dim_date["date"].dt.weekday < 5).astype(int)
    dim_date.to_sql("dim_date", engine, if_exists="append", index=False)
    print(f"[dim_date] {len(dim_date)} rows generated from fact_nav date range")


def main():
    os.makedirs(DB_DIR, exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"Schema created at {DB_PATH}")

    engine = create_engine(f"sqlite:///{DB_PATH}")
    for fname, table, cols in LOAD_PLAN:
        path = os.path.join(PROCESSED_DIR, fname)
        df = pd.read_csv(path)
        if cols:
            df = df[cols]
        df.to_sql(table, engine, if_exists="append", index=False)
        print(f"[{table}] loaded {len(df)} rows from {fname}")

    build_dim_date(engine)

    conn = sqlite3.connect(DB_PATH)
    print("=" * 60)
    print("ROW COUNTS PER TABLE")
    for (table,) in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall():
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<25} {count}")
    conn.close()


if __name__ == "__main__":
    main()