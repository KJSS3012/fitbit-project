import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.services.dashboard_service import get_dashboard_metrics

# --- MOCK DATA ---
MOCK_RECORDS = [
    {"date": "2026-01-10", "steps": 8000, "bpm": 72, "sleep_hours": 7.5},
]

# --- TEST CASES ---

@patch("app.services.dashboard_service.FitbitModel.find_by_cpf_and_date")
def test_get_dashboard_metrics_format_and_calculation(mock_find):
    """Checks if Fitbit data conversion (steps to string, hours to minutes) is correct."""
    mock_find.return_value = MOCK_RECORDS
    
    result = get_dashboard_metrics("12345678900", "daily")

    assert "activities-steps" in result
    assert result["activities-steps"][0]["value"] == "8000"
    assert result["activities-heart"][0]["value"]["restingHeartRate"] == 72
    assert result["sleep"][0]["minutesAsleep"] == 450 # 7.5 * 60

@patch("app.services.dashboard_service.FitbitModel.find_by_cpf_and_date")
def test_get_dashboard_metrics_empty_db(mock_find):
    """Ensures empty lists are returned when no data is found (Standard 200 OK behavior)."""
    mock_find.return_value = []
    
    result = get_dashboard_metrics("00000000000", "weekly")
    
    assert result["activities-steps"] == []
    assert result["activities-heart"] == []
    assert result["sleep"] == []

def test_error_start_date_greater_than_end_date():
    """TB.1: Validates that initial date cannot be after final date."""
    with pytest.raises(HTTPException) as exc:
        get_dashboard_metrics(
            cpf="123", 
            period="custom", 
            start_date="2026-01-10", 
            end_date="2026-01-01"
        )
    assert exc.value.status_code == 400
    assert "Initial date cannot be greater than final date" in exc.value.detail

def test_error_future_date():
    """Validation: Prevents filtering dates beyond today."""
    future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    with pytest.raises(HTTPException) as exc:
        get_dashboard_metrics(
            cpf="123", 
            period="custom", 
            start_date="2026-01-01", 
            end_date=future_date
        )
    assert exc.value.status_code == 400
    assert "cannot be later than today" in exc.value.detail

def test_error_custom_period_missing_dates():
    """Scenario 6: Ensures 'custom' period fails without date parameters."""
    with pytest.raises(HTTPException) as exc:
        get_dashboard_metrics(cpf="123", period="custom")
    assert exc.value.status_code == 400
    assert "Initial and final dates are required" in exc.value.detail

def test_error_performance_limit_exceeded():
    """TB.2: Validates the 365-day performance limit for custom queries."""
    with pytest.raises(HTTPException) as exc:
        get_dashboard_metrics(
            cpf="123", 
            period="custom", 
            start_date="2020-01-01", 
            end_date="2022-01-01"
        )
    assert exc.value.status_code == 400
    assert "cannot exceed 365 days" in exc.value.detail

def test_error_invalid_period_name():
    """Validation: Rejects periods that are not daily, weekly, monthly, or custom."""
    with pytest.raises(HTTPException) as exc:
        get_dashboard_metrics(cpf="123", period="yearly")
    assert exc.value.status_code == 400
    assert "Invalid period" in exc.value.detail