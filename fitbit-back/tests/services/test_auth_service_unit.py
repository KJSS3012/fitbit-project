"""
Testes UNITÁRIOS para auth_service - usando MOCKS
Estes testes são independentes de banco de dados e sempre funcionam.
"""
import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException

from app.services.auth_service import create_patient, login_patient
from app.schemas.auth_schema import PatientCreate, PatientLogin
from app.models.patient import Patient


class TestCreatePatient:
    """Testes unitários para create_patient"""
    
    def test_create_patient_success(self):
        """Deve criar paciente com dados válidos"""
        # Arrange
        patient_data = PatientCreate(
            cpf="52998224725",  # Valid CPF
            name="João Silva",
            password="Senha@123456"  # Valid password
        )
        
        # Mock do repository
        mock_db = Mock()
        mock_repo = Mock()
        mock_repo.find_by_cpf.return_value = None  # CPF não existe
        mock_repo.create.return_value = Patient(
            cpf="52998224725",
            name="JOÃO SILVA",
            password="hashed_password"
        )
        
        # Act
        with pytest.MonkeyPatch.context() as m:
            m.setattr("app.services.auth_service.PatientRepository", lambda db: mock_repo)
            response = create_patient(patient_data, mock_db)
        
        # Assert
        assert response.status_code == 201
        import json
        data = json.loads(response.body)
        assert data["cpf"] == "52998224725"
        assert data["name"] == "JOÃO SILVA"
        
        # Verificar que métodos foram chamados
        mock_repo.find_by_cpf.assert_called_once_with("52998224725")
        mock_repo.create.assert_called_once()
    
    def test_create_patient_duplicate_cpf(self):
        """Deve retornar 409 se CPF já existe"""
        # Arrange
        patient_data = PatientCreate(
            cpf="52998224725",  # Valid CPF
            name="João Silva",
            password="Senha@123456"  # Valid password
        )
        
        # Mock retorna paciente existente
        mock_db = Mock()
        mock_repo = Mock()
        mock_repo.find_by_cpf.return_value = Patient(cpf="52998224725", name="Existente", password="hash")
        
        # Act & Assert
        with pytest.MonkeyPatch.context() as m:
            m.setattr("app.services.auth_service.PatientRepository", lambda db: mock_repo)
            response = create_patient(patient_data, mock_db)
            
            assert response.status_code == 409
            import json
            data = json.loads(response.body)
            assert "cpf já está cadastrado" in data["detail"].lower()


class TestLoginPatient:
    """Testes unitários para login_patient"""
    
    def test_login_success(self):
        """Deve retornar token JWT com credenciais válidas"""
        # Arrange
        credentials = PatientLogin(
            cpf="52998224725",  # Valid CPF
            password="Senha@123456"
        )
        
        mock_db = Mock()
        mock_repo = Mock()
        mock_patient = Patient(
            cpf="52998224725",
            name="João Silva",
            password="$2b$12$hashedpassword"  # Hash bcrypt mockado
        )
        mock_repo.find_by_cpf.return_value = mock_patient
        
        # Mock verify_password
        with pytest.MonkeyPatch.context() as m:
            m.setattr("app.services.auth_service.verify_password", lambda plain, hashed: True)
            m.setattr("app.services.auth_service.PatientRepository", lambda db: mock_repo)
            
            # Act
            response = login_patient(credentials, mock_db)
        
        # Assert
        assert response.status_code == 200
        import json
        data = json.loads(response.body)
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Deve retornar 401 com senha incorreta"""
        credentials = PatientLogin(
            cpf="52998224725",  # Valid CPF
            password="Senha@Errada1"
        )
        
        mock_db = Mock()
        mock_repo = Mock()
        mock_patient = Patient(cpf="52998224725", name="João", password="hash")
        mock_repo.find_by_cpf.return_value = mock_patient
        
        # Mock verify_password retorna False
        with pytest.MonkeyPatch.context() as m:
            m.setattr("app.services.auth_service.verify_password", lambda plain, hashed: False)
            m.setattr("app.services.auth_service.PatientRepository", lambda db: mock_repo)
            
            response = login_patient(credentials, mock_db)
            
            assert response.status_code == 401
            import json
            data = json.loads(response.body)
            assert "credenciais inválidas" in data["detail"].lower()
