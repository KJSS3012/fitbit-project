import pytest
import json
from app.services.auth_service import create_patient, create_doctor
from app.schemas.auth_schema import PatientCreate, DoctorCreate
from app.services.auth_service import fake_patients_db, fake_doctors_db

@pytest.fixture(autouse=True)
def clear_fake_db():
    fake_patients_db.clear()
    fake_doctors_db.clear()

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
    
    assert response.status_code == 200 or response.status_code == 201
    assert data["cpf"] == patient.cpf
    assert data["name"] == patient.name

def test_create_patient_invalid_name():
    patient = PatientCreate(
        cpf="52998224725",
        name="João123",
        password="Abcdefjhijk1!"
    )

    response = create_patient(patient)
    assert response.status_code == 400

def test_create_patient_invalid_cpf():
    patient = PatientCreate(
        cpf="11111111111",
        name="João Cabral",
        password="Abcdefjhijk1!"
    )

    response = create_patient(patient)
    assert response.status_code == 400

def test_create_patient_invalid_password():
    patient = PatientCreate(
        cpf="52998224725",
        name="João Cabral",
        password="abc"
    )

    response = create_patient(patient)
    assert response.status_code == 400

def test_create_patient_duplicate_cpf():
    patient = PatientCreate(
        cpf="52998224725",
        name="João Cabral",
        password="Abcdefjhijk1!"
    )

    create_patient(patient)
    response = create_patient(patient)
    assert response.status_code == 409


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

    assert response.status_code == 200 or response.status_code == 201
    assert data["crm"] == doctor.crm
    assert data["name"] == doctor.name

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
    doctor = DoctorCreate(
        cpf="52998224725",
        name="Dr Cabral",
        crm="SP123456",
        password="Abcdefjhijk1!"
    )

    create_doctor(doctor)

    response = create_doctor(doctor)
    assert response.status_code == 409