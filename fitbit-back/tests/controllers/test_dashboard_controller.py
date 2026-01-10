import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.controllers.dashboard_controller import router
from app.database.connection import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.models.patient import Patient

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Setup app
app = FastAPI()
app.include_router(router)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def test_patient():
    """Create a test patient in the database."""
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
    """Generate JWT token for test patient."""
    return create_access_token(subject=test_patient.cpf, user_type="patient")

@pytest.fixture
def client():
    """Fixture that provides a TestClient for the FastAPI app."""
    return TestClient(app)

# --- TEST CASES ---

def test_get_metrics_predefined_weekly(client, patient_token):
    """TA.2: Success with predefined period (weekly)."""
    response = client.get(
        "/metrics?period=weekly",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "activities-steps" in data
    assert "activities-heart" in data
    assert "sleep" in data

def test_get_metrics_custom_period_success(client, patient_token):
    """Scenario 4: Filter by a valid custom period."""
    response = client.get(
        "/metrics?period=custom&start_date=2026-01-01&end_date=2026-01-05",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    # Should find the record from 2026-01-05 (ID 25)
    assert "activities-steps" in data

def test_get_metrics_invalid_chronology(client, patient_token):
    """Scenario 5 / TB.1: Start date greater than end date."""
    response = client.get(
        "/metrics?period=custom&start_date=2026-01-10&end_date=2026-01-01",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Initial date cannot be greater than final date."

def test_get_metrics_missing_dates_for_custom(client, patient_token):
    """Scenario 6: Using 'custom' period without providing dates."""
    response = client.get(
        "/metrics?period=custom",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 400
    assert "Initial and final dates are required" in response.json()["detail"]

def test_get_metrics_future_date_error(client, patient_token):
    """Validation: Prevent filtering dates in the future."""
    response = client.get(
        "/metrics?period=custom&start_date=2026-01-01&end_date=2029-12-31",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "The date cannot be later than today's date."

def test_get_metrics_performance_limit(client, patient_token):
    """TB.2: Prevent periods longer than 365 days."""
    response = client.get(
        "/metrics?period=custom&start_date=2024-01-01&end_date=2025-05-01",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 400
    assert "cannot exceed 365 days" in response.json()["detail"]

def test_get_metrics_invalid_period_regex(client, patient_token):
    """Validation: Only daily, weekly, monthly, or custom allowed."""
    response = client.get(
        "/metrics?period=yearly",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert response.status_code == 422 # FastAPI built-in validation