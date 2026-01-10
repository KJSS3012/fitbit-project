from unittest.mock import patch
from app.services.dashboard_service import get_dashboard_metrics

MOCK_RECORDS = [
    {"date": "2023-10-25", "steps": 8000, "bpm": 72, "sleep_hours": 7.5},
]

@patch("app.services.dashboard_service.FitbitModel")
def test_dashboard_fitbit_format_correctness(MockModel):
    MockModel.find_by_cpf.return_value = MOCK_RECORDS
    
    result = get_dashboard_metrics("12345678900", "daily")

    # Verifica chaves oficiais
    assert "activities-steps" in result
    assert "activities-heart" in result
    assert "sleep" in result

    # Verifica valores e conversões
    assert result["activities-steps"][0]["value"] == "8000"
    assert result["activities-heart"][0]["value"]["restingHeartRate"] == 72
    # 7.5 horas * 60 = 450 minutos
    assert result["sleep"][0]["minutesAsleep"] == 450

@patch("app.services.dashboard_service.FitbitModel")
def test_dashboard_empty_return(MockModel):
    MockModel.find_by_cpf.return_value = []
    result = get_dashboard_metrics("000", "daily")
    
    assert result["activities-steps"] == []
    assert len(result["sleep"]) == 0