"""
Testes para user_controller.py - GET /user/me e PATCH /user/me
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.database.connection import Base, get_db
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.core.security import get_password_hash
from app.core.security import create_access_token


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_patient(db):
    """Create test patient"""
    patient = Patient(
        cpf="12345678901",
        name="João Silva",
        password=get_password_hash("senha123456789")
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@pytest.fixture
def test_doctor(db):
    """Create test doctor"""
    doctor = Doctor(
        cpf="98765432100",
        crm="CRM12345",
        name="Dr. Maria Santos",
        password=get_password_hash("senha123456789")
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@pytest.fixture
def patient_token(test_patient):
    """Generate JWT token for test patient"""
    return create_access_token(
        subject=test_patient.cpf,
        user_type="patient"
    )


@pytest.fixture
def doctor_token(test_doctor):
    """Generate JWT token for test doctor"""
    return create_access_token(
        subject=test_doctor.crm,
        user_type="doctor"
    )


def test_get_current_user_patient(patient_token):
    """Test GET /user/me for patient"""
    response = client.get(
        "/user/me",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "12345678901"
    assert data["name"] == "João Silva"
    assert data["type"] == "patient"


def test_get_current_user_doctor(doctor_token):
    """Test GET /user/me for doctor"""
    response = client.get(
        "/user/me",
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "CRM12345"
    assert data["name"] == "Dr. Maria Santos"
    assert data["type"] == "doctor"


def test_get_current_user_no_token():
    """Test GET /user/me without authentication"""
    response = client.get("/user/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token():
    """Test GET /user/me with invalid token"""
    response = client.get(
        "/user/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_update_user_name_patient(patient_token):
    """Test PATCH /user/me - update name"""
    response = client.patch(
        "/user/me",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={"name": "João Silva Atualizado"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "atualizado" in data["message"].lower()
    
    # Verify change
    get_response = client.get(
        "/user/me",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert get_response.json()["name"] == "João Silva Atualizado"


def test_update_user_password_patient(patient_token):
    """Test PATCH /user/me - update password"""
    new_password = "novasenha12345678"  # 17 caracteres
    
    response = client.patch(
        "/user/me",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={"password": new_password}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "atualizado" in data["message"].lower()


def test_update_user_password_too_short(patient_token):
    """Test PATCH /user/me - password too short"""
    response = client.patch(
        "/user/me",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={"password": "short"}
    )
    
    assert response.status_code == 400
    assert "12 caracteres" in response.json()["detail"]


def test_update_user_both_fields(patient_token):
    """Test PATCH /user/me - update both name and password"""
    response = client.patch(
        "/user/me",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={
            "name": "Novo Nome",
            "password": "novasenha123456"
        }
    )
    
    assert response.status_code == 200
    
    # Verify name change
    get_response = client.get(
        "/user/me",
        headers={"Authorization": f"Bearer {patient_token}"}
    )
    assert get_response.json()["name"] == "Novo Nome"


def test_update_user_no_changes(patient_token):
    """Test PATCH /user/me - empty update"""
    response = client.patch(
        "/user/me",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={}
    )
    
    assert response.status_code == 200


def test_update_user_doctor(doctor_token):
    """Test PATCH /user/me for doctor"""
    response = client.patch(
        "/user/me",
        headers={"Authorization": f"Bearer {doctor_token}"},
        json={"name": "Dra. Maria Santos"}
    )
    
    assert response.status_code == 200
    
    get_response = client.get(
        "/user/me",
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    assert get_response.json()["name"] == "Dra. Maria Santos"


def test_update_user_no_auth():
    """Test PATCH /user/me without authentication"""
    response = client.patch(
        "/user/me",
        json={"name": "Tentativa sem autenticação"}
    )
    assert response.status_code == 401
