import pytest
from unittest.mock import patch
from fastapi import HTTPException
from app.services.dashboard_service import get_dashboard_metrics

# --- DATA MOCK ---
MOCK_30_DAYS = [
    {"date": f"2026-01-{i:02d}", "steps": 1000, "bpm": 70, "sleep_hours": 8}
    for i in range(1, 31)
]

MOCK_3_DAYS = MOCK_30_DAYS[:3]

# --- TESTS ---

@patch("app.services.dashboard_service.get_cached_data")
def test_alternation_of_periods_values(mock_cache):
    """Validates that changing the period parameter alters the returned data."""
    mock_cache.return_value = [MOCK_30_DAYS[0]]
    res_daily = get_dashboard_metrics("123", period="daily")
    
    mock_cache.return_value = MOCK_30_DAYS[:7]
    res_weekly = get_dashboard_metrics("123", period="weekly")

    assert len(res_daily["activities-steps"]) == 1
    assert len(res_weekly["activities-steps"]) == 7
    assert res_daily != res_weekly

@patch("app.services.dashboard_service.get_cached_data")
def test_aggregation_precision_monthly(mock_cache):
    """Validates aggregation accuracy for monthly view (weekly averages)."""
    mock_cache.return_value = MOCK_30_DAYS 
    
    result = get_dashboard_metrics("123", period="monthly")
    
    first_week = result["activities-steps"][0]
    
    assert first_week["dateTime"] == "Week 1"
    assert first_week["value"] == "7000"
    
    assert result["activities-heart"][0]["value"]["restingHeartRate"] == 70

@patch("app.services.dashboard_service.get_cached_data")
def test_insufficient_data_block(mock_cache):
    """Validates that monthly view is blocked if less than 7 records exist."""
    mock_cache.return_value = MOCK_3_DAYS
    
    with pytest.raises(HTTPException) as exc:
        get_dashboard_metrics("123", period="monthly")
    
    assert exc.value.status_code == 400
    assert "São necessários pelo menos 7 registros" in exc.value.detail

@patch("app.services.dashboard_service.get_cached_data")
def test_consistency_unit_conversion(mock_cache):
    """Validates consistency in unit conversions (hours to minutes for sleep)."""
    mock_cache.return_value = [MOCK_30_DAYS[0]] # 8 hours of sleep
    
    result = get_dashboard_metrics("123", period="daily")
    
    # 8 hours * 60 = 480 minutes
    assert result["sleep"][0]["minutesAsleep"] == 480