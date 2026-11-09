-- =============================================================================
-- Apache Hive DDL: Schema and Table Creation for Energy Monitoring System
-- =============================================================================

CREATE DATABASE IF NOT EXISTS energy_db;
USE energy_db;

-- 1. External Table over Raw CSV Telemetry stored in HDFS
DROP TABLE IF EXISTS raw_energy_readings;
CREATE EXTERNAL TABLE IF NOT EXISTS raw_energy_readings (
    reading_id      STRING,
    meter_id        STRING,
    company_id      STRING,
    branch_name     STRING,
    country         STRING,
    reading_time    TIMESTAMP,
    energy_kwh      DOUBLE,
    voltage         DOUBLE,
    current_amp     DOUBLE,
    power_factor    DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/energy-monitoring/raw-data'
TBLPROPERTIES ("skip.header.line.count"="1");

-- 2. Managed Optimized Partitioned Table (Partitioned by Country and Reading Date)
DROP TABLE IF EXISTS partitioned_energy_readings;
CREATE TABLE IF NOT EXISTS partitioned_energy_readings (
    reading_id      STRING,
    meter_id        STRING,
    company_id      STRING,
    branch_name     STRING,
    reading_time    TIMESTAMP,
    energy_kwh      DOUBLE,
    voltage         DOUBLE,
    current_amp     DOUBLE,
    power_factor    DOUBLE
)
PARTITIONED BY (
    country_part    STRING,
    date_part       STRING
)
STORED AS ORC
TBLPROPERTIES (
    "orc.compress"="SNAPPY",
    "transactional"="false"
);

-- 3. Dynamic Partition Insertion from Raw External Data
SET hive.exec.dynamic.partition = true;
SET hive.exec.dynamic.partition.mode = nonstrict;

-- INSERT OVERWRITE TABLE partitioned_energy_readings
-- PARTITION (country_part, date_part)
-- SELECT
--     reading_id,
--     meter_id,
--     company_id,
--     branch_name,
--     reading_time,
--     energy_kwh,
--     voltage,
--     current_amp,
--     power_factor,
--     country AS country_part,
--     to_date(reading_time) AS date_part
-- FROM raw_energy_readings;

-- 4. Processed Country-Wise Aggregated Summary Table
DROP TABLE IF EXISTS country_energy_summary;
CREATE TABLE IF NOT EXISTS country_energy_summary (
    country                 STRING,
    total_consumption_kwh   DOUBLE,
    avg_consumption_kwh     DOUBLE,
    reading_count           BIGINT,
    tariff_rate             DOUBLE,
    currency                STRING,
    total_expenditure_local DOUBLE,
    last_updated            TIMESTAMP
)
STORED AS ORC;

-- 5. Processed Branch-Wise Aggregated Summary Table
DROP TABLE IF EXISTS branch_energy_summary;
CREATE TABLE IF NOT EXISTS branch_energy_summary (
    branch_name             STRING,
    country                 STRING,
    total_consumption_kwh   DOUBLE,
    avg_consumption_kwh     DOUBLE,
    max_peak_kwh            DOUBLE,
    min_kwh                 DOUBLE,
    reading_count           BIGINT
)
STORED AS ORC;

-- 6. Monthly Energy Trend Table
DROP TABLE IF EXISTS monthly_energy_summary;
CREATE TABLE IF NOT EXISTS monthly_energy_summary (
    year_month              STRING,
    country                 STRING,
    total_kwh               DOUBLE,
    avg_daily_kwh           DOUBLE,
    estimated_cost_local    DOUBLE
)
STORED AS ORC;

