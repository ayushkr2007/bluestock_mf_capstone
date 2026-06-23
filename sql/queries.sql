-- ============================================================
-- queries.sql — 10 analytical queries against bluestock_mf.db
-- ============================================================

-- Q1: Top 5 funds by AUM
SELECT amfi_code, scheme_name, fund_house, aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

-- Q2: Average NAV per month for a given scheme (example: amfi_code 119551)
SELECT strftime('%Y-%m', date) AS month, ROUND(AVG(nav), 2) AS avg_nav
FROM fact_nav
WHERE amfi_code = '119551'
GROUP BY month
ORDER BY month;

-- Q3: SIP inflow YoY growth (latest 12 months)
SELECT month, sip_inflow_crore, yoy_growth_pct
FROM fact_sip_industry
ORDER BY month DESC
LIMIT 12;

-- Q4: Total transaction amount by state
SELECT state, COUNT(*) AS num_transactions, SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- Q5: Funds with expense ratio below 1%
SELECT amfi_code, scheme_name, fund_house, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- Q6: Best-performing fund (highest 3yr CAGR) within each category
SELECT category, scheme_name, return_3yr_pct
FROM fact_performance
WHERE (category, return_3yr_pct) IN (
    SELECT category, MAX(return_3yr_pct)
    FROM fact_performance
    GROUP BY category
);

-- Q7: Average SIP amount by investor age group
SELECT age_group, ROUND(AVG(amount_inr), 2) AS avg_amount_inr, COUNT(*) AS num_transactions
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY age_group
ORDER BY avg_amount_inr DESC;

-- Q8: Funds with negative Sharpe ratio (data quality / risk flag)
SELECT amfi_code, scheme_name, sharpe_ratio
FROM fact_performance
WHERE flag_negative_sharpe = 1;

-- Q9: AUM growth by fund house, latest quarter vs first quarter on record
SELECT fund_house,
       MIN(date) AS first_date, MAX(date) AS latest_date,
       (SELECT aum_crore FROM fact_aum a2
          WHERE a2.fund_house = a1.fund_house ORDER BY date ASC LIMIT 1)  AS first_aum_crore,
       (SELECT aum_crore FROM fact_aum a2
          WHERE a2.fund_house = a1.fund_house ORDER BY date DESC LIMIT 1) AS latest_aum_crore
FROM fact_aum a1
GROUP BY fund_house
ORDER BY latest_aum_crore DESC;

-- Q10: City-tier split of total SIP investment (T30 vs B30)
SELECT city_tier, COUNT(*) AS num_transactions, SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY city_tier;