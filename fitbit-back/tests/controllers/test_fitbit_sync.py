"""
Tests for /fitbit/sync endpoint and metrics persistence
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.models.patient import Patient
from app.models.patient_metrics import PatientMetrics
from app.core.security import get_current_user_cpf
from app.controllers.fitbit_controller import router as fitbit_router


def create_test_app():
    """Create isolated test app"""
    test_app = FastAPI()
    
    def override_get_current_user_cpf():
        return "12345678901"
    
    test_app.dependency_overrides[get_current_user_cpf] = override_get_current_user_cpf
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
        ENTÃO busca dados Fitbit E salva no BD E retorna sucesso"""
        
        # Mock patient with valid token
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.fitbit_access_token = "valid_token"
        mock_patient.fitbit_refresh_token = "refresh_token"
        mock_find_cpf.return_value = mock_patient
        
        # Mock Fitbit API responses
        mock_get.side_effect = [
            # Activity response
            Mock(status_code=200, json=lambda: {"summary": {"steps": 10000, "caloriesOut": 2500}}),
            # Heartrate response
            Mock(status_code=200, json=lambda: {"activities-heart": [{"value": {"restingHeartRate": 72}}]}),
            # Sleep response
            Mock(status_code=200, json=lambda: {"summary": {"totalMinutesAsleep": 420}})
        ]
        
        # Mock save_metrics
        mock_metric = Mock(spec=PatientMetrics)
        mock_save_metrics.return_value = [mock_metric]
        
        response = client.post("/fitbit/sync?day=2026-01-10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Dados sincronizados com sucesso"
        assert data["data"]["steps"] == 10000
        assert data["data"]["hr_avg"] == 72
        assert data["data"]["sleep_hours"] == 7.0
        assert data["data"]["calories"] == 2500
        assert data["metrics_saved"] == 1
        
        # Verify save_metrics was called
        mock_save_metrics.assert_called_once()
        call_args = mock_save_metrics.call_args
        assert call_args[0][0] == "12345678901"  # cpf
        assert len(call_args[0][1]) == 1  # metrics_list
        assert call_args[0][1][0]["date"] == "2026-01-10"
        assert call_args[0][1][0]["steps"] == 10000

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
        ENTÃO faz refresh do token E retenta E salva dados"""
        
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
        
        mock_find_cpf.side_effect = [mock_patient, mock_patient_refreshed, mock_patient_refreshed, mock_patient_refreshed]
        
        # Mock refresh token success
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"access_token": "new_token", "refresh_token": "refresh_token", "expires_in": 3600}
        )
        
        mock_update_tokens.return_value = mock_patient_refreshed
        
        # First call returns 401 (expired), second call succeeds with new token
        mock_get.side_effect = [
            Mock(status_code=401),  # Expired token
            # After refresh - activity
            Mock(status_code=200, json=lambda: {"summary": {"steps": 8000, "caloriesOut": 2000}}),
            # Heartrate
            Mock(status_code=200, json=lambda: {"activities-heart": [{"value": {"restingHeartRate": 70}}]}),
            # Sleep
            Mock(status_code=200, json=lambda: {"summary": {"totalMinutesAsleep": 400}})
        ]
        
        mock_save.return_value = [Mock(spec=PatientMetrics)]
        
        response = client.post("/fitbit/sync")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify refresh was attempted
        mock_post.assert_called_once()
        mock_update_tokens.assert_called_once()

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
        """DADO erro de rede no Fitbit
        QUANDO POST /fitbit/sync
        ENTÃO retorna 500 'Falha ao sincronizar dados'"""
        
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.fitbit_access_token = "valid_token"
        mock_find_cpf.return_value = mock_patient
        
        # Simulate network error
        mock_get.side_effect = Exception("Network timeout")
        
        response = client.post("/fitbit/sync")
        
        assert response.status_code == 500
        assert "Falha ao sincronizar" in response.json()["detail"]
