import os
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 160)

RAW_DIR = os.path.join("data", "raw")

DATASETS = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]

def load_all_datasets():
    frames = {}
    for fname in DATASETS:
        path = os.path.join(RAW_DIR, fname)
        frames[fname] = pd.read_csv(path)
    return frames

def print_overview(frames):
    for fname, df in frames.items():
        print("=" * 90)
        print(f"{fname}  -> shape={df.shape}")
        print(df.dtypes)
        print(f"\nnull cells: {df.isnull().sum().sum()}  |  duplicate rows: {df.duplicated().sum()}")
        print("\nhead():")
        print(df.head())
        print()

def explore_fund_master(fund_master):
    print("=" * 90)
    print("FUND MASTER — UNIQUE VALUE EXPLORATION")
    print(f"Fund houses: {sorted(fund_master['fund_house'].unique())}")
    print(f"Categories: {sorted(fund_master['category'].unique())}")
    print(f"Sub-categories: {sorted(fund_master['sub_category'].unique())}")
    print(f"Risk categories: {sorted(fund_master['risk_category'].unique())}")

def validate_amfi_codes(fund_master, nav_history):
    print("=" * 90)
    print("AMFI CODE VALIDATION")
    fm_codes = set(fund_master["amfi_code"])
    nav_codes = set(nav_history["amfi_code"])
    print(f"Missing from nav_history: {fm_codes - nav_codes or 'None'}")
    print(f"Extra in nav_history: {nav_codes - fm_codes or 'None'}")

def main():
    frames = load_all_datasets()
    print_overview(frames)
    explore_fund_master(frames["01_fund_master.csv"])
    validate_amfi_codes(frames["01_fund_master.csv"], frames["02_nav_history.csv"])

if __name__ == "__main__":
    main()