from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database.connection import get_db

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
def register_patient(patient: PatientCreate, db: Session = Depends(get_db)) -> JSONResponse:
    return create_patient(patient, db)

@router.post("/login/patient")
def login_patient_route(credentials: PatientLogin, db: Session = Depends(get_db)) -> JSONResponse:
    return login_patient(credentials, db)


# --- DOCTOR ROUTES ---

@router.post("/register/doctor")
def register_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)) -> JSONResponse:
    return create_doctor(doctor, db)

@router.post("/login/doctor")
def login_doctor_route(credentials: DoctorLogin, db: Session = Depends(get_db)) -> JSONResponse:
    return login_doctor(credentials, db)