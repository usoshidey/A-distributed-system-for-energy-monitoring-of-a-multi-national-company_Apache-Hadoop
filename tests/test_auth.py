"""
Test User Authentication and Role-based Access Control.
"""

import pytest
from backend.app import create_app
from backend.database import SessionLocal
from backend.models import User


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_login_success(client):
    res = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "Admin@123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["role"] == "admin"


def test_login_invalid_password(client):
    res = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "WrongPassword999"
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False


def test_country_manager_login(client):
    res = client.post("/api/auth/login", json={
        "username": "manager_in",
        "password": "Manager@123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["user"]["role"] == "country_manager"
    assert data["user"]["assigned_country"] == "India"


def test_user_registration(client):
    import time
    uname = f"test_mgr_{int(time.time())}"
    res = client.post("/api/auth/register", json={
        "username": uname,
        "email": f"{uname}@test.com",
        "password": "SecretPassword@123",
        "full_name": "Test Regional Supervisor",
        "role": "country_manager",
        "assigned_country": "Germany"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["username"] == uname

