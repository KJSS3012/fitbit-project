import pytest
import json
from unittest.mock import patch
from app.services.auth_service import create_patient, create_doctor
from app.schemas.auth_schema import PatientCreate, DoctorCreate
from app.models.mock import FAKE_PATIENTS_DB as fake_patients_db, FAKE_DOCTORS_DB as fake_doctors_db
from app.core.security import verify_password

@pytest.fixture(autouse=True)
def clear_fake_db_and_mock_disk():
    """Clear memory DB and mock disk persistence before each test."""
    fake_patients_db.clear()
    fake_doctors_db.clear()
    with patch("app.services.auth_service.load_persistence"), \
         patch("app.services.auth_service.save_persistence"):
        yield

# -------------------
# PATIENT
# -------------------

def test_create_patient_success():
    patient = PatientCreate(
        cpf="52998224725",
        name="João Cabral",
        password="Abcdefjhijk1!"
    )

    response = create_patient(patient)
    data = json.loads(response.body)
    
    assert response.status_code in [200, 201]
    assert data["cpf"] == patient.cpf
    assert data["name"] == patient.name.upper()

def test_create_patient_invalid_name():
    patient = PatientCreate(cpf="52998224725", name="João123", password="Abcdefjhijk1!")
    response = create_patient(patient)
    assert response.status_code == 400

def test_create_patient_invalid_cpf():
    patient = PatientCreate(cpf="11111111111", name="João Cabral", password="Abcdefjhijk1!")
    response = create_patient(patient)
    assert response.status_code == 400

def test_create_patient_invalid_password():
    patient = PatientCreate(cpf="52998224725", name="João Cabral", password="abc")
    response = create_patient(patient)
    assert response.status_code == 400

def test_create_patient_duplicate_cpf():
    patient = PatientCreate(cpf="52998224725", name="João Cabral", password="Abcdefjhijk1!")
    create_patient(patient)
    response = create_patient(patient)
    assert response.status_code == 409

def test_patient_password_hashing():
    raw_password = "PatientPassword123!"
    patient = PatientCreate(cpf="52998224725", name="John Doe", password=raw_password)
    response = create_patient(patient)
    assert response.status_code == 201

    saved_patient = fake_patients_db[0]
    saved_password = saved_patient["password"]

    assert saved_password != raw_password
    assert verify_password(raw_password, saved_password) is True


# -------------------
# DOCTOR
# -------------------

def test_create_doctor_success():
    doctor = DoctorCreate(
        cpf="52998224725",
        name="Dr Cabral",
        crm="SP123456",
        password="Abcdefjhijk1!"
    )

    response = create_doctor(doctor)
    data = json.loads(response.body)

    assert response.status_code in [200, 201]
    assert data["message"] == "Doctor created"
    assert fake_doctors_db[0]["crm"] == doctor.crm

def test_create_doctor_invalid_crm():
    doctor = DoctorCreate(
        cpf="52998224725", 
        name="Dr Cabral", 
        crm="123", 
        password="Abcdefjhijk1!"
    )
    response = create_doctor(doctor)
    assert response.status_code == 400

def test_create_doctor_duplicate_crm():
    doctor = DoctorCreate(cpf="52998224725", name="Dr Cabral", crm="SP123456", password="Abcdefjhijk1!")
    create_doctor(doctor)
    response = create_doctor(doctor)
    assert response.status_code == 409

def test_doctor_password_hashing():
    raw_password = "DoctorPassword123!"
    doctor = DoctorCreate(cpf="52998224725", name="Dr House", crm="SP123456", password=raw_password)
    response = create_doctor(doctor)
    assert response.status_code == 201

    saved_doctor = fake_doctors_db[0]
    saved_password = saved_doctor["password"]

    assert saved_password != raw_password
    assert verify_password(raw_password, saved_password) is True