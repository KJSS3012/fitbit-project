from fastapi import APIRouter
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.schemas.auth_schema import (
    PatientCreate,
    PatientLogin,
    DoctorCreate,
    DoctorLogin
)
from app.services.auth_service import (
    create_patient,
    login_patient,
    create_doctor,
    login_doctor
)

load_dotenv()

router = APIRouter(tags=["Authentication", "Fitbit"])


# --- PATIENT ROUTES ---

@router.post("/register/patient")
def register_patient(patient: PatientCreate) -> JSONResponse:
    return create_patient(patient)

@router.post("/login/patient")
def login_patient_route(credentials: PatientLogin) -> JSONResponse:
    return login_patient(credentials)


# --- DOCTOR ROUTES ---

@router.post("/register/doctor")
def register_doctor(doctor: DoctorCreate) -> JSONResponse:
    return create_doctor(doctor)

@router.post("/login/doctor")
def login_doctor_route(credentials: DoctorLogin) -> JSONResponse:
    return login_doctor(credentials)