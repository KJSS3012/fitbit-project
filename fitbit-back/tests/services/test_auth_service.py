import pytest
from fastapi import HTTPException
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
    assert response.cpf == patient.cpf
    assert response.name == patient.name

def test_create_patient_invalid_name():
    patient = PatientCreate(
        cpf="52998224725",
        name="João123",
        password="Abcdefjhijk1!"
    )

    with pytest.raises(HTTPException) as exc:
        create_patient(patient)

    assert exc.value.status_code == 400

def test_create_patient_invalid_cpf():
    patient = PatientCreate(
        cpf="11111111111",
        name="João Cabral",
        password="Abcdefjhijk1!"
    )

    with pytest.raises(HTTPException) as exc:
        create_patient(patient)

    assert exc.value.status_code == 400

def test_create_patient_invalid_password():
    patient = PatientCreate(
        cpf="52998224725",
        name="João Cabral",
        password="abc"
    )

    with pytest.raises(HTTPException) as exc:
        create_patient(patient)

    assert exc.value.status_code == 400

def test_create_patient_duplicate_cpf():
    patient = PatientCreate(
        cpf="52998224725",
        name="João Cabral",
        password="Abcdefjhijk1!"
    )

    create_patient(patient)

    with pytest.raises(HTTPException) as exc:
        create_patient(patient)

    assert exc.value.status_code == 409


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
    assert response.crm == doctor.crm
    assert response.name == doctor.name

def test_create_doctor_invalid_crm():
    doctor = DoctorCreate(
        cpf="52998224725",
        name="Dr Cabral",
        crm="123",
        password="Abcdefjhijk1!"
    )

    with pytest.raises(HTTPException) as exc:
        create_doctor(doctor)

    assert exc.value.status_code == 400

def test_create_doctor_duplicate_crm():
    doctor = DoctorCreate(
        cpf="52998224725",
        name="Dr Cabral",
        crm="SP123456",
        password="Abcdefjhijk1!"
    )

    create_doctor(doctor)

    with pytest.raises(HTTPException) as exc:
        create_doctor(doctor)

    assert exc.value.status_code == 409