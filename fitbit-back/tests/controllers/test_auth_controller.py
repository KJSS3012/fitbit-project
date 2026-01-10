import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.controllers.auth_controller import router
from app.database.connection import Base, get_db

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(router, prefix="/auth")

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for the FastAPI app.
    Recreates database schema before each test.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestClient(app)

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
    
    # First submission: Should succeed
    response1 = client.post("/auth/register/patient", json=payload)
    assert response1.status_code == 201
    
    # Second submission: Should fail with 409 Conflict
    response2 = client.post("/auth/register/patient", json=payload)
    assert response2.status_code == 409
    assert response2.json()["detail"] == "CPF already registered."

def test_register_patient_invalid_cpf_format(client):
    payload = {
        "cpf": "111", 
        "name": "João Cabral",
        "password": "Abcdefjhijk1!"
    }
    response = client.post("/auth/register/patient", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "CPF must contain exactly 11 digits."

def test_register_patient_invalid_cpf_checksum(client):
    payload = {
        "cpf": "12345678910", 
        "name": "João Cabral",
        "password": "Abcdefjhijk1!"
    }
    response = client.post("/auth/register/patient", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid CPF."

def test_register_patient_weak_password_length(client):
    payload = {
        "cpf": "52998224725",
        "name": "João Cabral",
        "password": "123"
    }
    response = client.post("/auth/register/patient", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Password must contain at least 12 characters."

def test_register_patient_weak_password_complexity(client):
    payload = {
        "cpf": "52998224725",
        "name": "João Cabral",
        "password": "apenasletrasminusculas"
    }
    response = client.post("/auth/register/patient", json=payload)
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Password must contain" in detail

def test_register_patient_invalid_name_spacing(client):
    payload = {
        "cpf": "52998224725",
        "name": "João   Cabral",
        "password": "Abcdefjhijk1!"
    }
    response = client.post("/auth/register/patient", json=payload)
    assert response.status_code == 400
    assert "Name must contain only letters and single spaces" in response.json()["detail"]