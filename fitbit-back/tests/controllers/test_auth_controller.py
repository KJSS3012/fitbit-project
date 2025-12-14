from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_patient_success():
    response = client.post(
        "/auth/register/patient",
        json={
            "cpf": "52998224725",
            "name": "João Cabral",
            "password": "Abcdefjhijk1!"
        }
    )
    assert response.status_code == 201

def test_register_patient_invalid_cpf():
    response = client.post(
        "/auth/register/patient",
        json={
            "cpf": "111",
            "name": "João Cabral",
            "password": "Abcdef1!"
        }
    )
    assert response.status_code == 400


def test_register_doctor_success():
    response = client.post(
        "/auth/register/doctor",
        json={
            "cpf": "52998224725",
            "name": "Dr Cabral",
            "crm": "SP123456",
            "password": "Abcdefjhijk1!"
        }
    )
    assert response.status_code == 201

def test_register_doctor_invalid_crm():
    response = client.post(
        "/auth/register/doctor",
        json={
            "cpf": "52998224725",
            "name": "Dr Cabral",
            "crm": "asd",
            "password": "Abcdef1!"
        }
    )
    assert response.status_code == 400