import sys
import os
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import patch

# 1. Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.controllers.dashboard_controller import router
from app.api.dependencies import get_current_user_cpf

# 2. Setup the Test App
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# 3. Security Mocking
def mock_get_current_user_cpf():
    return "60440964083" 

app.dependency_overrides[get_current_user_cpf] = mock_get_current_user_cpf

# --- TEST CASES ---

def test_get_metrics_predefined_weekly():
    """TA.2: Success with predefined period (weekly)."""
    response = client.get("/metrics?period=weekly")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "activities-steps" in data
    assert "activities-heart" in data

def test_get_metrics_custom_period_success():
    """Scenario 4: Filter by a valid custom period."""
    
    mock_data = {
        "activities-steps": [{"dateTime": "2026-01-05", "value": "10000"}],
        "activities-heart": [],
        "sleep": []
    }

    with patch("app.controllers.dashboard_controller.get_dashboard_metrics", return_value=mock_data):
        response = client.get("/metrics?period=custom&start_date=2026-01-01&end_date=2026-01-05")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert len(data["activities-steps"]) > 0
    assert data["activities-steps"][0]["value"] == "10000"

def test_get_metrics_invalid_chronology():
    """Scenario 5 / TB.1: Start date greater than end date."""
    response = client.get("/metrics?period=custom&start_date=2026-01-10&end_date=2026-01-01")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Initial date cannot be greater than final date."

def test_get_metrics_missing_dates_for_custom():
    """Scenario 6: Using 'custom' period without providing dates."""
    response = client.get("/metrics?period=custom")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Initial and final dates are required" in response.json()["detail"]

def test_get_metrics_future_date_error():
    """Validation: Prevent filtering dates in the future."""
    response = client.get("/metrics?period=custom&start_date=2026-01-01&end_date=2029-12-31")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "The date cannot be later than today's date."

def test_get_metrics_performance_limit():
    """TB.2: Prevent periods longer than 365 days."""
    response = client.get("/metrics?period=custom&start_date=2024-01-01&end_date=2025-05-01")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot exceed 365 days" in response.json()["detail"]

def test_get_metrics_invalid_period_regex():
    """Validation: Only daily, weekly, monthly, or custom allowed."""
    response = client.get("/metrics?period=yearly")
    assert response.status_code == 422