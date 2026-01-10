import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base, get_db
from app.services.auth_service import create_patient, create_doctor
from app.schemas.auth_schema import PatientCreate, DoctorCreate
from app.core.security import verify_password

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

# -------------------
# PATIENT
# -------------------

def test_create_patient_success(db):
    patient = PatientCreate(
        cpf="52998224725",
        name="João Cabral",
        password="Abcdefjhijk1!"
    )

    response = create_patient(patient, db)
    
    assert response.status_code in [200, 201]

def test_create_patient_invalid_name(db):
    patient = PatientCreate(
        cpf="52998224725",
        name="João123",
        password="Abcdefjhijk1!"
    )

    response = create_patient(patient, db)
    assert response.status_code == 400

def test_create_patient_invalid_cpf(db):
    patient = PatientCreate(
        cpf="11111111111",
        name="João Cabral",
        password="Abcdefjhijk1!"
    )

    response = create_patient(patient, db)
    assert response.status_code == 400

def test_create_patient_invalid_password(db):
    patient = PatientCreate(
        cpf="52998224725",
        name="João Cabral",
        password="abc"
    )

    response = create_patient(patient, db)
    assert response.status_code == 400

def test_create_patient_duplicate_cpf(db):
    patient = PatientCreate(
        cpf="52998224725",
        name="João Cabral",
        password="Abcdefjhijk1!"
    )

    create_patient(patient, db)
    response = create_patient(patient, db)
    assert response.status_code == 409

def test_patient_password_hashing(db):
    from app.models.patient import Patient
    raw_password = "PatientPassword123!"

    patient = PatientCreate(
        cpf="52998224725",
        name="John Doe",
        password=raw_password
    )

    response = create_patient(patient, db)
    assert response.status_code in [200, 201]

    # Retrieve stored record
    saved_patient = db.query(Patient).filter(Patient.cpf == patient.cpf).first()
    saved_password = saved_patient.password

    assert saved_password != raw_password
    assert saved_password.startswith("$2b$")
    assert verify_password(raw_password, saved_password) is True


# -------------------
# DOCTOR
# -------------------

def test_create_doctor_success(db):
    doctor = DoctorCreate(
        cpf="52998224725",
        name="Dr Cabral",
        crm="SP123456",
        password="Abcdefjhijk1!"
    )

    response = create_doctor(doctor, db)
    
    assert response.status_code in [200, 201]

def test_create_doctor_invalid_crm(db):
    doctor = DoctorCreate(
        cpf="52998224725",
        name="Dr Cabral",
        crm="123",
        password="Abcdefjhijk1!"
    )

    response = create_doctor(doctor, db)
    assert response.status_code == 400

def test_create_doctor_duplicate_crm(db):
    doctor = DoctorCreate(
        cpf="52998224725",
        name="Dr Cabral",
        crm="SP123456",
        password="Abcdefjhijk1!"
    )

    create_doctor(doctor, db)

    response = create_doctor(doctor, db)
    assert response.status_code == 409

def test_doctor_password_hashing(db):
    from app.models.doctor import Doctor
    
    raw_password = "DoctorPassword123!"

    doctor = DoctorCreate(
        cpf="52998224725", 
        name="Dr House",
        crm="SP123456",
        password=raw_password
    )

    response = create_doctor(doctor, db)
    assert response.status_code in [200, 201]

    # Retrieve stored record
    saved_doctor = db.query(Doctor).filter(Doctor.crm == doctor.crm).first()
    saved_password = saved_doctor.password

    assert saved_password != raw_password
    assert saved_password.startswith("$2b$")
    assert verify_password(raw_password, saved_password) is True
