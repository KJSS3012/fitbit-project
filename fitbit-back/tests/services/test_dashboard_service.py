from app.services.dashboard_service import get_dashboard_metrics

def test_dashboard_calculation_correctness():
    """
    Scenario: Valid CPF '12345678900' (present in mock with 3 records).
    Expected Result: Steps, BPM, and Sleep averages must be exact integers/floats based on the mock data.
    """
    cpf = "12345678900"
    result = get_dashboard_metrics(cpf, period="daily")

    # Manual calculations based on mock.py data:
    # Steps: (8000 + 10200 + 5000) / 3 = 23200 / 3 = 7733.33 -> int(7733)
    assert result["summary"]["avg_steps"] == 7733
    
    # BPM: (72 + 78 + 68) / 3 = 218 / 3 = 72.66 -> int(72)
    assert result["summary"]["avg_bpm"] == 72
    
    # Sleep: (7.5 + 6.0 + 8.0) / 3 = 21.5 / 3 = 7.16 -> round(7.2)
    assert result["summary"]["avg_sleep"] == 7.2
    
    # Count check
    assert result["summary"]["days_analyzed"] == 3

def test_dashboard_chart_data_consistency():
    """
    Scenario: Requesting chart data.
    Expected Result: All data arrays (steps, dates, bpm) must have the exact same length to prevent frontend errors.
    """
    cpf = "12345678900"
    result = get_dashboard_metrics(cpf, period="daily")
    
    charts = result["charts"]
    dates_qty = len(charts["dates"])
    
    assert len(charts["steps"]) == dates_qty
    assert len(charts["bpm"]) == dates_qty
    assert len(charts["sleep"]) == dates_qty
    
    # Verify order preservation (first date from mock)
    assert charts["dates"][0] == "2023-10-25"
    assert charts["steps"][0] == 8000

def test_dashboard_empty_user():
    """
    Scenario: A CPF that does not exist in the database.
    Expected Result: Should return zeroed values and empty lists without raising exceptions (e.g., division by zero).
    """
    result = get_dashboard_metrics("00000000000", period="daily")
    
    assert result["summary"]["days_analyzed"] == 0
    assert result["summary"]["avg_steps"] == 0
    assert result["charts"]["dates"] == []