"""
Tests for GET /patients/{cpf}/health-metrics endpoint (PB07)
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime, timedelta

from app.models.patient import Patient
from app.models.patient_metrics import PatientMetrics
from app.models.data_authorization import DataAuthorization
from app.api.dependencies import get_current_user
from app.controllers.user_controller import router as user_router


def create_test_app_doctor():
    """Create test app with doctor JWT override"""
    test_app = FastAPI()
    
    def override_get_current_user_doctor():
        return {"sub": "12345SP", "type": "doctor"}
    
    test_app.dependency_overrides[get_current_user] = override_get_current_user_doctor
    test_app.include_router(user_router, prefix="/users")
    
    return test_app


def create_test_app_patient():
    """Create test app with patient JWT override"""
    test_app = FastAPI()
    
    def override_get_current_user_patient():
        return {"sub": "12345678901", "type": "patient"}
    
    test_app.dependency_overrides[get_current_user] = override_get_current_user_patient
    test_app.include_router(user_router, prefix="/users")
    
    return test_app


client_doctor = TestClient(create_test_app_doctor(), raise_server_exceptions=False)
client_patient = TestClient(create_test_app_patient(), raise_server_exceptions=False)


class TestDoctorViewPatientMetrics:
    """Tests for PB07 - Doctor viewing patient metrics"""

    @patch('app.repositories.patient_repository.PatientRepository.get_metrics')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    @patch('app.repositories.authorization_repository.AuthorizationRepository.check_authorization')
    def test_authorized_doctor_gets_patient_metrics_200(
        self, 
        mock_check_auth, 
        mock_find_patient, 
        mock_get_metrics
    ):
        """
        DADO: Médico autorizado (data_authorization.authorized=true)
        QUANDO: GET /patients/{cpf}/health-metrics?doctor_crm=12345SP
        ENTÃO: Retorna 200 com métricas do paciente
        """
        # Mock authorization = True
        mock_check_auth.return_value = True
        
        # Mock patient
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "52998224725"
        mock_patient.name = "João da Silva"
        mock_find_patient.return_value = mock_patient
        
        # Mock metrics (recent data - not outdated)
        today = datetime.now().date().isoformat()
        mock_metric = Mock(spec=PatientMetrics)
        mock_metric.date = today
        mock_metric.steps = 10000
        mock_metric.hr_avg = 72
        mock_metric.sleep_hours = 7.5
        mock_metric.calories = 2500
        mock_metric.source = "fitbit"
        mock_get_metrics.return_value = [mock_metric]
        
        response = client_doctor.get(
            "/users/patients/52998224725/health-metrics?doctor_crm=12345SP"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["patient_cpf"] == "52998224725"
        assert data["patient_name"] == "João da Silva"
        assert data["total_records"] == 1
        assert data["is_data_outdated"] is False
        assert len(data["metrics"]) == 1
        assert data["metrics"][0]["steps"] == 10000
        
        # Verify authorization was checked
        mock_check_auth.assert_called_once_with("12345SP", "52998224725")

    @patch('app.repositories.authorization_repository.AuthorizationRepository.check_authorization')
    def test_unauthorized_doctor_gets_403(self, mock_check_auth):
        """
        DADO: Paciente NÃO autorizou médico (data_authorization.authorized=false)
        QUANDO: GET /patients/{cpf}/health-metrics
        ENTÃO: Retorna 403 "Paciente não autorizou compartilhamento"
        """
        # Mock authorization = False
        mock_check_auth.return_value = False
        
        response = client_doctor.get(
            "/users/patients/12345678901/health-metrics?doctor_crm=12345SP"
        )
        
        assert response.status_code == 403
        assert "não autorizou" in response.json()["detail"].lower()

    @patch('app.repositories.patient_repository.PatientRepository.get_metrics')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    @patch('app.repositories.authorization_repository.AuthorizationRepository.check_authorization')
    def test_outdated_data_flag_when_older_than_24h(
        self, 
        mock_check_auth, 
        mock_find_patient, 
        mock_get_metrics
    ):
        """
        DADO: Última métrica >24h atrás
        QUANDO: GET /patients/{cpf}/health-metrics
        ENTÃO: Retorna is_data_outdated=true
        """
        mock_check_auth.return_value = True
        
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "52998224725"
        mock_patient.name = "Maria Santos"
        mock_find_patient.return_value = mock_patient
        
        # Mock metrics with old data (3 days ago)
        old_date = (datetime.now() - timedelta(days=3)).date().isoformat()
        mock_metric = Mock(spec=PatientMetrics)
        mock_metric.date = old_date
        mock_metric.steps = 5000
        mock_metric.hr_avg = 68
        mock_metric.sleep_hours = 6.0
        mock_metric.calories = 1800
        mock_metric.source = "fitbit"
        mock_get_metrics.return_value = [mock_metric]
        
        response = client_doctor.get(
            "/users/patients/52998224725/health-metrics?doctor_crm=12345SP"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_data_outdated"] is True
        assert data["last_sync"] == old_date

    def test_patient_cannot_access_endpoint_403(self):
        """
        DADO: Usuário é paciente (não médico)
        QUANDO: GET /patients/{cpf}/health-metrics
        ENTÃO: Retorna 403 "Apenas médicos podem acessar"
        """
        response = client_patient.get(
            "/users/patients/52998224725/health-metrics?doctor_crm=12345SP"
        )
        
        assert response.status_code == 403
        assert "apenas médicos" in response.json()["detail"].lower()

    def test_crm_mismatch_jwt_gets_403(self):
        """
        DADO: doctor_crm no query param diferente do JWT
        QUANDO: GET /patients/{cpf}/health-metrics?doctor_crm=99999XX
        ENTÃO: Retorna 403 "CRM não corresponde"
        """
        response = client_doctor.get(
            "/users/patients/52998224725/health-metrics?doctor_crm=99999XX"
        )
        
        assert response.status_code == 403
        assert "não corresponde" in response.json()["detail"].lower()

    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    @patch('app.repositories.authorization_repository.AuthorizationRepository.check_authorization')
    def test_patient_not_found_404(self, mock_check_auth, mock_find_patient):
        """
        DADO: CPF não existe no banco
        QUANDO: GET /patients/{cpf}/health-metrics
        ENTÃO: Retorna 404 "Paciente não encontrado"
        """
        mock_check_auth.return_value = True
        mock_find_patient.return_value = None
        
        response = client_doctor.get(
            "/users/patients/99999999999/health-metrics?doctor_crm=12345SP"
        )
        
        assert response.status_code == 404
        assert "paciente não encontrado" in response.json()["detail"].lower()
