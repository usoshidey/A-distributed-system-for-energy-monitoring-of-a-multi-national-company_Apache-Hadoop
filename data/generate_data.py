#!/usr/bin/env python3
"""
Energy Data Generator
Generates realistic, timestamped energy consumption readings for a multinational corporation
operating in India, USA, Germany, and Japan across offices and industrial manufacturing facilities.
"""

import os
import csv
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(DATA_DIR, "energy_data.csv")

COMPANY_ID = "COMP-001"
COMPANY_NAME = "Apex Global Industries"

BRANCHES_CONFIG = [
    # India (3 branches)
    {
        "country": "India",
        "branch": "Kolkata Office",
        "type": "office",
        "meters": ["MTR-IND-KOL-01", "MTR-IND-KOL-02"],
        "base_kwh": (70, 160),
        "voltage_range": (220, 240),
        "nominal_voltage": 230
    },
    {
        "country": "India",
        "branch": "Mumbai Factory",
        "type": "factory",
        "meters": ["MTR-IND-BOM-01", "MTR-IND-BOM-02", "MTR-IND-BOM-03"],
        "base_kwh": (450, 950),
        "voltage_range": (390, 420),
        "nominal_voltage": 400
    },
    {
        "country": "India",
        "branch": "Delhi Office",
        "type": "office",
        "meters": ["MTR-IND-DEL-01", "MTR-IND-DEL-02"],
        "base_kwh": (80, 190),
        "voltage_range": (220, 240),
        "nominal_voltage": 230
    },

    # USA (2 branches)
    {
        "country": "USA",
        "branch": "New York Office",
        "type": "office",
        "meters": ["MTR-USA-NYC-01", "MTR-USA-NYC-02", "MTR-USA-NYC-03"],
        "base_kwh": (110, 260),
        "voltage_range": (110, 125),
        "nominal_voltage": 120
    },
    {
        "country": "USA",
        "branch": "California Factory",
        "type": "factory",
        "meters": ["MTR-USA-CAL-01", "MTR-USA-CAL-02", "MTR-USA-CAL-03", "MTR-USA-CAL-04"],
        "base_kwh": (550, 1200),
        "voltage_range": (460, 490),
        "nominal_voltage": 480
    },

    # Germany (2 branches)
    {
        "country": "Germany",
        "branch": "Berlin Office",
        "type": "office",
        "meters": ["MTR-DEU-BER-01", "MTR-DEU-BER-02"],
        "base_kwh": (65, 175),
        "voltage_range": (225, 238),
        "nominal_voltage": 230
    },
    {
        "country": "Germany",
        "branch": "Munich Factory",
        "type": "factory",
        "meters": ["MTR-DEU-MUC-01", "MTR-DEU-MUC-02", "MTR-DEU-MUC-03"],
        "base_kwh": (480, 1050),
        "voltage_range": (390, 415),
        "nominal_voltage": 400
    },

    # Japan (2 branches)
    {
        "country": "Japan",
        "branch": "Tokyo Office",
        "type": "office",
        "meters": ["MTR-JPN-TYO-01", "MTR-JPN-TYO-02"],
        "base_kwh": (85, 210),
        "voltage_range": (95, 108),
        "nominal_voltage": 100
    },
    {
        "country": "Japan",
        "branch": "Osaka Factory",
        "type": "factory",
        "meters": ["MTR-JPN-OSA-01", "MTR-JPN-OSA-02", "MTR-JPN-OSA-03"],
        "base_kwh": (420, 980),
        "voltage_range": (190, 215),
        "nominal_voltage": 200
    }
]


def generate_records(num_records=12000, anomaly_rate=0.03):
    """
    Generate realistic energy readings over the past 90 days.
    Simulates:
    - Diurnal work hour curves for offices (peaking 9 AM - 6 PM)
    - Multi-shift operations for factories
    - Realistic power factor (0.85 - 0.98)
    - Voltage and current relationship (Current ~ kWh * 1000 / (Voltage * PF))
    - Controlled anomaly spikes (> 1.5x average) for anomaly detection verification
    """
    random.seed(42)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    total_seconds = int((end_date - start_date).total_seconds())

    records = []
    
    # Calculate approximate branch averages to calibrate anomaly threshold
    branch_averages = {}
    for cfg in BRANCHES_CONFIG:
        avg_base = (cfg["base_kwh"][0] + cfg["base_kwh"][1]) / 2.0
        branch_averages[cfg["branch"]] = avg_base

    print(f"Generating {num_records} energy reading records...")

    for i in range(1, num_records + 1):
        # Pick random branch configuration
        cfg = random.choice(BRANCHES_CONFIG)
        branch = cfg["branch"]
        country = cfg["country"]
        meter_id = random.choice(cfg["meters"])
        reading_id = f"R-{i:07d}"

        # Generate realistic random timestamp within the past 90 days
        rand_sec = random.randint(0, total_seconds)
        ts = start_date + timedelta(seconds=rand_sec)
        hour = ts.hour
        is_weekend = ts.weekday() >= 5

        # Base load calculation
        low, high = cfg["base_kwh"]
        kwh = random.uniform(low, high)

        # Apply diurnal office patterns or factory shifts
        if cfg["type"] == "office":
            if 8 <= hour <= 19 and not is_weekend:
                # Business hours peak load
                kwh *= random.uniform(1.1, 1.4)
            elif is_weekend:
                # Weekend low load (standby servers, security, HVAC min)
                kwh *= random.uniform(0.3, 0.5)
            else:
                # Night hours
                kwh *= random.uniform(0.35, 0.6)
        else:
            # Factory: 2-3 shifts
            if 6 <= hour <= 22:
                kwh *= random.uniform(1.05, 1.25)
            else:
                kwh *= random.uniform(0.75, 0.95)

        # Check if this record should be an anomaly spike (> 1.5x of branch normal)
        is_anomaly = random.random() < anomaly_rate
        if is_anomaly:
            spike_factor = random.uniform(1.65, 2.45)
            kwh = branch_averages[branch] * spike_factor

        # Electrical attributes
        v_min, v_max = cfg["voltage_range"]
        voltage = round(random.uniform(v_min, v_max), 2)
        power_factor = round(random.uniform(0.85, 0.98), 2)
        
        # Calculate current: I = (P_kW * 1000) / (V * PF)
        current = round((kwh * 1000.0) / (voltage * power_factor), 2)
        kwh = round(kwh, 2)

        records.append({
            "reading_id": reading_id,
            "meter_id": meter_id,
            "company_id": COMPANY_ID,
            "branch_name": branch,
            "country": country,
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "energy_kwh": kwh,
            "voltage": voltage,
            "current": current,
            "power_factor": power_factor
        })

    # Sort chronological for realistic time series ingestion
    records.sort(key=lambda x: x["timestamp"])

    return records


def export_to_csv(records, filepath=OUTPUT_FILE):
    """Save records to CSV with exact header format required for HDFS & Hive ingestion."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fieldnames = [
        "reading_id",
        "meter_id",
        "company_id",
        "branch_name",
        "country",
        "timestamp",
        "energy_kwh",
        "voltage",
        "current",
        "power_factor"
    ]
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Successfully generated and wrote {len(records)} records to {filepath}")


if __name__ == "__main__":
    records = generate_records(num_records=12000, anomaly_rate=0.035)
    export_to_csv(records)

