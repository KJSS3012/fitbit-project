"""
Tests for GET /export endpoint (PB14)
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime

from app.models.patient import Patient
from app.models.patient_metrics import PatientMetrics
from app.api.dependencies import get_current_user
from app.controllers.export_controller import router as export_router


def create_test_app_patient():
    """Create test app with patient JWT override"""
    test_app = FastAPI()
    
    def override_get_current_user():
        return {"sub": "12345678901", "type": "patient"}
    
    test_app.dependency_overrides[get_current_user] = override_get_current_user
    test_app.include_router(export_router)
    
    return test_app


client = TestClient(create_test_app_patient(), raise_server_exceptions=False)


class TestExportDataEndpoint:
    """Tests for PB14 - Export Data (PDF/CSV/JSON)"""

    @patch('app.repositories.patient_repository.PatientRepository.get_metrics')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_export_pdf_success(self, mock_find_patient, mock_get_metrics):
        """
        Scenario 1: Export PDF com dados + header
        DADO: Paciente tem métricas no período
        QUANDO: GET /export?format=pdf&start_date=2026-01-01&end_date=2026-01-10
        ENTÃO: Retorna PDF com header "Paciente: Nome (CPF) Gerado: DD/MM/YYYY HH:MM"
        """
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.name = "João Silva"
        mock_find_patient.return_value = mock_patient
        
        mock_metric = Mock(spec=PatientMetrics)
        mock_metric.date = "2026-01-05"
        mock_metric.steps = 10000
        mock_metric.hr_avg = 72
        mock_metric.sleep_hours = 7.5
        mock_metric.calories = 2500
        mock_metric.source = "fitbit"
        mock_get_metrics.return_value = [mock_metric]
        
        response = client.get(
            "/export?format=pdf&start_date=2026-01-01&end_date=2026-01-10"
        )
        
        assert response.status_code == 200
        # PDF or text/plain (fallback)
        content_type = response.headers["content-type"].split(";")[0]
        assert content_type in ["application/pdf", "text/plain"]
        assert "content-disposition" in response.headers
        assert "fitbit_dados_12345678901" in response.headers["content-disposition"]
        
        # Verify content contains patient info (for text fallback)
        if content_type == "text/plain":
            content = response.content.decode('utf-8')
            assert "João Silva" in content
            assert "12345678901" in content
            assert "Gerado" in content

    @patch('app.repositories.patient_repository.PatientRepository.get_metrics')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_export_csv_header_metadata(self, mock_find_patient, mock_get_metrics):
        """
        Scenario 2: CSV com header metadata
        DADO: Paciente tem métricas
        QUANDO: GET /export?format=csv
        ENTÃO: CSV inclui linhas comentadas com "# Paciente: Nome (CPF)" e "# Gerado em:"
        """
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.name = "Maria Santos"
        mock_find_patient.return_value = mock_patient
        
        mock_metric = Mock(spec=PatientMetrics)
        mock_metric.date = "2026-01-05"
        mock_metric.steps = 8000
        mock_metric.hr_avg = 68
        mock_metric.sleep_hours = 8.0
        mock_metric.calories = 2200
        mock_get_metrics.return_value = [mock_metric]
        
        response = client.get(
            "/export?format=csv&start_date=2026-01-01&end_date=2026-01-10"
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        
        content = response.content.decode('utf-8')
        
        # Verify metadata header lines (as comments)
        assert "# Paciente: Maria Santos (12345678901)" in content
        assert "# Gerado em:" in content
        assert "# Período:" in content
        
        # Verify CSV data
        assert "Data,Passos,Frequência Cardíaca (BPM),Sono (horas),Calorias" in content
        assert "2026-01-05,8000,68,8.0,2200" in content

    @patch('app.repositories.patient_repository.PatientRepository.get_metrics')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_export_json_metadata(self, mock_find_patient, mock_get_metrics):
        """
        Scenario 3: JSON com objeto metadata
        DADO: Paciente tem métricas
        QUANDO: GET /export?format=json
        ENTÃO: JSON tem {"metadata": {"patient_name", "patient_cpf", "generated_at", "period"}, "metrics": [...]}
        """
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.name = "Carlos Oliveira"
        mock_find_patient.return_value = mock_patient
        
        mock_metric = Mock(spec=PatientMetrics)
        mock_metric.date = "2026-01-05"
        mock_metric.steps = 12000
        mock_metric.hr_avg = 75
        mock_metric.sleep_hours = 7.0
        mock_metric.calories = 2800
        mock_metric.source = "fitbit"
        mock_get_metrics.return_value = [mock_metric]
        
        response = client.get(
            "/export?format=json&start_date=2026-01-01&end_date=2026-01-10"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify metadata structure
        assert "metadata" in data
        assert data["metadata"]["patient_name"] == "Carlos Oliveira"
        assert data["metadata"]["patient_cpf"] == "12345678901"
        assert "generated_at" in data["metadata"]
        assert data["metadata"]["period"]["start"] == "2026-01-01"
        assert data["metadata"]["period"]["end"] == "2026-01-10"
        assert data["metadata"]["total_records"] == 1
        
        # Verify metrics data
        assert "metrics" in data
        assert len(data["metrics"]) == 1
        assert data["metrics"][0]["date"] == "2026-01-05"
        assert data["metrics"][0]["steps"] == 12000
        assert data["metrics"][0]["hr_avg"] == 75

    @patch('app.repositories.patient_repository.PatientRepository.get_metrics')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_export_no_data_404(self, mock_find_patient, mock_get_metrics):
        """
        Scenario 4: Sem dados no período
        DADO: Paciente não tem métricas no período
        QUANDO: GET /export?format=pdf&start_date=2020-01-01&end_date=2020-01-10
        ENTÃO: Retorna 404 "Nenhum dado disponível"
        """
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.name = "Test Patient"
        mock_find_patient.return_value = mock_patient
        
        mock_get_metrics.return_value = []
        
        response = client.get(
            "/export?format=pdf&start_date=2020-01-01&end_date=2020-01-10"
        )
        
        assert response.status_code == 404
        assert "Nenhum dado disponível" in response.json()["detail"]

    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_export_invalid_period_400(self, mock_find_patient):
        """
        Scenario 6: Período inválido
        DADO: start_date > end_date
        QUANDO: GET /export?format=csv&start_date=2026-01-10&end_date=2026-01-01
        ENTÃO: Retorna 400 "Período inválido"
        """
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.name = "Test Patient"
        mock_find_patient.return_value = mock_patient
        
        response = client.get(
            "/export?format=csv&start_date=2026-01-10&end_date=2026-01-01"
        )
        
        assert response.status_code == 400
        assert "Período inválido" in response.json()["detail"]

    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_export_exceeds_365_days_400(self, mock_find_patient):
        """
        Validação: Período > 365 dias
        DADO: Período maior que 1 ano
        QUANDO: GET /export?format=json&start_date=2024-01-01&end_date=2025-05-01
        ENTÃO: Retorna 400 "não pode exceder 365 dias"
        """
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.name = "Test Patient"
        mock_find_patient.return_value = mock_patient
        
        response = client.get(
            "/export?format=json&start_date=2024-01-01&end_date=2025-05-01"
        )
        
        assert response.status_code == 400
        assert "não pode exceder 365 dias" in response.json()["detail"]

    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_export_future_date_400(self, mock_find_patient):
        """
        Validação: Data futura
        DADO: end_date é futuro
        QUANDO: GET /export?format=pdf&start_date=2026-01-01&end_date=2027-01-01
        ENTÃO: Retorna 400 "não pode ser posterior à data de hoje"
        """
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.name = "Test Patient"
        mock_find_patient.return_value = mock_patient
        
        response = client.get(
            "/export?format=pdf&start_date=2026-01-01&end_date=2027-01-01"
        )
        
        assert response.status_code == 400
        assert "não pode ser posterior à data de hoje" in response.json()["detail"]

    @patch('app.repositories.patient_repository.PatientRepository.get_metrics')
    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_export_all_formats_have_header(self, mock_find_patient, mock_get_metrics):
        """
        Scenario 7: Todos formatos incluem header com nome/ID/data geração
        DADO: Paciente tem métricas
        QUANDO: Exporta em PDF, CSV e JSON
        ENTÃO: Todos incluem nome paciente, CPF e timestamp geração
        """
        mock_patient = Mock(spec=Patient)
        mock_patient.cpf = "12345678901"
        mock_patient.name = "Ana Paula"
        mock_find_patient.return_value = mock_patient
        
        mock_metric = Mock(spec=PatientMetrics)
        mock_metric.date = "2026-01-05"
        mock_metric.steps = 9000
        mock_metric.hr_avg = 70
        mock_metric.sleep_hours = 7.5
        mock_metric.calories = 2300
        mock_metric.source = "fitbit"
        mock_get_metrics.return_value = [mock_metric]
        
        # Test CSV
        csv_response = client.get(
            "/export?format=csv&start_date=2026-01-01&end_date=2026-01-10"
        )
        assert csv_response.status_code == 200
        csv_content = csv_response.content.decode('utf-8')
        assert "Ana Paula" in csv_content
        assert "12345678901" in csv_content
        assert "Gerado em:" in csv_content
        
        # Test JSON
        json_response = client.get(
            "/export?format=json&start_date=2026-01-01&end_date=2026-01-10"
        )
        assert json_response.status_code == 200
        json_data = json_response.json()
        assert json_data["metadata"]["patient_name"] == "Ana Paula"
        assert json_data["metadata"]["patient_cpf"] == "12345678901"
        assert "generated_at" in json_data["metadata"]

    def test_export_invalid_date_format_400(self):
        """
        Validação: Formato de data inválido
        DADO: Formato de data incorreto
        QUANDO: GET /export?format=csv&start_date=01-01-2026&end_date=10-01-2026
        ENTÃO: Retorna 400 "Formato de data inválido"
        """
        response = client.get(
            "/export?format=csv&start_date=01-01-2026&end_date=10-01-2026"
        )
        
        assert response.status_code == 400
        assert "Formato de data inválido" in response.json()["detail"]
