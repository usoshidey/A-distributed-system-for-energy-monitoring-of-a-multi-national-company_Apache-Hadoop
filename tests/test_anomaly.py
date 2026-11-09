"""
Test Abnormal Consumption Anomaly Detection and Acknowledgment Workflow.
"""

import pytest
from backend.app import create_app
from backend.database import SessionLocal
from backend.models import EnergyAlert


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_anomaly_detection_trigger(client):
    # Kolkata Office average baseline is ~115 kWh
    # Post a severe spike of 450 kWh (> 3.5x average)
    payload = {
        "branch_name": "Kolkata Office",
        "meter_code": "MTR-IND-KOL-01",
        "timestamp": "2026-11-10 11:30:00",
        "energy_kwh": 485.0,  # Critical anomaly spike
        "voltage": 228.0,
        "power_factor": 0.88
    }
    res = client.post("/api/energy/readings", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["anomaly_detected"] is True
    assert data["alert"] is not None
    assert data["alert"]["current_kwh"] == 485.0
    assert data["alert"]["ratio"] > 1.5
    assert data["alert"]["status"] == "Pending"


def test_normal_reading_no_anomaly(client):
    # Post standard consumption for Kolkata office (~100 kWh)
    payload = {
        "branch_name": "Kolkata Office",
        "meter_code": "MTR-IND-KOL-01",
        "timestamp": "2026-11-10 11:45:00",
        "energy_kwh": 105.0,
        "voltage": 230.0,
        "power_factor": 0.95
    }
    res = client.post("/api/energy/readings", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["anomaly_detected"] is False
    assert data["alert"] is None


def test_acknowledge_alert(client):
    db = SessionLocal()
    pending = db.query(EnergyAlert).filter_by(status="Pending").first()
    assert pending is not None
    alert_id = pending.id
    db.close()

    res = client.post("/api/alerts/acknowledge", json={
        "alert_id": alert_id,
        "acknowledged_by": "Test Operator"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["alert"]["status"] == "Acknowledged"
    assert data["alert"]["acknowledged_by"] == "Test Operator"

