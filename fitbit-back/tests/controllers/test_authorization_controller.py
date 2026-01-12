"""
Tests for Authorization Controller (PB11)
Patient controls which doctors can access their health data.
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime
import json

from app.models.data_authorization import DataAuthorization
from app.models.doctor import Doctor
from app.api.dependencies import get_current_user
from app.controllers.authorization_controller import router as authorization_router


def create_test_app_patient():
    """Create test app with patient JWT override."""
    test_app = FastAPI()
    
    def override_get_current_user_patient():
        return {"sub": "52998224725", "type": "patient"}
    
    test_app.dependency_overrides[get_current_user] = override_get_current_user_patient
    test_app.include_router(authorization_router, prefix="/auth")
    
    return test_app


def create_test_app_doctor():
    """Create test app with doctor JWT override."""
    test_app = FastAPI()
    
    def override_get_current_user_doctor():
        return {"sub": "12345SP", "type": "doctor"}
    
    test_app.dependency_overrides[get_current_user] = override_get_current_user_doctor
    test_app.include_router(authorization_router, prefix="/auth")
    
    return test_app


client_patient = TestClient(create_test_app_patient(), raise_server_exceptions=False)
client_doctor = TestClient(create_test_app_doctor(), raise_server_exceptions=False)


class TestPatientAuthorizationControl:
    """Tests for PB11 - Patient controls doctor authorizations."""

    @patch('app.repositories.authorization_repository.AuthorizationRepository.get_patient_authorized_doctors')
    def test_list_authorized_doctors_success(self, mock_get_doctors):
        """
        DADO: Paciente autenticado com médicos vinculados
        QUANDO: GET /auth/doctors
        ENTÃO: Retorna lista [{crm, doctor_name, authorized}]
        """
        mock_get_doctors.return_value = [
            {"crm": "12345SP", "doctor_name": "Dr. João Silva", "authorized": True},
            {"crm": "67890RJ", "doctor_name": "Dra. Maria Santos", "authorized": False}
        ]
        
        response = client_patient.get("/auth/doctors")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["crm"] == "12345SP"
        assert data[0]["doctor_name"] == "Dr. João Silva"
        assert data[0]["authorized"] is True
        assert data[1]["authorized"] is False
        
        mock_get_doctors.assert_called_once_with("52998224725")

    @patch('app.repositories.authorization_repository.AuthorizationRepository.get_patient_authorized_doctors')
    def test_list_authorized_doctors_empty(self, mock_get_doctors):
        """
        PB11 Scenario 4: Nenhum médico vinculado
        DADO: Paciente sem médicos autorizados
        QUANDO: GET /auth/doctors
        ENTÃO: Retorna lista vazia []
        """
        mock_get_doctors.return_value = []
        
        response = client_patient.get("/auth/doctors")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []

    @patch('app.repositories.authorization_repository.AuthorizationRepository.toggle_authorization_with_audit')
    def test_toggle_authorization_grant(self, mock_toggle):
        """
        PB11 Scenario 1: Ativa médico
        DADO: Médico com authorized=False
        QUANDO: PATCH /auth/doctors/{crm}
        ENTÃO: Toggle para True + mensagem "Compartilhamento ativado"
        """
        mock_toggle.return_value = {"authorized": True, "action": "grant"}
        
        response = client_patient.patch("/auth/doctors/12345SP")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["authorized"] is True
        assert "ativado" in data["message"].lower()
        
        mock_toggle.assert_called_once_with("12345SP", "52998224725")

    @patch('app.repositories.authorization_repository.AuthorizationRepository.toggle_authorization_with_audit')
    def test_toggle_authorization_revoke(self, mock_toggle):
        """
        PB11 Scenario 2: Revoga médico
        DADO: Médico com authorized=True
        QUANDO: PATCH /auth/doctors/{crm}
        ENTÃO: Toggle para False + mensagem "Revogado"
        """
        mock_toggle.return_value = {"authorized": False, "action": "revoke"}
        
        response = client_patient.patch("/auth/doctors/12345SP")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["authorized"] is False
        assert "revogado" in data["message"].lower()

    @patch('app.repositories.authorization_repository.AuthorizationRepository.toggle_authorization_with_audit')
    def test_toggle_authorization_audit_error(self, mock_toggle):
        """
        PB11 Scenario 3: Erro auditoria
        DADO: Falha ao registrar auditoria
        QUANDO: PATCH /auth/doctors/{crm}
        ENTÃO: Retorna 500 "Erro ao registrar auditoria. Operação não concluída"
        """
        mock_toggle.side_effect = RuntimeError("Database commit failed")
        
        response = client_patient.patch("/auth/doctors/12345SP")
        
        assert response.status_code == 500
        assert "auditoria" in response.json()["detail"].lower()
        assert "não concluída" in response.json()["detail"].lower()

    @patch('app.repositories.authorization_repository.AuthorizationRepository.toggle_authorization_with_audit')
    def test_toggle_authorization_not_found(self, mock_toggle):
        """
        DADO: CRM não vinculado ao paciente
        QUANDO: PATCH /auth/doctors/{crm}
        ENTÃO: Retorna 404 "Autorização não encontrada"
        """
        mock_toggle.side_effect = ValueError("Autorização não encontrada para CRM 99999XX")
        
        response = client_patient.patch("/auth/doctors/99999XX")
        
        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"].lower()

    def test_doctor_cannot_manage_authorizations(self):
        """
        DADO: Usuário autenticado como médico
        QUANDO: GET /auth/doctors
        ENTÃO: Retorna 403 "Apenas pacientes podem gerenciar autorizações"
        """
        response = client_doctor.get("/auth/doctors")
        
        assert response.status_code == 403
        assert "apenas pacientes" in response.json()["detail"].lower()

    @patch('app.repositories.doctor_repository.DoctorRepository.find_by_crm')
    @patch('app.repositories.authorization_repository.AuthorizationRepository.grant_new_authorization')
    def test_add_doctor_authorization_success(self, mock_grant, mock_find_doctor):
        """
        DADO: CRM válido de médico cadastrado
        QUANDO: POST /auth/doctors {"doctor_crm": "12345SP"}
        ENTÃO: Cria autorização + retorna "Dr. XXX adicionado"
        """
        mock_doctor = Mock(spec=Doctor)
        mock_doctor.crm = "12345SP"
        mock_doctor.name = "Dr. João Silva"
        mock_find_doctor.return_value = mock_doctor
        
        mock_auth = Mock(spec=DataAuthorization)
        mock_auth.doctor_crm = "12345SP"
        mock_auth.patient_cpf = "52998224725"
        mock_auth.authorized = True
        mock_grant.return_value = mock_auth
        
        response = client_patient.post(
            "/auth/doctors",
            json={"doctor_crm": "12345SP"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["authorized"] is True
        assert "João Silva" in data["message"]
        
        mock_find_doctor.assert_called_once_with("12345SP")
        mock_grant.assert_called_once_with("12345SP", "52998224725")

    @patch('app.repositories.doctor_repository.DoctorRepository.find_by_crm')
    def test_add_doctor_authorization_not_found(self, mock_find_doctor):
        """
        DADO: CRM não cadastrado no sistema
        QUANDO: POST /auth/doctors {"doctor_crm": "99999XX"}
        ENTÃO: Retorna 404 "Médico com CRM 99999XX não encontrado"
        """
        mock_find_doctor.return_value = None
        
        response = client_patient.post(
            "/auth/doctors",
            json={"doctor_crm": "99999XX"}
        )
        
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"].lower()

    @patch('app.repositories.doctor_repository.DoctorRepository.find_by_crm')
    @patch('app.repositories.authorization_repository.AuthorizationRepository.grant_new_authorization')
    def test_add_doctor_authorization_already_exists(self, mock_grant, mock_find_doctor):
        """
        DADO: Médico já vinculado ao paciente
        QUANDO: POST /auth/doctors {"doctor_crm": "12345SP"}
        ENTÃO: Retorna 400 "Médico já está vinculado"
        """
        mock_doctor = Mock(spec=Doctor)
        mock_doctor.crm = "12345SP"
        mock_doctor.name = "Dr. João Silva"
        mock_find_doctor.return_value = mock_doctor
        
        mock_grant.side_effect = ValueError("Médico 12345SP já está vinculado")
        
        response = client_patient.post(
            "/auth/doctors",
            json={"doctor_crm": "12345SP"}
        )
        
        assert response.status_code == 400
        assert "vinculado" in response.json()["detail"].lower()

    @patch('app.repositories.authorization_repository.AuthorizationRepository.revoke_all_authorizations')
    def test_revoke_all_authorizations_success(self, mock_revoke_all):
        """
        DADO: Paciente com autorizações ativas
        QUANDO: DELETE /auth/doctors/all
        ENTÃO: Retorna 200 com mensagem de sucesso e count
        """
        mock_revoke_all.return_value = 3
        
        response = client_patient.delete("/auth/doctors/all")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "3 autorizações revogadas" in data["message"]
        assert data["revoked_count"] == 3
        mock_revoke_all.assert_called_once()

    @patch('app.repositories.authorization_repository.AuthorizationRepository.revoke_all_authorizations')
    def test_revoke_all_authorizations_none(self, mock_revoke_all):
        """
        DADO: Paciente sem autorizações ativas
        QUANDO: DELETE /auth/doctors/all
        ENTÃO: Retorna 200 com mensagem apropriada
        """
        mock_revoke_all.return_value = 0
        
        response = client_patient.delete("/auth/doctors/all")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "nenhuma autorização" in data["message"].lower()
        assert data["revoked_count"] == 0

    @patch('app.repositories.authorization_repository.AuthorizationRepository.revoke_all_authorizations')
    def test_revoke_all_authorizations_audit_error(self, mock_revoke_all):
        """
        DADO: Erro ao registrar auditoria durante revoke all
        QUANDO: DELETE /auth/doctors/all
        ENTÃO: Retorna 500 com mensagem de erro
        """
        mock_revoke_all.side_effect = RuntimeError("Erro ao registrar auditoria")
        
        response = client_patient.delete("/auth/doctors/all")
        
        assert response.status_code == 500
        assert "auditoria" in response.json()["detail"].lower()

    def test_revoke_all_authorizations_doctor_forbidden(self):
        """
        DADO: Usuário é médico
        QUANDO: DELETE /auth/doctors/all
        ENTÃO: Retorna 403 "Apenas pacientes podem revogar autorizações"
        """
        response = client_doctor.delete("/auth/doctors/all")
        
        assert response.status_code == 403
        assert "apenas pacientes" in response.json()["detail"].lower()
