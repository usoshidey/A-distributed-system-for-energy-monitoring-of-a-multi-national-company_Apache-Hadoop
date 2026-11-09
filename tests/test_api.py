"""
Test Backend REST API endpoints.
"""

import pytest
from backend.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_dashboard_endpoint(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.get_json()

    assert "kpi" in data
    assert "charts" in data
    assert "expenditure_breakdown" in data
    assert "recent_readings" in data

    # Verify key dashboard stats
    assert data["kpi"]["total_countries"] == 4
    assert data["kpi"]["total_branches"] == 9
    assert data["kpi"]["total_consumption_kwh"] > 0
    assert data["kpi"]["total_expenditure_usd"] > 0
    assert len(data["charts"]["daily"]["labels"]) > 0


def test_countries_endpoint(client):
    res = client.get("/api/countries")
    assert res.status_code == 200
    data = res.get_json()
    assert "countries" in data
    assert len(data["countries"]) == 4

    country_names = [c["name"] for c in data["countries"]]
    for expected in ["India", "USA", "Germany", "Japan"]:
        assert expected in country_names


def test_branches_endpoint(client):
    res = client.get("/api/branches")
    assert res.status_code == 200
    data = res.get_json()
    assert "branches" in data
    assert len(data["branches"]) == 9

    branch_names = [b["name"] for b in data["branches"]]
    assert "Kolkata Office" in branch_names
    assert "California Factory" in branch_names
    assert "Munich Factory" in branch_names
    assert "Tokyo Office" in branch_names


def test_energy_readings_query(client):
    res = client.get("/api/energy/readings?limit=25")
    assert res.status_code == 200
    data = res.get_json()
    assert "readings" in data
    assert len(data["readings"]) == 25
    assert data["total"] >= 10000


def test_energy_reading_ingestion(client):
    payload = {
        "branch_name": "Kolkata Office",
        "meter_code": "MTR-IND-KOL-01",
        "timestamp": "2026-11-10 10:00:00",
        "energy_kwh": 95.5,
        "voltage": 232.0,
        "power_factor": 0.94
    }
    res = client.post("/api/energy/readings", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["reading"]["energy_kwh"] == 95.5


def test_reports_filter_and_export(client):
    res = client.get("/api/reports?country=India&limit=50")
    assert res.status_code == 200
    data = res.get_json()
    assert "summary" in data
    assert "data" in data
    assert data["summary"]["filters"]["country"] == "India"

    # Test CSV export
    export_res = client.get("/api/reports/export?country=India")
    assert export_res.status_code == 200
    assert "text/csv" in export_res.content_type
    assert b"reading_id,meter_code,branch_name" in export_res.data

