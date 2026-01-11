import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.controllers.auth_controller import router
from app.database.connection import Base, get_db

app = FastAPI()
app.include_router(router, prefix="/auth")

# Setup in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Create test client with fresh database."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_register_patient_success(client):
    payload = {
        "cpf": "52998224725",
        "name": "João Cabral",
        "password": "Abcdefjhijk1!"
    }

    response = client.post("/auth/register/patient", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["cpf"] == "52998224725"
    assert data["name"] == "JOÃO CABRAL"


def test_register_patient_duplicate_cpf(client):
    payload = {
        "cpf": "52998224725",
        "name": "João Cabral",
        "password": "Abcdefjhijk1!"
    }

    response1 = client.post("/auth/register/patient", json=payload)
    assert response1.status_code == 201

    response2 = client.post("/auth/register/patient", json=payload)
    assert response2.status_code == 409
    assert response2.json()["detail"] == "O CPF já está cadastrado"


def test_register_patient_invalid_cpf_format(client):
    payload = {
        "cpf": "111",
        "name": "João Cabral",
        "password": "Abcdefjhijk1!"
    }

    response = client.post("/auth/register/patient", json=payload)
    assert response.status_code == 400


def test_register_patient_invalid_cpf_checksum(client):
    payload = {
        "cpf": "12345678910",
        "name": "João Cabral",
        "password": "Abcdefjhijk1!"
    }

    response = client.post("/auth/register/patient", json=payload)
    assert response.status_code == 400


def test_register_patient_weak_password_length(client):
    payload = {
        "cpf": "52998224725",
        "name": "João Cabral",
        "password": "123"
    }

    response = client.post("/auth/register/patient", json=payload)
    assert response.status_code == 400


def test_register_patient_weak_password_complexity(client):
    payload = {
        "cpf": "52998224725",
        "name": "João Cabral",
        "password": "apenasletrasminusculas"
    }

    response = client.post("/auth/register/patient", json=payload)
    assert response.status_code == 400


def test_register_patient_invalid_name_spacing(client):
    payload = {
        "cpf": "52998224725",
        "name": "João   Cabral",
        "password": "Abcdefjhijk1!"
    }

    response = client.post("/auth/register/patient", json=payload)
    assert response.status_code == 400


# -------------------
# LOGIN PATIENT
# -------------------

def test_login_patient_success(client):
    """Test successful login with valid CPF and password returns JWT token."""
    # First, register a patient
    register_payload = {
        "cpf": "52998224725",
        "name": "João Cabral",
        "password": "Abcdefjhijk1!"
    }
    client.post("/auth/register/patient", json=register_payload)

    # Now login with the same credentials
    login_payload = {
        "cpf": "52998224725",
        "password": "Abcdefjhijk1!"
    }

    response = client.post("/auth/login/patient", json=login_payload)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_login_patient_cpf_not_found(client):
    """Test login with non-existent CPF returns 401 Credenciais inválidas."""
    login_payload = {
        "cpf": "52998224725",
        "password": "Abcdefjhijk1!"
    }

    response = client.post("/auth/login/patient", json=login_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"


def test_login_patient_wrong_password(client):
    """Test login with correct CPF but wrong password returns 401."""
    # Register patient first
    register_payload = {
        "cpf": "52998224725",
        "name": "João Cabral",
        "password": "Abcdefjhijk1!"
    }
    client.post("/auth/register/patient", json=register_payload)

    # Login with wrong password
    login_payload = {
        "cpf": "52998224725",
        "password": "WrongPassword123!"
    }

    response = client.post("/auth/login/patient", json=login_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"


def test_login_patient_empty_cpf(client):
    """Test login with empty CPF returns 401 (treated as invalid credentials)."""
    login_payload = {
        "cpf": "",
        "password": "Abcdefjhijk1!"
    }

    response = client.post("/auth/login/patient", json=login_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"


def test_login_patient_empty_password(client):
    """Test login with empty password returns 401 (treated as invalid credentials)."""
    login_payload = {
        "cpf": "52998224725",
        "password": ""
    }

    response = client.post("/auth/login/patient", json=login_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"


# -------------------
# LOGIN DOCTOR
# -------------------

def test_login_doctor_success(client):
    """Test successful doctor login with valid CRM and password returns JWT token."""
    # First, register a doctor
    register_payload = {
        "cpf": "52998224725",
        "name": "Dr Cabral",
        "crm": "SP123456",
        "password": "Abcdefjhijk1!"
    }
    client.post("/auth/register/doctor", json=register_payload)

    # Now login with the same credentials
    login_payload = {
        "crm": "SP123456",
        "password": "Abcdefjhijk1!"
    }

    response = client.post("/auth/login/doctor", json=login_payload)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_login_doctor_crm_not_found(client):
    """Test login with non-existent CRM returns 401 Credenciais inválidas."""
    login_payload = {
        "crm": "SP999999",
        "password": "Abcdefjhijk1!"
    }

    response = client.post("/auth/login/doctor", json=login_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"


def test_login_doctor_wrong_password(client):
    """Test login with correct CRM but wrong password returns 401."""
    # Register doctor first
    register_payload = {
        "cpf": "52998224725",
        "name": "Dr Cabral",
        "crm": "SP123456",
        "password": "Abcdefjhijk1!"
    }
    client.post("/auth/register/doctor", json=register_payload)

    # Login with wrong password
    login_payload = {
        "crm": "SP123456",
        "password": "WrongPassword123!"
    }

    response = client.post("/auth/login/doctor", json=login_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"


def test_login_doctor_empty_crm(client):
    """Test login with empty CRM returns 401 (treated as invalid credentials)."""
    login_payload = {
        "crm": "",
        "password": "Abcdefjhijk1!"
    }

    response = client.post("/auth/login/doctor", json=login_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas"
