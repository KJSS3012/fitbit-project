import sys
import os
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.controllers.dashboard_controller import router
from app.database.connection import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.patient import Patient

# ---------------- DATABASE SETUP ----------------

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base.metadata.create_all(bind=engine)

# ---------------- APP SETUP ----------------

app = FastAPI()
app.include_router(router, prefix="/dashboard")

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# ---------------- FIXTURES ----------------

@pytest.fixture
def test_patient():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    patient = Patient(
        cpf="60440964083",
        name="Test Patient",
        password=get_password_hash("TestPassword123!")
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    db.close()
    return patient

@pytest.fixture
def patient_token(test_patient):
    return create_access_token(
        subject=test_patient.cpf,
        user_type="patient"
    )

@pytest.fixture
def client():
    return TestClient(app)

# ---------------- TEST CASES ----------------

def test_get_metrics_predefined_weekly(client, patient_token):
    response = client.get(
        "/dashboard/metrics?period=weekly",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "activities-steps" in data
    assert "activities-heart" in data


def test_get_metrics_custom_period_success(client, patient_token):
    mock_data = {
        "activities-steps": [{"dateTime": "2026-01-05", "value": "10000"}],
        "activities-heart": [],
        "sleep": []
    }

    with patch(
        "app.controllers.dashboard_controller.get_dashboard_metrics",
        return_value=mock_data
    ):
        response = client.get(
            "/dashboard/metrics?period=custom&start_date=2026-01-01&end_date=2026-01-05",
            headers={"Authorization": f"Bearer {patient_token}"}
        )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["activities-steps"][0]["value"] == "10000"


def test_get_metrics_invalid_chronology(client, patient_token):
    response = client.get(
        "/dashboard/metrics?period=custom&start_date=2026-01-10&end_date=2026-01-01",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Initial date cannot be greater than final date."


def test_get_metrics_missing_dates_for_custom(client, patient_token):
    response = client.get(
        "/dashboard/metrics?period=custom",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 400
    assert "Initial and final dates are required" in response.json()["detail"]


def test_get_metrics_future_date_error(client, patient_token):
    response = client.get(
        "/dashboard/metrics?period=custom&start_date=2026-01-01&end_date=2029-12-31",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "The date cannot be later than today's date."


def test_get_metrics_performance_limit(client, patient_token):
    response = client.get(
        "/dashboard/metrics?period=custom&start_date=2024-01-01&end_date=2025-05-01",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 400
    assert "cannot exceed 365 days" in response.json()["detail"]


def test_get_metrics_invalid_period_regex(client, patient_token):
    response = client.get(
        "/dashboard/metrics?period=yearly",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 422
