from fastapi import status, HTTPException
from app.schemas.auth_schema import PatientCreate, PatientResponse
from app.services.auth_validators import (
    check_password_complexity,
    validate_cpf,
    validate_name, 
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
    if any(p["cpf"] == patient_in.cpf for p in fake_patients_db):
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
