from fastapi import APIRouter, status
from dotenv import load_dotenv

from app.schemas.auth_schema import (
    PatientCreate,
    PatientResponse,
    PatientLogin,
    DoctorCreate,
    DoctorResponse
)
from app.services.auth_service import (
    create_patient,
    login_patient,
    create_doctor
)

load_dotenv()

router = APIRouter(tags=["Authentication", "Fitbit"])


# --- PATIENT ROUTES ---

@router.post(
    "/register/patient",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED
)
def register_patient(patient: PatientCreate):
    return create_patient(patient)

@router.post(
    "/login/patient",
    response_model=PatientResponse,
) 
def login_patient_route(credentials: PatientLogin):
    patient = login_patient(credentials) 
    return patient


# --- DOCTOR ROUTES ---

@router.post(
    "/register/doctor",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED
)
def register_doctor(doctor: DoctorCreate):
    return create_doctor(doctor)