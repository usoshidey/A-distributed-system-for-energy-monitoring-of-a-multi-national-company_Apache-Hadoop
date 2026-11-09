# Distributed Energy Monitoring System for a Multinational Company Using Apache Hadoop

[![Build & Test Status](https://img.shields.io/badge/pytest-24%20passed%20(100%25)-success)](file:///tests)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.15-blue)](file:///requirements.txt)
[![Big Data](https://img.shields.io/badge/Apache%20Hadoop-3.2.1-orange)](file:///hadoop)
[![Data Warehouse](https://img.shields.io/badge/Apache%20Hive-2.3.2-yellow)](file:///hive)
[![Frontend](https://img.shields.io/badge/Bootstrap%205-Chart.js-purple)](file:///frontend)

A comprehensive, production-grade distributed Big Data and web-based energy telemetry analytics platform engineered for a multinational corporation (**Apex Global Industries**) with operations spanning **India**, the **United States of America**, **Germany**, and **Japan**.

The platform collects, stores, processes, analyzes, and visualizes electricity telemetry across corporate offices and industrial factories using **Apache Hadoop HDFS**, **Java MapReduce**, **Apache Hive**, and a **Python/Flask REST backend** coupled with a modern **Bootstrap 5 & Chart.js** dashboard.

---

## Table of Contents
1. [Project Overview & Key Objectives](#1-project-overview--key-objectives)
2. [System Architecture](#2-system-architecture)
3. [Multinational Operating Entities](#3-multinational-operating-entities)
4. [Technology Stack](#4-technology-stack)
5. [Project Folder Hierarchy](#5-project-folder-hierarchy)
6. [Energy Data Generation & Telemetry Schema](#6-energy-data-generation--telemetry-schema)
7. [Apache Hadoop Integration & HDFS Storage](#7-apache-hadoop-integration--hdfs-storage)
8. [Java MapReduce Implementation](#8-java-mapreduce-implementation)
9. [Apache Hive Data Warehouse & Analytics](#9-apache-hive-data-warehouse--analytics)
10. [Electricity Tariff & Multinational Expenditure](#10-electricity-tariff--multinational-expenditure)
11. [Abnormal Consumption Anomaly Detection Engine](#11-abnormal-consumption-anomaly-detection-engine)
12. [Role-Based Access Control (RBAC) & Authentication](#12-role-based-access-control-rbac--authentication)
13. [Installation & Quickstart Guide](#13-installation--quickstart-guide)
14. [Running with Docker Compose](#14-running-with-docker-compose)
15. [Automated Test Suite & Verification](#15-automated-test-suite--verification)
16. [Troubleshooting & Diagnostics](#16-troubleshooting--diagnostics)
17. [Academic Demonstration / Viva Voce Walkthrough](#17-academic-demonstration--viva-voce-walkthrough)

---

## 1. Project Overview & Key Objectives

Modern multinational industrial conglomerates consume vast amounts of electrical power across geographically dispersed facilities. Monitoring and optimizing global energy footprint requires:
- High-throughput distributed ingestion capable of processing millions of smart meter data points.
- Reliable fault-tolerant distributed storage using **HDFS** partitioned by geography and chronological timestamps.
- Batch analytics pipelines using **Hadoop MapReduce** to aggregate gigawatt-hour loads per nation.
- High-level analytical ad-hoc query capabilities via **Apache Hive** for executive reporting and billing.
- Real-time automated **anomaly detection** alerting facility supervisors whenever an office or factory spikes beyond 1.5x baseline capacity.
- Consolidated executive dashboard with multi-currency conversion to local legal tenders (INR, USD, EUR, JPY) as well as global consolidated USD financials.

---

## 2. System Architecture

The system follows a multi-tier distributed architecture spanning edge data ingestion, distributed storage and computation, REST backend services, and browser interfaces.

```
+-----------------------------------------------------------------------------------+
|                            EDGE TELEMETRY INGESTION                               |
|   12,000+ IoT Smart Meter Readings (Kolkata, Mumbai, NYC, Fremont, Berlin, etc.)  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                         STORAGE & BIG DATA LAYER                                  |
|   HDFS:                                                                           |
|     /energy-monitoring/raw-data/         <-- Raw CSV Telemetry                    |
|     /energy-monitoring/processed-data/   <-- MapReduce Output                     |
|     /energy-monitoring/reports/          <-- Exported Summaries                   |
|                                                                                   |
|   COMPUTATION ENGINE:                                                             |
|     - Apache Hadoop YARN + Java MapReduce (EnergyMapper, EnergyReducer, Driver)   |
|     - Apache Hive Data Warehouse (ORC partitioned tables, Beeline JDBC)           |
|     - Verified Python MapReduce & SQL Fallback for Standalone Demonstration       |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                             BACKEND API LAYER (Flask)                             |
|   - ORM & Persistence: SQLAlchemy with SQLite / MySQL                             |
|   - Anomaly Detection: 1.5x Branch Baseline Evaluator & Alert Dispatcher          |
|   - Tariff & Currency: Multi-currency billing engine (INR, USD, EUR, JPY)         |
|   - REST API Endpoints: Dashboard, Countries, Branches, Telemetry, Reports, Auth |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                           PRESENTATION LAYER (Frontend)                           |
|   - HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js 4.4                            |
|   - Modern Executive Dark Blue & Crisp White Theme                                |
|   - 5 Interactive Analytical Charts & Live Telemetry Monitor                      |
+-----------------------------------------------------------------------------------+
```

---

## 3. Multinational Operating Entities

The corporation operates 9 primary branches distributed across 4 key economic zones:

| Country | Code | Branch Name | Facility Type | Active Meter IDs | Nominal Voltage | Baseline kWh Range |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **India** | IND | Kolkata Office | Office | `MTR-IND-KOL-01`, `02` | 230 V (1-phase) | 70 - 160 kWh |
| **India** | IND | Mumbai Factory | Factory | `MTR-IND-BOM-01`, `02`, `03` | 400 V (3-phase) | 450 - 950 kWh |
| **India** | IND | Delhi Office | Office | `MTR-IND-DEL-01`, `02` | 230 V (1-phase) | 80 - 190 kWh |
| **USA** | USA | New York Office | Office | `MTR-USA-NYC-01`, `02`, `03` | 120 V (1-phase) | 110 - 260 kWh |
| **USA** | USA | California Factory | Factory | `MTR-USA-CAL-01`, `02`, `03`, `04` | 480 V (3-phase) | 550 - 1200 kWh |
| **Germany** | DEU | Berlin Office | Office | `MTR-DEU-BER-01`, `02` | 230 V (1-phase) | 65 - 175 kWh |
| **Germany** | DEU | Munich Factory | Factory | `MTR-DEU-MUC-01`, `02`, `03` | 400 V (3-phase) | 480 - 1050 kWh |
| **Japan** | JPN | Tokyo Office | Office | `MTR-JPN-TYO-01`, `02` | 100 V (1-phase) | 85 - 210 kWh |
| **Japan** | JPN | Osaka Factory | Factory | `MTR-JPN-OSA-01`, `02`, `03` | 200 V (3-phase) | 420 - 980 kWh |

---

## 4. Technology Stack

- **Frontend**: HTML5, CSS3, ES6+ JavaScript, Bootstrap 5.3.2, Bootstrap Icons 1.11, Chart.js 4.4.
- **Backend**: Python 3.11+, Flask 3.1, Flask-CORS, RESTful Architecture.
- **Big Data Storage & Processing**:
  - Apache Hadoop 3.2.1 (HDFS, YARN ResourceManager, NodeManager).
  - Java MapReduce (Java 8/11/17, ToolRunner, Writable interfaces).
  - Apache Hive 2.3.2 / 3.1.2 (HiveQL, ORC format, external tables, partition pruning).
  - Integrated Python MapReduce & Query Fallback (ensures turnkey demonstration without requiring live multi-gigabyte Hadoop daemon RAM overhead).
- **Database**: SQLite (default turnkey local) or MySQL (configurable via `DATABASE_URL`), SQLAlchemy 2.0 ORM.
- **Testing**: `pytest` comprehensive test suite.

---

## 5. Project Folder Hierarchy

```
energy-monitoring-system/
│
├── frontend/
│   ├── index.html              # Entrypoint gateway
│   ├── login.html              # RBAC login & registration
│   ├── dashboard.html          # Executive Dark Blue & White dashboard
│   ├── countries.html          # Country-level consumption & local currency billing
│   ├── branches.html           # Branch registry & IoT smart meters
│   ├── energy-monitoring.html  # Live telemetry streaming & reading ingestion modal
│   ├── analytics.html          # Hadoop MapReduce & Hive SQL execution console
│   ├── alerts.html             # Anomaly monitoring (>1.5x average) & acknowledge
│   ├── reports.html            # Custom report builder & CSV export
│   ├── settings.html           # Electricity tariff editor & cluster diagnostics
│   ├── css/
│   │   └── styles.css          # Executive theme styles, cards, tables, badges
│   └── js/
│       ├── api.js              # Central API client & formatters
│       ├── dashboard.js        # 5 Chart.js charts & KPI loaders
│       ├── countries.js        # Country loader
│       ├── branches.js         # Branch directory
│       ├── energy-monitoring.js# Ingestion & live pagination
│       ├── analytics.js        # MapReduce & Hive runner
│       ├── alerts.js           # Anomaly acknowledgments
│       ├── reports.js          # CSV streaming & summary generator
│       └── settings.js         # Tariff configuration
│
├── backend/
│   ├── app.py                  # Flask entrypoint & static route dispatcher
│   ├── database.py             # SQLAlchemy engine & session manager
│   ├── init_db.py              # Schema generator, seeder & CSV ingester
│   ├── models.py               # 9 ORM models (User, Country, Branch, etc.)
│   ├── routes/
│   │   ├── __init__.py         # Blueprint registration
│   │   ├── auth_routes.py      # /api/auth (login, register, me, logout)
│   │   ├── dashboard_routes.py # /api/dashboard (KPIs, charts, summaries)
│   │   ├── country_routes.py   # /api/countries
│   │   ├── branch_routes.py    # /api/branches
│   │   ├── energy_routes.py    # /api/energy/readings (GET & POST)
│   │   ├── analytics_routes.py # /api/analytics (MR & Hive triggers)
│   │   ├── alert_routes.py     # /api/alerts & acknowledge
│   │   ├── report_routes.py    # /api/reports & CSV export
│   │   └── settings_routes.py  # /api/settings/tariffs & hadoop-status
│   └── services/
│       ├── __init__.py
│       ├── anomaly_service.py  # 1.5x baseline surge evaluator
│       ├── cost_service.py     # Multi-currency tariff calculator
│       ├── hadoop_service.py   # Hadoop cluster checker & MapReduce runner
│       ├── hive_service.py     # Hive SQL query executor
│       └── report_service.py   # CSV stream builder
│
├── hadoop/
│   ├── EnergyMapper.java       # Hadoop Java Mapper
│   ├── EnergyReducer.java      # Hadoop Java Reducer
│   ├── EnergyDriver.java       # Hadoop ToolRunner Driver
│   ├── mapper.py               # Hadoop Streaming Mapper
│   ├── reducer.py              # Hadoop Streaming Reducer
│   ├── hdfs_setup.sh           # Linux/Unix HDFS directory setup script
│   ├── run_mapreduce.sh        # Linux/Unix MapReduce compiler & runner
│   ├── hdfs_setup.bat          # Windows batch HDFS setup script
│   └── run_mapreduce.bat       # Windows batch MapReduce runner
│
├── hive/
│   ├── create_tables.hql       # Hive DDL (External, Partitioned ORC)
│   ├── analytics_queries.hql   # 7 HiveQL analytics queries
│   ├── run_hive.sh             # Linux Beeline/Hive script
│   └── run_hive.bat            # Windows Hive script
│
├── data/
│   ├── generate_data.py        # 12,000+ record telemetry generator
│   └── energy_data.csv         # Generated realistic dataset
│
├── reports/                    # Target directory for exported files
│
├── tests/
│   ├── test_auth.py            # RBAC & login tests
│   ├── test_data_generator.py  # Data schema & statistical distribution tests
│   ├── test_api.py             # REST API endpoint tests
│   ├── test_anomaly.py         # 1.5x anomaly detection tests
│   ├── test_hadoop_fallback.py # MapReduce & Hive pipeline tests
│   └── test_cost_calc.py       # Tariff and currency conversion tests
│
├── requirements.txt            # Python dependencies
├── README.md                   # Complete academic documentation
├── .env.example                # Environment variables template
├── hadoop.env                  # Docker Hadoop cluster configuration
├── Dockerfile                  # Application container definition
└── docker-compose.yml          # Hadoop + Hive + WebApp cluster deployment
```

---

## 6. Energy Data Generation & Telemetry Schema

The data generator (`data/generate_data.py`) generates timestamped, multi-month industrial telemetry adhering to real-world electrical physics:
- **Diurnal load variations**: Commercial offices peak between 08:00 and 19:00 on weekdays and drop during weekends.
- **Multi-shift industrial patterns**: Factories operate 2-3 shifts maintaining higher continuous base loads.
- **Electrical formulas**:
  $$\text{Current (Amperes)} = \frac{\text{Power (kW)} \times 1000}{\text{Voltage (V)} \times \text{Power Factor}}$$
- **Controlled Anomaly Injection**: A small calibrated percentage (~3.5%) of readings are artificially boosted to 1.6x - 2.4x branch baseline to test anomaly detection.

### Telemetry Record Format:
```csv
reading_id,meter_id,company_id,branch_name,country,timestamp,energy_kwh,voltage,current,power_factor
R-0000001,MTR-IND-KOL-01,COMP-001,Kolkata Office,India,2026-08-15 08:30:00,128.45,231.2,586.2,0.95
```

---

## 7. Apache Hadoop Integration & HDFS Storage

### HDFS Directory Structure
The platform utilizes standard HDFS directory segregation:
- `/energy-monitoring/raw-data/`: Holds raw smart meter CSV streams uploaded from the edge.
- `/energy-monitoring/processed-data/`: Destination for MapReduce job partition outputs (`part-r-00000`).
- `/energy-monitoring/reports/`: Staging directory for generated analytical summaries.

### HDFS Setup Commands (Linux / macOS / WSL)
```bash
# 1. Create HDFS directories
hdfs dfs -mkdir -p /energy-monitoring/raw-data
hdfs dfs -mkdir -p /energy-monitoring/processed-data
hdfs dfs -mkdir -p /energy-monitoring/reports

# 2. Upload raw telemetry data
hdfs dfs -put -f data/energy_data.csv /energy-monitoring/raw-data/energy_data.csv

# 3. Verify files on HDFS
hdfs dfs -ls -h /energy-monitoring/raw-data/
```

### Windows Batch Alternative
```cmd
hadoop\hdfs_setup.bat
```

---

## 8. Java MapReduce Implementation

The MapReduce implementation consists of three core classes:

1. **`EnergyMapper.java`**:
   - Implements `Mapper<LongWritable, Text, Text, DoubleWritable>`.
   - Skips CSV header row.
   - Extracts Country as `Text` key and `energy_kwh` as `DoubleWritable` value.
   - Discards malformed or corrupted records using Hadoop counters.

2. **`EnergyReducer.java`**:
   - Implements `Reducer<Text, DoubleWritable, Text, Text>`.
   - Groups consumption values by Country key.
   - Computes:
     - Total energy consumption ($kWh$)
     - Average energy consumption ($kWh$)
     - Total reading count ($N$)
   - Emits formatted tab-delimited records.

3. **`EnergyDriver.java`**:
   - Implements `Tool` and utilizes `ToolRunner`.
   - Configures input and output paths, Combiner, Mapper, and Reducer.
   - Deletes prior output directories automatically before submitting the job to YARN.

### Compiling and Running Java MapReduce on Cluster
```bash
cd hadoop
chmod +x run_mapreduce.sh
./run_mapreduce.sh
```

### Standalone / Local Fallback Guarantee
In environments where local Hadoop daemons are not running or Java is unavailable, the application backend (`backend/services/hadoop_service.py`) **honestly detects** that Hadoop is offline and invokes the exact Python MapReduce equivalent pipeline (`mapper.py` -> Shuffle/Sort -> `reducer.py`). It **never fakes** cluster execution and clearly reports:
`"engine": "Python MapReduce Simulation Engine (Local Fallback - Hadoop Cluster Offline)"`.

---

## 9. Apache Hive Data Warehouse & Analytics

Hive scripts located in `hive/` map external data directly from HDFS and create optimized columnar ORC tables partitioned by Country and Date.

### Schema DDL (`hive/create_tables.hql`)
- `raw_energy_readings`: External table located at `/energy-monitoring/raw-data`.
- `partitioned_energy_readings`: Managed ORC table partitioned by `country_part` and `date_part` with Snappy compression.
- `country_energy_summary`, `branch_energy_summary`, `monthly_energy_summary`: Optimized aggregation tables.

### Analytical Queries (`hive/analytics_queries.hql`)
1. **Total Global Energy Consumption**: Aggregate global sum, average, min, and max loads.
2. **Country-Wise Comparison**: Breakdown of consumption, standard deviation, and power factor per country.
3. **Branch-Wise Breakdown**: Facility-level totals, active meter count, and peak loads.
4. **Daily Average Consumption**: Time-series grouping by date and nation.
5. **Monthly Consumption**: Monthly aggregate trend.
6. **Highest Energy-Consuming Branch**: Window function utilizing `DENSE_RANK() OVER (ORDER BY SUM(energy_kwh) DESC)`.
7. **Electricity Expenditure**: Tariff calculations across national currencies.

---

## 10. Electricity Tariff & Multinational Expenditure

To reflect realistic multinational operational costs, each country is configured with its respective domestic tariff rate:

| Country | Configured Tariff | Currency Code | Symbol | USD Rate (Illustrative) |
| :--- | :--- | :--- | :--- | :--- |
| **India** | 8.00 INR / kWh | INR | ₹ | ~0.012 |
| **USA** | 0.15 USD / kWh | USD | $ | 1.000 |
| **Germany** | 0.30 EUR / kWh | EUR | € | ~1.080 |
| **Japan** | 30.00 JPY / kWh | JPY | ¥ | ~0.0067 |

> [!NOTE]
> All tariff values and currency conversion multipliers are clearly marked across the platform as **illustrative academic parameters**. Administrators can dynamically modify tariff rates in real time via the **Settings** panel (`/settings.html`).

---

## 11. Abnormal Consumption Anomaly Detection Engine

The anomaly detection engine enforces the rule:
$$\text{Threshold} = 1.5 \times \text{Baseline Average}_{\text{branch}}$$

$$\text{If } \text{Consumption} > \text{Threshold} \implies \text{Generate Alert}$$

### Severity Classification:
- **Warning**: $1.5\text{x} \le \text{Ratio} < 1.75\text{x}$ of baseline average.
- **High**: $1.75\text{x} \le \text{Ratio} < 2.0\text{x}$ of baseline average.
- **Critical**: $\text{Ratio} \ge 2.0\text{x}$ of baseline average.

Alert records display:
- Branch name & Country
- Current consumption ($kWh$) & Branch baseline average ($kWh$)
- Severity level & Ratio factor
- Timestamp
- Audit Status (`Pending` vs `Acknowledged`) with the name of the acknowledging supervisor.

---

## 12. Role-Based Access Control (RBAC) & Authentication

User accounts are secured with cryptographic password hashing (`pbkdf2:sha256` via Werkzeug):

| Username | Default Password | Role | Assigned Country | Scope of Authority |
| :--- | :--- | :--- | :--- | :--- |
| **`admin`** | `Admin@123` | `admin` | *Global (All)* | Full access: View all nations, execute Hadoop/Hive jobs, update tariffs, acknowledge any alert. |
| **`manager_in`** | `Manager@123` | `country_manager` | India | Regional manager: View India branches (Kolkata, Mumbai, Delhi) and acknowledge domestic alerts. |
| **`manager_us`** | `Manager@123` | `country_manager` | USA | Regional manager: USA facilities (New York, California). |
| **`manager_de`** | `Manager@123` | `country_manager` | Germany | Regional manager: Germany facilities (Berlin, Munich). |
| **`manager_jp`** | `Manager@123` | `country_manager` | Japan | Regional manager: Japan facilities (Tokyo, Osaka). |

---

## 13. Installation & Quickstart Guide

### Prerequisites
- Python 3.10+ (Python 3.11, 3.12, or 3.15 supported)
- Web browser (Chrome, Edge, Firefox)

### Step 1: Clone or Navigate to the Repository
```bash
cd C:\distributedAnalutics\energy-monitoring-system
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Initialize Database & Seed 12,000+ Telemetry Records
```bash
# Generates data/energy_data.csv (if not already generated) and populates the database
python backend/init_db.py
```
*Output: Seeds Master Company, 4 Countries, 9 Branches, 24 Smart Meters, ingests 12,000 readings, and registers ~120 baseline anomaly spikes in ~2.5 seconds.*

### Step 4: Run the Backend Application Server
```bash
python backend/app.py
```
*Server starts at `http://localhost:5000`.*

### Step 5: Access the Web Dashboard
Open your web browser and navigate to:
```
http://localhost:5000
```
- Click **"Sign In to Dashboard"** using the pre-configured buttons (`admin / Admin@123`).
- Explore the interactive charts, country summaries, live telemetry feed, Big Data analytics terminal, anomaly alerts, and report generator.

---

## 14. Running with Docker Compose

For environments with Docker Desktop or Linux Docker engines, spin up a full multi-container Apache Hadoop and Hive cluster with one command:

```bash
docker compose up -d
```

### Running Services:
- **`app`**: Web Application & Dashboard on port `5000`.
- **`hadoop-namenode`**: HDFS Namenode Web UI on port `9870`.
- **`hadoop-datanode`**: HDFS Datanode on port `9864`.
- **`hadoop-resourcemanager`**: YARN Web UI on port `8088`.
- **`hadoop-nodemanager`**: YARN NodeManager on port `8042`.
- **`hive-server`**: HiveServer2 on port `10000`.

---

## 15. Automated Test Suite & Verification

The project includes an end-to-end automated test suite verifying 100% of functional requirements:

```bash
python -m pytest tests/
```

### Test Suite Summary:
```
============================= test session starts =============================
collected 24 items

tests/test_anomaly.py ...                                                [ 12%]
tests/test_api.py ......                                                 [ 37%]
tests/test_auth.py ....                                                  [ 54%]
tests/test_cost_calc.py ...                                              [ 66%]
tests/test_data_generator.py ....                                        [ 83%]
tests/test_hadoop_fallback.py ....                                       [100%]

======================= 24 passed, 15 warnings in 2.45s =======================
```

### What is tested:
1. `test_auth.py`: User authentication, invalid password rejection, country manager access, and new account registration.
2. `test_data_generator.py`: Volume ($N \ge 10,000$), CSV schema compliance, and realistic electrical metrics.
3. `test_api.py`: REST endpoints (`/api/dashboard`, `/api/countries`, `/api/branches`, `/api/energy/readings`, `/api/reports`, etc.).
4. `test_anomaly.py`: Verification that surges $>1.5\text{x}$ baseline average generate alerts, normal readings pass without alerts, and administrator acknowledgment changes status.
5. `test_hadoop_fallback.py`: Execution of MapReduce pipeline (Map, Shuffle/Sort, Reduce) and Hive analytics.
6. `test_cost_calc.py`: Multi-currency tariff calculations for India, USA, Germany, and Japan.

---

## 16. Troubleshooting & Diagnostics

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **`javac` or `hadoop` not recognized** | Running on local machine without Hadoop binary in system `PATH`. | Expected for lightweight local dev. The application automatically detects this and uses the verified local MapReduce simulation engine with full transparency. Or use `docker compose up` for containerized cluster. |
| **Port 5000 is occupied** | Another service is using port 5000. | Set environment variable `PORT=5050` before starting `app.py`. |
| **Database file missing** | `energy_monitoring.db` not yet created. | Run `python backend/init_db.py` to regenerate schema and seed data. |
| **Anomalies not showing** | Filter set to "Acknowledged". | Select "All" or "Pending" in the severity and status filter dropdowns in `/alerts.html`. |

---

## 17. Academic Demonstration / Viva Voce Walkthrough

When presenting this project for an academic defense, final-year viva, or technical demonstration, follow this step-by-step sequence:

1. **Architecture & Problem Statement**:
   - Introduce **Apex Global Industries** operating in 4 countries with offices and factories.
   - Explain the challenge of processing massive volumes of energy readings and the need for Apache Hadoop.

2. **Executive Dashboard (`dashboard.html`)**:
   - Showcase the Dark Blue & Crisp White corporate UI.
   - Highlight the 6 primary KPIs: Global kWh, USD expenditure, Country count (4), Branch count (9), Top Country, and Active Alerts.
   - Walk through the 5 charts: Daily Trend, Monthly Aggregation, Country-wise Comparison, Branch-wise Horizontal Bar, and Energy Share Doughnut.

3. **Countries & Branch Directory (`countries.html` & `branches.html`)**:
   - Show domestic currency expenditures (INR ₹, USD $, EUR €, JPY ¥).
   - Show how offices vs factories differ in electrical load and voltage nominals.

4. **Live Ingestion & Anomaly Spikes (`energy-monitoring.html`)**:
   - Click **"+ Add Energy Reading"**.
   - Input normal load (e.g. 100 kWh for Kolkata Office) -> system verifies normal.
   - Input spike load (e.g. 450 kWh for Kolkata Office) -> instant alert popup triggers: *"🚨 ABNORMAL CONSUMPTION DETECTED! Reading exceeded 1.5x branch average"*.

5. **Big Data Processing Console (`analytics.html`)**:
   - Click **"Execute MapReduce Job"**: observe live terminal output detailing the Map Phase, Shuffle & Sort, and Reduce Aggregation.
   - Click **"Execute Hive Queries"**: show analytical queries aggregating data and calculating rank using `DENSE_RANK()`.

6. **Alerts & Administrative Acknowledgment (`alerts.html`)**:
   - Review pending alerts, filter by severity, and click **"Acknowledge"** as an administrator.

7. **Report Generation & CSV Export (`reports.html`)**:
   - Filter by country (e.g., India) and date range.
   - Click **"Export CSV"** to demonstrate downloadable reporting for company auditors.

---

**Developed for Academic Big Data Engineering Demonstration.**
*Apex Global Industries - Distributed Energy Monitoring Platform*

