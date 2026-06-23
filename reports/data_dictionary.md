# Data Dictionary — Bluestock MF Capstone

Database: `data/db/bluestock_mf.db` (SQLite) | Schema: `sql/schema.sql`

## dim_fund (40 rows)
Master list of mutual fund schemes.

| Column | Type | Description |
|---|---|---|
| amfi_code | TEXT (PK) | Unique scheme identifier |
| scheme_name | TEXT | Full official scheme name |
| fund_house | TEXT | AMC name |
| category | TEXT | Equity / Debt |
| sub_category | TEXT | Large Cap / Mid Cap / Liquid / etc. |
| plan | TEXT | Regular or Direct |
| launch_date | DATE | Fund launch date |
| benchmark | TEXT | Official benchmark index |
| expense_ratio_pct | REAL | Annual expense ratio (%) |
| exit_load_pct | REAL | Exit load (%) |
| min_sip_amount | REAL | Minimum SIP investment (₹) |
| min_lumpsum_amount | REAL | Minimum lumpsum investment (₹) |
| fund_manager | TEXT | Primary fund manager |
| risk_category | TEXT | SEBI risk category |
| sebi_category_code | TEXT | Internal SEBI code |

## dim_date (1,150 rows)
Generated from the distinct trading dates in `fact_nav`.

| Column | Type | Description |
|---|---|---|
| date_id | INTEGER (PK) | Surrogate key |
| date | DATE (unique) | Calendar date |
| year / month / quarter | INTEGER | Date parts |
| is_weekday | INTEGER (0/1) | 1 if Mon–Fri |

## fact_nav (46,000 rows) — source: 02_nav_history.csv
| Column | Type | Description |
|---|---|---|
| amfi_code | TEXT (FK → dim_fund) | Scheme code |
| date | DATE | NAV date |
| nav | REAL | NAV in ₹ |
| daily_return_pct | REAL | Day-over-day % change (computed) |

## fact_transactions (32,778 rows) — source: 08_investor_transactions.csv
| Column | Type | Description |
|---|---|---|
| tx_id | INTEGER (PK) | Surrogate key |
| investor_id | TEXT | Investor identifier |
| transaction_date | DATE | Transaction date |
| amfi_code | TEXT (FK → dim_fund) | Fund invested in |
| transaction_type | TEXT | SIP / Lumpsum / Redemption |
| amount_inr | INTEGER | Amount in ₹ |
| state / city / city_tier | TEXT | Investor geography (T30/B30 per AMFI) |
| age_group / gender / annual_income_lakh | — | Investor demographics |
| payment_mode | TEXT | UPI / Net Banking / Mandate / Cheque |
| kyc_status | TEXT | Verified / Pending |

## fact_performance (40 rows) — source: 07_scheme_performance.csv
| Column | Type | Description |
|---|---|---|
| amfi_code | TEXT (PK, FK → dim_fund) | Scheme code |
| return_1yr_pct / return_3yr_pct / return_5yr_pct | REAL | Returns |
| benchmark_3yr_pct | REAL | Benchmark 3yr CAGR |
| alpha / beta | REAL | Risk-adjusted measures |
| sharpe_ratio / sortino_ratio | REAL | Risk-adjusted return ratios |
| std_dev_ann_pct | REAL | Annualised volatility |
| max_drawdown_pct | REAL | Worst peak-to-trough decline |
| aum_crore | REAL | Fund-level AUM (₹ crore) |
| expense_ratio_pct | REAL | Annual expense ratio |
| morningstar_rating | INTEGER | 1–5 star (simulated) |
| flag_negative_sharpe | INTEGER (0/1) | Data-quality flag (Day 2 Task 3) |
| flag_expense_ratio_out_of_range | INTEGER (0/1) | Flag: outside 0.1–2.5% (Day 2 Task 3) |

## fact_portfolio (322 rows) — source: 09_portfolio_holdings.csv
| Column | Type | Description |
|---|---|---|
| amfi_code | TEXT (FK → dim_fund) | Fund |
| stock_symbol / stock_name | TEXT | Holding identity |
| sector | TEXT | Sector classification |
| weight_pct | REAL | % weight in portfolio |
| market_value_cr | REAL | Holding value (₹ crore) |
| current_price_inr | REAL | Stock price (₹) |
| portfolio_date | DATE | As-of date (Dec 2025) |

## fact_aum (90 rows) — source: 03_aum_by_fund_house.csv
| Column | Type | Description |
|---|---|---|
| date | DATE | Quarter-end date |
| fund_house | TEXT | AMC name |
| aum_lakh_crore / aum_crore | REAL | AUM in two units |
| num_schemes | INTEGER | Scheme count for that AMC |

## fact_sip_industry (48 rows) — source: 04_monthly_sip_inflows.csv
| Column | Type | Description |
|---|---|---|
| month | TEXT (PK) | YYYY-MM |
| sip_inflow_crore | REAL | Total SIP inflow (₹ crore) |
| active_sip_accounts_crore | REAL | Active SIP accounts (crore) |
| new_sip_accounts_lakh | REAL | New registrations (lakh) |
| sip_aum_lakh_crore | REAL | SIP AUM (₹ lakh crore) |
| yoy_growth_pct | REAL | YoY growth (null for first 12 months — see Day 1 notes) |

## fact_category_inflows (144 rows) — source: 05_category_inflows.csv
| Column | Type | Description |
|---|---|---|
| month | TEXT | YYYY-MM |
| category | TEXT | Fund category |
| net_inflow_crore | REAL | Net inflow (₹ crore) |

## fact_industry_folio (21 rows) — source: 06_industry_folio_count.csv
| Column | Type | Description |
|---|---|---|
| month | TEXT (PK) | YYYY-MM |
| total_folios_crore | REAL | Total folios (crore) |
| equity_folios_crore / debt_folios_crore / hybrid_folios_crore / others_folios_crore | REAL | Folio split by type |

## fact_benchmark (8,050 rows) — source: 10_benchmark_indices.csv
| Column | Type | Description |
|---|---|---|
| index_name | TEXT | Nifty 50 / Nifty 100 / etc. |
| date | DATE | Closing date |
| close_value | REAL | Index closing value |

---

## Cleaning rules applied (Day 2)

- **fact_nav**: dates parsed, sorted, deduplicated by `(amfi_code, date)`, reindexed to a
  full business-day calendar per fund with forward-fill for any gap (none found —
  source data already has zero missing trading days), NAV ≤ 0 dropped (none found),
  `daily_return_pct` computed.
- **fact_transactions**: `transaction_type` standardised (SIP kept uppercase as an
  acronym, others Title Case), rows with `amount_inr` ≤ 0 dropped (none found),
  `kyc_status` validated against {Verified, Pending} (no violations), unparseable
  dates dropped (none found).
- **fact_performance**: all numeric columns coerced with `pd.to_numeric` (catches
  any stray non-numeric values), `flag_negative_sharpe` and
  `flag_expense_ratio_out_of_range` (outside 0.1–2.5%) added as data-quality flags
  for downstream use — both flags are 0 for every row in this dataset.
- **All other 7 datasets**: deduplicated and null-checked; no issues found beyond the
  expected 12 nulls in `yoy_growth_pct` (see Day 1 notes).