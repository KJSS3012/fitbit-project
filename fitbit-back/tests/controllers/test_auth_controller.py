import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.controllers.auth_controller import router
from app.models.mock import FAKE_PATIENTS_DB

app = FastAPI()
app.include_router(router, prefix="/auth")


@pytest.fixture
def client():
    """
    Clear mock DB and patch persistence functions
    so tests do not read/write the real JSON file.
    """
    FAKE_PATIENTS_DB.clear()

    with patch("app.services.auth_service.load_persistence"), \
         patch("app.services.auth_service.save_persistence"):
        yield TestClient(app)


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
    assert response2.json()["detail"] == "CPF already registered."


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
