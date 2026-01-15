"""
Tests for /fitbit/sync endpoint and metrics persistence
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.models.patient import Patient
from app.models.patient_metrics import PatientMetrics
from app.api.dependencies import get_cpf_from_header
from app.controllers.fitbit_controller import router as fitbit_router


def create_test_app():
    """Create isolated test app"""
    test_app = FastAPI()
    
    def override_get_cpf_from_header():
        return "12345678901"
    
    test_app.dependency_overrides[get_cpf_from_header] = override_get_cpf_from_header
    test_app.include_router(fitbit_router, prefix="/fitbit")
    
    return test_app


client = TestClient(create_test_app(), raise_server_exceptions=False)


class TestFitbitSync:
    """Tests for Fitbit sync endpoint"""

    @patch('app.controllers.fitbit_controller.requests.get')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    @patch('app.repositories.patient_repository.PatientRepository.save_metrics')
    def test_sync_success_saves_to_database(self, mock_save_metrics, mock_find_cpf, mock_get):
        """DADO Fitbit conectado
        QUANDO POST /fitbit/sync
        ENTÃO busca dados Fitbit dos últimos 7 dias E salva no BD E retorna sucesso"""
        
        # Mock patient with valid token
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.fitbit_access_token = "valid_token"
        mock_patient.fitbit_refresh_token = "refresh_token"
        mock_find_cpf.return_value = mock_patient
        
        # Mock Fitbit API responses for 7 days (3 calls per day: activity, heart, sleep)
        api_responses = []
        for day in range(7):
            api_responses.extend([
                # Activity response
                Mock(status_code=200, json=lambda d=day: {"summary": {"steps": 10000 + d * 100, "caloriesOut": 2500}}),
                # Heartrate response
                Mock(status_code=200, json=lambda: {"activities-heart": [{"value": {"restingHeartRate": 72}}]}),
                # Sleep response
                Mock(status_code=200, json=lambda: {"summary": {"totalMinutesAsleep": 420}})
            ])
        
        mock_get.side_effect = api_responses
        
        # Mock save_metrics to return list for each call
        mock_metric = Mock(spec=PatientMetrics)
        mock_save_metrics.return_value = [mock_metric]
        
        response = client.post("/fitbit/sync")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "7 dias" in data["message"]
        assert "date_range" in data
        assert "start" in data["date_range"]
        assert "end" in data["date_range"]
        assert len(data["data"]) == 7  # Should have 7 days of data
        assert data["metrics_saved"] == 7  # Should have saved 7 metrics
        
        # Verify save_metrics was called 7 times (once per day)
        assert mock_save_metrics.call_count == 7

    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_sync_fitbit_not_connected_401(self, mock_find_cpf):
        """DADO Fitbit não conectado
        QUANDO POST /fitbit/sync
        ENTÃO retorna 401 'Fitbit não conectado'"""
        
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.fitbit_access_token = None
        mock_find_cpf.return_value = mock_patient
        
        response = client.post("/fitbit/sync")
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Fitbit não conectado"

    @patch('app.controllers.fitbit_controller.requests.get')
    @patch('app.controllers.fitbit_controller.requests.post')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    @patch('app.repositories.patient_repository.PatientRepository.update_fitbit_tokens')
    @patch('app.repositories.patient_repository.PatientRepository.save_metrics')
    def test_sync_token_expired_401_with_refresh(self, mock_save, mock_update_tokens, mock_find_cpf, mock_post, mock_get):
        """DADO token expirado
        QUANDO POST /fitbit/sync
        ENTÃO faz refresh do token E retenta E salva dados dos 7 dias"""
        
        # Mock patient with expired token
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.fitbit_access_token = "expired_token"
        mock_patient.fitbit_refresh_token = "refresh_token"
        
        # Mock patient with new token after refresh
        mock_patient_refreshed = Mock(spec=Patient)
        mock_patient_refreshed.cpf = "12345678901"
        mock_patient_refreshed.fitbit_access_token = "new_token"
        mock_patient_refreshed.fitbit_refresh_token = "refresh_token"
        
        # Multiple calls to find_by_cpf for 7 days of syncing
        mock_find_cpf.side_effect = [mock_patient] + [mock_patient_refreshed] * 21  # 1 initial + 3 calls per day * 7 days
        
        # Mock refresh token success
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"access_token": "new_token", "refresh_token": "refresh_token", "expires_in": 3600}
        )
        
        mock_update_tokens.return_value = mock_patient_refreshed
        
        # First call returns 401 (expired), then 7 days of successful calls (3 per day)
        api_responses = [Mock(status_code=401)]  # Expired token
        for day in range(7):
            api_responses.extend([
                # Activity
                Mock(status_code=200, json=lambda: {"summary": {"steps": 8000, "caloriesOut": 2000}}),
                # Heartrate
                Mock(status_code=200, json=lambda: {"activities-heart": [{"value": {"restingHeartRate": 70}}]}),
                # Sleep
                Mock(status_code=200, json=lambda: {"summary": {"totalMinutesAsleep": 400}})
            ])
        
        mock_get.side_effect = api_responses
        mock_save.return_value = [Mock(spec=PatientMetrics)]
        
        response = client.post("/fitbit/sync")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 7  # 7 days of data
        
        # Verify refresh was attempted
        mock_post.assert_called_once()
        mock_update_tokens.assert_called_once()
        # Verify save was called 7 times (once per day)
        assert mock_save.call_count == 7

    @patch('app.controllers.fitbit_controller.requests.get')
    @patch('app.controllers.fitbit_controller.requests.post')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_sync_token_expired_refresh_fails_401(self, mock_find_cpf, mock_post, mock_get):
        """DADO token expirado E refresh falha
        QUANDO POST /fitbit/sync
        ENTÃO retorna 401 'Conexão Fitbit expirou. Reconecte'"""
        
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.fitbit_access_token = "expired_token"
        mock_patient.fitbit_refresh_token = "invalid_refresh_token"
        mock_find_cpf.return_value = mock_patient
        
        # Mock Fitbit API returning 401
        mock_get.return_value = Mock(status_code=401)
        
        # Mock refresh token failure
        mock_post.return_value = Mock(status_code=401)
        
        response = client.post("/fitbit/sync")
        
        assert response.status_code == 401
        assert "expirou" in response.json()["detail"].lower()
        assert "reconecte" in response.json()["detail"].lower()

    @patch('app.controllers.fitbit_controller.requests.get')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_sync_network_error_500(self, mock_find_cpf, mock_get):
        """DADO erro de rede no Fitbit para todos os dias
        QUANDO POST /fitbit/sync
        ENTÃO retorna 200 com dados marcados com erro (comportamento resiliente)"""
        
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.fitbit_access_token = "valid_token"
        mock_find_cpf.return_value = mock_patient
        
        # Simulate network error
        mock_get.side_effect = Exception("Network timeout")
        
        response = client.post("/fitbit/sync")
        
        # Should still return 200 but with errors in data
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # All 7 days should have error markers
        assert len(data["data"]) == 7
        # Check that errors are recorded
        errors_count = sum(1 for d in data["data"] if "error" in d)
        assert errors_count == 7
        assert data["metrics_saved"] == 0  # No metrics saved due to errors
