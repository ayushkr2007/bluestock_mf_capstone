"""
data_cleaning.py
-----------------
Bluestock Fintech MF Capstone — Day 2, Tasks 1-3

Cleans all 10 raw datasets and writes them to data/processed/.
Deep cleaning is applied to nav_history, investor_transactions, and
scheme_performance. The remaining 7 get a lighter pass.

Usage:
    python scripts/data_cleaning.py
"""

import os
import pandas as pd
import numpy as np

RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")


def clean_nav_history():
    df = pd.read_csv(os.path.join(RAW_DIR, "02_nav_history.csv"))
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["amfi_code", "date"]).drop_duplicates(subset=["amfi_code", "date"])

    filled_rows = 0
    out_frames = []
    for code, grp in df.groupby("amfi_code"):
        full_range = pd.bdate_range(grp["date"].min(), grp["date"].max())
        grp = grp.set_index("date").reindex(full_range)
        before_nulls = grp["nav"].isnull().sum()
        grp["nav"] = grp["nav"].ffill()
        filled_rows += before_nulls
        grp["amfi_code"] = code
        grp.index.name = "date"
        out_frames.append(grp.reset_index())

    df = pd.concat(out_frames, ignore_index=True)
    df = df[df["nav"] > 0]
    df["daily_return_pct"] = df.groupby("amfi_code")["nav"].pct_change() * 100

    out_path = os.path.join(PROCESSED_DIR, "clean_nav.csv")
    df.to_csv(out_path, index=False)
    print(f"[nav_history] {len(df)} rows | forward-filled {filled_rows} missing trading days | -> {out_path}")
    return df


def clean_investor_transactions():
    df = pd.read_csv(os.path.join(RAW_DIR, "08_investor_transactions.csv"))
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")

    type_map = {"sip": "SIP", "lumpsum": "Lumpsum", "redemption": "Redemption"}
    df["transaction_type"] = df["transaction_type"].str.strip().str.lower().map(type_map)
    valid_types = {"SIP", "Lumpsum", "Redemption"}
    bad_types = (~df["transaction_type"].isin(valid_types)).sum()

    invalid_amounts = (df["amount_inr"] <= 0).sum()
    df = df[df["amount_inr"] > 0]

    valid_kyc = {"Verified", "Pending"}
    bad_kyc = (~df["kyc_status"].isin(valid_kyc)).sum()

    before = len(df)
    df = df.dropna(subset=["transaction_date"])
    bad_dates = before - len(df)

    out_path = os.path.join(PROCESSED_DIR, "clean_transactions.csv")
    df.to_csv(out_path, index=False)
    print(f"[investor_transactions] {len(df)} rows | invalid amounts dropped: {invalid_amounts} | "
          f"unrecognised transaction_type: {bad_types} | unrecognised kyc_status: {bad_kyc} | "
          f"unparseable dates dropped: {bad_dates} | -> {out_path}")
    return df


def clean_scheme_performance():
    df = pd.read_csv(os.path.join(RAW_DIR, "07_scheme_performance.csv"))

    numeric_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "sharpe_ratio",
                    "sortino_ratio", "alpha", "beta", "std_dev_ann_pct", "max_drawdown_pct",
                    "expense_ratio_pct"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["flag_negative_sharpe"] = df["sharpe_ratio"] < 0
    df["flag_expense_ratio_out_of_range"] = ~df["expense_ratio_pct"].between(0.1, 2.5)

    out_path = os.path.join(PROCESSED_DIR, "clean_performance.csv")
    df.to_csv(out_path, index=False)
    n_neg_sharpe = df["flag_negative_sharpe"].sum()
    n_bad_expense = df["flag_expense_ratio_out_of_range"].sum()
    print(f"[scheme_performance] {len(df)} rows | negative Sharpe flagged: {n_neg_sharpe} | "
          f"expense ratio out of 0.1-2.5% range: {n_bad_expense} | -> {out_path}")
    return df


def clean_passthrough(fname):
    df = pd.read_csv(os.path.join(RAW_DIR, fname))
    before = len(df)
    df = df.drop_duplicates()
    dupes_removed = before - len(df)
    nulls = df.isnull().sum().sum()

    out_name = "clean_" + fname.split("_", 1)[1]
    out_path = os.path.join(PROCESSED_DIR, out_name)
    df.to_csv(out_path, index=False)
    print(f"[{fname}] {len(df)} rows | duplicates removed: {dupes_removed} | nulls: {nulls} | -> {out_path}")
    return df


PASSTHROUGH_FILES = [
    "01_fund_master.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print("=" * 90)
    print("DAY 2 — DATA CLEANING")
    print("=" * 90)
    clean_nav_history()
    clean_investor_transactions()
    clean_scheme_performance()
    for fname in PASSTHROUGH_FILES:
        clean_passthrough(fname)
    print("=" * 90)
    print("All 10 datasets cleaned and written to data/processed/")


if __name__ == "__main__":
    main()