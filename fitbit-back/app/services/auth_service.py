from fastapi import status, HTTPException
from app.schemas.auth_schema import PatientCreate, PatientResponse, DoctorCreate, DoctorResponse
from app.services.auth_validators import (
    check_password_complexity,
    validate_cpf,
    validate_name,
    validate_crm
)
from typing import List, Dict, Any


# In-memory "tables" (Mock DB)
fake_patients_db: List[Dict[str, Any]] = []
fake_doctors_db: List[Dict[str, Any]] = []


# --- Patient Logic ---
def create_patient(patient_in: PatientCreate) -> PatientResponse:

    # 400 Bad Request: Name validation
    name_errors = validate_name(patient_in.name)
    if name_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=name_errors
        )

    # 400 Bad Request: CPF validation
    cpf_errors = validate_cpf(patient_in.cpf)
    if cpf_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=cpf_errors
        )

    # 400 Bad Request: Password validation
    password_errors = check_password_complexity(patient_in.password)
    if password_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_errors
        )

    # 409 Conflict: CPF duplication
    if any(p.get("cpf") == patient_in.cpf for p in fake_patients_db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF already registered."
        )

    # 201 Successful Response: Patient created
    patient_data = {
        "cpf": patient_in.cpf,
        "name": patient_in.name,
        "password": patient_in.password,
    }
    fake_patients_db.append(patient_data)

    return PatientResponse(
        cpf=patient_data["cpf"],
        name=patient_data["name"]
    )

# --- Doctor Logic ---
def create_doctor(doctor_in: DoctorCreate) -> DoctorResponse:
    
    # 400 Bad Request: Name validation
    name_errors = validate_name(doctor_in.name)
    if name_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=name_errors
        )

    # 400 Bad Request: CPF validation
    cpf_errors = validate_cpf(doctor_in.cpf)
    if cpf_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=cpf_errors
        )

    # 400 Bad Request: CRM validation
    crm_errors = validate_crm(doctor_in.crm)
    if crm_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=crm_errors
        )

    # 400 Bad Request: Password validation
    password_errors = check_password_complexity(doctor_in.password)
    if password_errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_errors
        )
    
    # 409 Conflict: CRM duplication (UNIQUE constraint)
    if any(d.get("crm") == doctor_in.crm for d in fake_doctors_db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CRM already registered."
        )
        
    # 201 Successful Response: Doctor created
    doctor_data = {
        "cpf": doctor_in.cpf,
        "name": doctor_in.name,
        "crm": doctor_in.crm,
        "password": doctor_in.password 
    }
    fake_doctors_db.append(doctor_data)
    
    return DoctorResponse(
        cpf=doctor_data["cpf"], 
        name=doctor_data["name"], 
        crm=doctor_data["crm"]
    )