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


class TestDoctorPatientMetricsPeriodFilters:
    """Tests for PB13 - Doctor period filters (daily, weekly, monthly, custom)"""

    @patch('app.repositories.patient_repository.PatientRepository.get_metrics')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    @patch('app.repositories.authorization_repository.AuthorizationRepository.check_authorization')
    def test_daily_period_filter(self, mock_check_auth, mock_find_patient, mock_get_metrics):
        """
        Scenario 1: Filtro "Dia" retorna dados do dia atual
        """
        mock_check_auth.return_value = True
        
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "52998224725"
        mock_patient.name = "Test Patient"
        mock_find_patient.return_value = mock_patient
        
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
            "/users/patients/52998224725/health-metrics?doctor_crm=12345SP&period=daily"
        )
        
        assert response.status_code == 200
        # Verify metrics were called with today's date
        mock_get_metrics.assert_called_once()
        call_args = mock_get_metrics.call_args[0]
        assert call_args[1] == today  # start_date
        assert call_args[2] == today  # end_date

    @patch('app.repositories.patient_repository.PatientRepository.get_metrics')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    @patch('app.repositories.authorization_repository.AuthorizationRepository.check_authorization')
    def test_weekly_period_filter(self, mock_check_auth, mock_find_patient, mock_get_metrics):
        """
        Scenario 2: Filtro "Semana" retorna dados dos últimos 7 dias
        """
        mock_check_auth.return_value = True
        
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "52998224725"
        mock_patient.name = "Test Patient"
        mock_find_patient.return_value = mock_patient
        
        mock_get_metrics.return_value = []
        
        response = client_doctor.get(
            "/users/patients/52998224725/health-metrics?doctor_crm=12345SP&period=weekly"
        )
        
        assert response.status_code == 200
        # Verify 7 days range
        call_args = mock_get_metrics.call_args[0]
        start = datetime.fromisoformat(call_args[1])
        end = datetime.fromisoformat(call_args[2])
        diff = (end - start).days
        assert diff == 7

    @patch('app.repositories.patient_repository.PatientRepository.get_metrics')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    @patch('app.repositories.authorization_repository.AuthorizationRepository.check_authorization')
    def test_monthly_period_filter(self, mock_check_auth, mock_find_patient, mock_get_metrics):
        """
        Scenario 3: Filtro "Mês" retorna dados dos últimos 30 dias
        """
        mock_check_auth.return_value = True
        
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "52998224725"
        mock_patient.name = "Test Patient"
        mock_find_patient.return_value = mock_patient
        
        mock_get_metrics.return_value = []
        
        response = client_doctor.get(
            "/users/patients/52998224725/health-metrics?doctor_crm=12345SP&period=monthly"
        )
        
        assert response.status_code == 200
        # Verify 30 days range
        call_args = mock_get_metrics.call_args[0]
        start = datetime.fromisoformat(call_args[1])
        end = datetime.fromisoformat(call_args[2])
        diff = (end - start).days
        assert diff == 30

    @patch('app.repositories.patient_repository.PatientRepository.get_metrics')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    @patch('app.repositories.authorization_repository.AuthorizationRepository.check_authorization')
    def test_custom_period_valid_range(self, mock_check_auth, mock_find_patient, mock_get_metrics):
        """
        Scenario 4: Período customizado válido retorna dados do intervalo
        """
        mock_check_auth.return_value = True
        
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "52998224725"
        mock_patient.name = "Test Patient"
        mock_find_patient.return_value = mock_patient
        
        mock_get_metrics.return_value = []
        
        response = client_doctor.get(
            "/users/patients/52998224725/health-metrics"
            "?doctor_crm=12345SP&period=custom&start_date=2026-01-01&end_date=2026-01-10"
        )
        
        assert response.status_code == 200
        mock_get_metrics.assert_called_once_with("52998224725", "2026-01-01", "2026-01-10")

    @patch('app.repositories.authorization_repository.AuthorizationRepository.check_authorization')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_custom_period_invalid_chronology(self, mock_find_patient, mock_check_auth):
        """
        Scenario 5: start_date > end_date retorna erro 400
        """
        mock_check_auth.return_value = True
        
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "52998224725"
        mock_patient.name = "Test Patient"
        mock_find_patient.return_value = mock_patient
        
        response = client_doctor.get(
            "/users/patients/52998224725/health-metrics"
            "?doctor_crm=12345SP&period=custom&start_date=2026-01-10&end_date=2026-01-01"
        )
        
        assert response.status_code == 400
        assert "Período inválido" in response.json()["detail"]

    @patch('app.repositories.authorization_repository.AuthorizationRepository.check_authorization')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_custom_period_missing_dates(self, mock_find_patient, mock_check_auth):
        """
        Scenario 6: Datas faltando retorna erro 400
        """
        mock_check_auth.return_value = True
        
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "52998224725"
        mock_patient.name = "Test Patient"
        mock_find_patient.return_value = mock_patient
        
        response = client_doctor.get(
            "/users/patients/52998224725/health-metrics?doctor_crm=12345SP&period=custom"
        )
        
        assert response.status_code == 400
        assert "Data inicial e final são obrigatórias" in response.json()["detail"]

    @patch('app.repositories.authorization_repository.AuthorizationRepository.check_authorization')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_custom_period_exceeds_limit(self, mock_find_patient, mock_check_auth):
        """
        Validação: Período maior que 365 dias retorna erro 400
        """
        mock_check_auth.return_value = True
        
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "52998224725"
        mock_patient.name = "Test Patient"
        mock_find_patient.return_value = mock_patient
        
        response = client_doctor.get(
            "/users/patients/52998224725/health-metrics"
            "?doctor_crm=12345SP&period=custom&start_date=2024-01-01&end_date=2025-05-01"
        )
        
        assert response.status_code == 400
        assert "não pode exceder 365 dias" in response.json()["detail"]

    @patch('app.repositories.authorization_repository.AuthorizationRepository.check_authorization')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_custom_period_future_date(self, mock_find_patient, mock_check_auth):
        """
        Validação: Data futura retorna erro 400
        """
        mock_check_auth.return_value = True
        
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "52998224725"
        mock_patient.name = "Test Patient"
        mock_find_patient.return_value = mock_patient
        
        future_date = (datetime.now() + timedelta(days=10)).date().isoformat()
        
        response = client_doctor.get(
            f"/users/patients/52998224725/health-metrics"
            f"?doctor_crm=12345SP&period=custom&start_date=2026-01-01&end_date={future_date}"
        )
        
        assert response.status_code == 400
        assert "não pode ser posterior à data de hoje" in response.json()["detail"]
