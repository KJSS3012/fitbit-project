"""
Testes para fitbit_controller.py - OAuth e endpoints Fitbit
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.models.patient import Patient
from app.core.security import get_current_user_cpf
from app.controllers.fitbit_controller import router as fitbit_router


# Cria um app isolado apenas para testes do Fitbit
def create_test_app():
    """Cria uma instância isolada do app para testes"""
    test_app = FastAPI()
    
    # Mock JWT para retornar CPF fixo
    def override_get_current_user_cpf():
        return "12345678901"
    
    test_app.dependency_overrides[get_current_user_cpf] = override_get_current_user_cpf
    test_app.include_router(fitbit_router, prefix="/fitbit")
    
    return test_app


client = TestClient(create_test_app(), raise_server_exceptions=False)


class TestFitbitOAuthFlow:
    """Testes do fluxo OAuth completo"""

    @patch('app.controllers.fitbit_controller.requests.post')
    @patch('app.repositories.patient_repository.PatientRepository.update_fitbit_tokens')
    def test_callback_success(self, mock_update_tokens, mock_post):
        """Dado que o usuário autorizou o acesso
        Quando recebo o callback com código válido
        Então armazeno tokens e redireciono com sucesso"""
        # Mock da resposta do Fitbit
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response
        
        # Mock do repositório
        mock_patient = Patient(cpf="12345678901", name="Teste", password="hash")
        mock_update_tokens.return_value = mock_patient
        
        response = client.get("/fitbit/callback?code=mock_auth_code&state=12345678901", follow_redirects=False)
        
        assert response.status_code == 307
        assert "fitbit=connected" in response.headers["location"]
        mock_update_tokens.assert_called_once()

    def test_callback_user_denied(self):
        """Dado que o usuário negou o acesso no Fitbit
        Quando recebo callback com error=access_denied
        Então redireciono com fitbit=denied"""
        response = client.get("/fitbit/callback?error=access_denied&state=12345678901", follow_redirects=False)
        
        assert response.status_code == 307
        assert "fitbit=denied" in response.headers["location"]

    def test_callback_server_error(self):
        """Dado que ocorreu erro no servidor Fitbit
        Quando recebo callback com error genérico
        Então redireciono com fitbit=error"""
        response = client.get("/fitbit/callback?error=server_error&state=12345678901", follow_redirects=False)
        
        assert response.status_code == 307
        assert "fitbit=error" in response.headers["location"]

    @patch('app.controllers.fitbit_controller.requests.post')
    def test_callback_exchange_token_fails(self, mock_post):
        """Dado que a troca de código falha
        Quando o Fitbit rejeita o código
        Então redireciono com fitbit=error"""
        mock_post.side_effect = Exception("Invalid code")
        
        response = client.get("/fitbit/callback?code=invalid_code&state=12345678901", follow_redirects=False)
        
        assert response.status_code == 307
        assert "fitbit=error" in response.headers["location"]

    def test_callback_missing_code_and_error(self):
        """Dado que não há code nem error no callback
        Quando recebo callback vazio
        Então redireciono com fitbit=error"""
        response = client.get("/fitbit/callback?state=12345678901", follow_redirects=False)
        
        assert response.status_code == 307
        assert "fitbit=error" in response.headers["location"]


class TestFitbitStatusEndpoint:
    """Testes do endpoint GET /fitbit/status"""

    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_status_connected(self, mock_find_by_cpf):
        """Dado que o paciente tem tokens Fitbit válidos
        Quando verifico o status
        Então retorna connected=true"""
        mock_patient = Patient(
            cpf="12345678901",
            name="Teste",
            password="hash",
            fitbit_access_token="valid_token"
        )
        mock_find_by_cpf.return_value = mock_patient
        
        response = client.get("/fitbit/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is True
        assert "scopes" in data

    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_status_not_connected(self, mock_find_by_cpf):
        """Dado que o paciente não tem tokens Fitbit
        Quando verifico o status
        Então retorna connected=false"""
        mock_patient = Patient(
            cpf="12345678901",
            name="Teste",
            password="hash",
            fitbit_access_token=None
        )
        mock_find_by_cpf.return_value = mock_patient
        
        response = client.get("/fitbit/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is False

    @patch('app.repositories.patient_repository.PatientRepository.find_by_cpf')
    def test_status_patient_not_found(self, mock_find_by_cpf):
        """Dado que o paciente não existe no banco
        Quando verifico o status
        Então retorna connected=false"""
        mock_find_by_cpf.return_value = None
        
        response = client.get("/fitbit/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is False


class TestFitbitDisconnectEndpoint:
    """Testes do endpoint POST /fitbit/disconnect"""

    @patch('app.repositories.patient_repository.PatientRepository.remove_fitbit_tokens')
    def test_disconnect_success(self, mock_remove_tokens):
        """Dado que o paciente está conectado ao Fitbit
        Quando solicita desconexão
        Então remove os tokens com sucesso"""
        mock_patient = Patient(
            cpf="12345678901",
            name="Teste",
            password="hash",
            fitbit_access_token="token"
        )
        mock_remove_tokens.return_value = mock_patient
        
        response = client.post("/fitbit/disconnect")
        
        assert response.status_code == 200
        data = response.json()
        assert "Fitbit desconectado" in data["message"]

    @patch('app.repositories.patient_repository.PatientRepository.remove_fitbit_tokens')
    def test_disconnect_patient_not_found(self, mock_remove_tokens):
        """Dado que o paciente não existe
        Quando solicita desconexão
        Então lança HTTPException 404"""
        mock_remove_tokens.return_value = None
        
        response = client.post("/fitbit/disconnect")
        
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]
