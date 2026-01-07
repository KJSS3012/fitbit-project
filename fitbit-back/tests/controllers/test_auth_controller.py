import sys
import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.controllers.auth_controller import router
from app.services.auth_service import fake_patients_db

app = FastAPI()
app.include_router(router, prefix="/auth")

@pytest.fixture
def client():
    fake_patients_db.clear()
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
    client.post("/auth/register/patient", json=payload)
    
    response = client.post("/auth/register/patient", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "CPF already registered."

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