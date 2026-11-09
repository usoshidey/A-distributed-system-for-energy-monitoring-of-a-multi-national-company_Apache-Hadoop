"""
Test Energy Data Generator schema, volume, and statistical distribution.
"""

import os
import csv
from data.generate_data import generate_records, export_to_csv, BRANCHES_CONFIG


def test_record_generation_count():
    records = generate_records(num_records=500, anomaly_rate=0.04)
    assert len(records) == 500


def test_record_schema():
    records = generate_records(num_records=50, anomaly_rate=0.0)
    rec = records[0]
    expected_fields = [
        "reading_id", "meter_id", "company_id", "branch_name",
        "country", "timestamp", "energy_kwh", "voltage", "current", "power_factor"
    ]
    for field in expected_fields:
        assert field in rec
        assert rec[field] is not None


def test_realistic_electrical_ranges():
    records = generate_records(num_records=200, anomaly_rate=0.0)
    for r in records:
        assert 0.80 <= r["power_factor"] <= 1.0
        assert r["energy_kwh"] > 0
        assert r["voltage"] >= 90.0
        assert r["current"] > 0
        assert r["country"] in ["India", "USA", "Germany", "Japan"]


def test_csv_export(tmp_path):
    records = generate_records(num_records=100, anomaly_rate=0.02)
    test_file = os.path.join(tmp_path, "test_energy.csv")
    export_to_csv(records, test_file)

    assert os.path.exists(test_file)
    with open(test_file, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        assert len(reader) == 100
        assert "energy_kwh" in reader[0]

