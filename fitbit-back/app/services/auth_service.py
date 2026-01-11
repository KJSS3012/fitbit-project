from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.schemas.auth_schema import (
    PatientCreate,
    PatientResponse,
    PatientLogin,
    DoctorCreate,
    DoctorResponse,
    DoctorLogin
)
from app.services.auth_validators import (
    check_password_complexity,
    validate_cpf,
    validate_name,
    validate_crm
)

from app.core.security import get_password_hash, verify_password, create_access_token
from typing import List, Dict, Any

# PERSISTENCE TOOLS
from app.models.mock import FAKE_PATIENTS_DB, FAKE_DOCTORS_DB
from app.core.fitbit_client import save_persistence, load_persistence

# --- PATIENT LOGIC ---

def create_patient(patient_in: PatientCreate) -> JSONResponse:
    load_persistence() # Load data before checking
    
    patient_in.name = patient_in.name.upper().strip()
    patient_in.cpf = patient_in.cpf.strip()
    patient_in.password = patient_in.password.strip()

    # Validations
    if validate_name(patient_in.name): 
        return JSONResponse(status_code=400, content={"detail": validate_name(patient_in.name)})
    if validate_cpf(patient_in.cpf): 
        return JSONResponse(status_code=400, content={"detail": validate_cpf(patient_in.cpf)})
    if check_password_complexity(patient_in.password): 
        return JSONResponse(status_code=400, content={"detail": check_password_complexity(patient_in.password)})

    # Conflict check
    if any(p.get("cpf") == patient_in.cpf for p in FAKE_PATIENTS_DB):
        return JSONResponse(status_code=409, content={"detail": "CPF already registered."})

    # Persist Data
    patient_data = {
        "cpf": patient_in.cpf,
        "name": patient_in.name,
        "password": get_password_hash(patient_in.password),
    }
    FAKE_PATIENTS_DB.append(patient_data)
    save_persistence() # SAVE TO JSON

    response_data = PatientResponse(cpf=patient_data["cpf"], name=patient_data["name"])
    return JSONResponse(status_code=201, content=jsonable_encoder(response_data))


def login_patient(credentials_in: PatientLogin) -> JSONResponse:
    load_persistence() # LOAD FROM JSON TO ENSURE USER EXISTS
    
    credentials_in.cpf = credentials_in.cpf.strip()
    
    patient_record = next((p for p in FAKE_PATIENTS_DB if p.get("cpf") == credentials_in.cpf), None)
    
    if not patient_record or not verify_password(credentials_in.password, patient_record.get("password")):
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials."})

    # The 'subject' must be the CPF for the Fitbit integration to work
    access_token = create_access_token(subject=patient_record["cpf"], user_type="patient")

    return JSONResponse(status_code=200, content={"access_token": access_token, "token_type": "bearer"})


# --- DOCTOR LOGIC ---

def create_doctor(doctor_in: DoctorCreate) -> JSONResponse:
    load_persistence()
    
    doctor_in.cpf = doctor_in.cpf.strip()
    doctor_in.crm = doctor_in.crm.upper().strip()

    crm_error = validate_crm(doctor_in.crm)
    if crm_error:
        return JSONResponse(status_code=400, content={"detail": crm_error})

    if any(d.get("cpf") == doctor_in.cpf or d.get("crm") == doctor_in.crm for d in FAKE_DOCTORS_DB):
        return JSONResponse(status_code=409, content={"detail": "Doctor already registered."})
        
    doctor_data = {
        "cpf": doctor_in.cpf,
        "name": doctor_in.name.upper(),
        "crm": doctor_in.crm,
        "password": get_password_hash(doctor_in.password) 
    }
    FAKE_DOCTORS_DB.append(doctor_data)
    save_persistence() # SAVE TO JSON
    
    return JSONResponse(status_code=201, content={"message": "Doctor created"})


def login_doctor(credentials_in: DoctorLogin) -> JSONResponse:
    load_persistence()
    credentials_in.crm = credentials_in.crm.strip()

    doctor_record = next((d for d in FAKE_DOCTORS_DB if d.get("crm") == credentials_in.crm), None)
    
    if not doctor_record or not verify_password(credentials_in.password, doctor_record.get("password")):
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials."})

    access_token = create_access_token(subject=doctor_record["cpf"], user_type="doctor")

    return JSONResponse(status_code=200, content={"access_token": access_token, "token_type": "bearer"})