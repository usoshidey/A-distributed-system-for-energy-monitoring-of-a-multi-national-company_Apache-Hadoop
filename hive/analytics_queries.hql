-- =============================================================================
-- Apache Hive Analytics Queries for Distributed Energy Monitoring Platform
-- =============================================================================

USE energy_db;

-- -----------------------------------------------------------------------------
-- Query 1: Total Global Energy Consumption (kWh)
-- -----------------------------------------------------------------------------
SELECT
    COUNT(*) AS total_readings_count,
    ROUND(SUM(energy_kwh), 2) AS global_total_kwh,
    ROUND(AVG(energy_kwh), 2) AS global_avg_kwh,
    ROUND(MIN(energy_kwh), 2) AS global_min_kwh,
    ROUND(MAX(energy_kwh), 2) AS global_max_kwh
FROM raw_energy_readings;


-- -----------------------------------------------------------------------------
-- Query 2: Country-Wise Energy Consumption & Comparison
-- -----------------------------------------------------------------------------
SELECT
    country,
    COUNT(*) AS total_records,
    ROUND(SUM(energy_kwh), 2) AS total_consumption_kwh,
    ROUND(AVG(energy_kwh), 2) AS avg_consumption_kwh,
    ROUND(STDDEV(energy_kwh), 2) AS consumption_stddev,
    ROUND(AVG(voltage), 1) AS avg_voltage_v,
    ROUND(AVG(power_factor), 2) AS avg_power_factor
FROM raw_energy_readings
GROUP BY country
ORDER BY total_consumption_kwh DESC;


-- -----------------------------------------------------------------------------
-- Query 3: Branch-Wise Consumption Breakdown
-- -----------------------------------------------------------------------------
SELECT
    country,
    branch_name,
    COUNT(DISTINCT meter_id) AS active_meters,
    COUNT(*) AS readings_count,
    ROUND(SUM(energy_kwh), 2) AS branch_total_kwh,
    ROUND(AVG(energy_kwh), 2) AS branch_avg_kwh,
    ROUND(MAX(energy_kwh), 2) AS peak_spike_kwh
FROM raw_energy_readings
GROUP BY country, branch_name
ORDER BY branch_total_kwh DESC;


-- -----------------------------------------------------------------------------
-- Query 4: Daily Average Consumption (Time-Series Aggregation)
-- -----------------------------------------------------------------------------
SELECT
    to_date(reading_time) AS reading_date,
    country,
    COUNT(*) AS daily_readings,
    ROUND(SUM(energy_kwh), 2) AS daily_total_kwh,
    ROUND(AVG(energy_kwh), 2) AS daily_avg_kwh
FROM raw_energy_readings
GROUP BY to_date(reading_time), country
ORDER BY reading_date DESC, country;


-- -----------------------------------------------------------------------------
-- Query 5: Monthly Consumption Trend
-- -----------------------------------------------------------------------------
SELECT
    substr(reading_time, 1, 7) AS year_month,
    country,
    ROUND(SUM(energy_kwh), 2) AS monthly_kwh,
    COUNT(DISTINCT to_date(reading_time)) AS active_days,
    ROUND(SUM(energy_kwh) / COUNT(DISTINCT to_date(reading_time)), 2) AS avg_kwh_per_day
FROM raw_energy_readings
GROUP BY substr(reading_time, 1, 7), country
ORDER BY year_month DESC, country;


-- -----------------------------------------------------------------------------
-- Query 6: Highest Energy-Consuming Branch (Analytical Window Ranking)
-- -----------------------------------------------------------------------------
SELECT
    country,
    branch_name,
    total_kwh,
    rank_in_country,
    rank_globally
FROM (
    SELECT
        country,
        branch_name,
        ROUND(SUM(energy_kwh), 2) AS total_kwh,
        DENSE_RANK() OVER (PARTITION BY country ORDER BY SUM(energy_kwh) DESC) AS rank_in_country,
        DENSE_RANK() OVER (ORDER BY SUM(energy_kwh) DESC) AS rank_globally
    FROM raw_energy_readings
    GROUP BY country, branch_name
) ranked_branches
WHERE rank_globally <= 3
ORDER BY rank_globally;


-- -----------------------------------------------------------------------------
-- Query 7: Electricity Expenditure Calculation Based on Country Tariffs
-- Sample illustrative tariffs:
-- India: 8.00 INR/kWh
-- USA: 0.15 USD/kWh
-- Germany: 0.30 EUR/kWh
-- Japan: 30.00 JPY/kWh
-- -----------------------------------------------------------------------------
SELECT
    country,
    ROUND(SUM(energy_kwh), 2) AS total_kwh,
    CASE
        WHEN country = 'India' THEN 8.00
        WHEN country = 'USA' THEN 0.15
        WHEN country = 'Germany' THEN 0.30
        WHEN country = 'Japan' THEN 30.00
        ELSE 0.20
    END AS tariff_rate,
    CASE
        WHEN country = 'India' THEN 'INR'
        WHEN country = 'USA' THEN 'USD'
        WHEN country = 'Germany' THEN 'EUR'
        WHEN country = 'Japan' THEN 'JPY'
        ELSE 'USD'
    END AS currency,
    CASE
        WHEN country = 'India' THEN '₹'
        WHEN country = 'USA' THEN '$'
        WHEN country = 'Germany' THEN '€'
        WHEN country = 'Japan' THEN '¥'
        ELSE '$'
    END AS currency_symbol,
    ROUND(
        SUM(energy_kwh) *
        (CASE
            WHEN country = 'India' THEN 8.00
            WHEN country = 'USA' THEN 0.15
            WHEN country = 'Germany' THEN 0.30
            WHEN country = 'Japan' THEN 30.00
            ELSE 0.20
        END), 2
    ) AS total_expenditure_local
FROM raw_energy_readings
GROUP BY country
ORDER BY total_kwh DESC;

