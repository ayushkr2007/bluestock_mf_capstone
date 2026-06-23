-- ============================================================
-- schema.sql
-- Bluestock Fintech MF Capstone — Day 2, Task 4
-- 11-table star schema (2 dimension + 9 fact tables)
-- ============================================================

DROP TABLE IF EXISTS dim_fund;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_portfolio;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_sip_industry;
DROP TABLE IF EXISTS fact_category_inflows;
DROP TABLE IF EXISTS fact_industry_folio;
DROP TABLE IF EXISTS fact_benchmark;

CREATE TABLE dim_fund (
    amfi_code           TEXT PRIMARY KEY,
    scheme_name         TEXT,
    fund_house          TEXT,
    category            TEXT,
    sub_category        TEXT,
    plan                TEXT,
    launch_date         DATE,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      REAL,
    min_lumpsum_amount  REAL,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);

CREATE TABLE dim_date (
    date_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    date        DATE UNIQUE NOT NULL,
    year        INTEGER,
    month       INTEGER,
    quarter     INTEGER,
    is_weekday  INTEGER
);

CREATE TABLE fact_nav (
    amfi_code         TEXT,
    date              DATE,
    nav               REAL,
    daily_return_pct  REAL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_transactions (
    tx_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT,
    transaction_date    DATE,
    amfi_code           TEXT,
    transaction_type    TEXT,
    amount_inr          INTEGER,
    state               TEXT,
    city                TEXT,
    city_tier           TEXT,
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_performance (
    amfi_code                       TEXT PRIMARY KEY,
    scheme_name                     TEXT,
    fund_house                      TEXT,
    category                        TEXT,
    plan                            TEXT,
    return_1yr_pct                  REAL,
    return_3yr_pct                  REAL,
    return_5yr_pct                  REAL,
    benchmark_3yr_pct                REAL,
    alpha                           REAL,
    beta                            REAL,
    sharpe_ratio                    REAL,
    sortino_ratio                   REAL,
    std_dev_ann_pct                 REAL,
    max_drawdown_pct                REAL,
    aum_crore                       REAL,
    expense_ratio_pct               REAL,
    morningstar_rating              INTEGER,
    risk_grade                      TEXT,
    flag_negative_sharpe            INTEGER,
    flag_expense_ratio_out_of_range INTEGER,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_portfolio (
    amfi_code         TEXT,
    stock_symbol      TEXT,
    stock_name        TEXT,
    sector            TEXT,
    weight_pct        REAL,
    market_value_cr   REAL,
    current_price_inr REAL,
    portfolio_date    DATE,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE fact_aum (
    date             DATE,
    fund_house       TEXT,
    aum_lakh_crore   REAL,
    aum_crore        REAL,
    num_schemes      INTEGER
);

CREATE TABLE fact_sip_industry (
    month                       TEXT PRIMARY KEY,
    sip_inflow_crore            REAL,
    active_sip_accounts_crore  REAL,
    new_sip_accounts_lakh      REAL,
    sip_aum_lakh_crore         REAL,
    yoy_growth_pct             REAL
);

CREATE TABLE fact_category_inflows (
    month      TEXT,
    category   TEXT,
    net_inflow_crore REAL
);

CREATE TABLE fact_industry_folio (
    month                 TEXT PRIMARY KEY,
    total_folios_crore    REAL,
    equity_folios_crore   REAL,
    debt_folios_crore     REAL,
    hybrid_folios_crore   REAL,
    others_folios_crore   REAL
);

CREATE TABLE fact_benchmark (
    index_name  TEXT,
    date        DATE,
    close_value REAL
);

CREATE INDEX idx_fact_nav_code     ON fact_nav(amfi_code);
CREATE INDEX idx_fact_nav_date     ON fact_nav(date);
CREATE INDEX idx_fact_tx_code      ON fact_transactions(amfi_code);
CREATE INDEX idx_fact_tx_date      ON fact_transactions(transaction_date);
CREATE INDEX idx_fact_portfolio_code ON fact_portfolio(amfi_code);
CREATE INDEX idx_fact_aum_house    ON fact_aum(fund_house);
CREATE INDEX idx_fact_benchmark_idx ON fact_benchmark(index_name, date);