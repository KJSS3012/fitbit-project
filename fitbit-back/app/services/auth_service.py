from fastapi import status, HTTPException
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
from typing import List, Dict, Any


# In-memory "tables" (Mock DB)
fake_patients_db: List[Dict[str, Any]] = []
fake_doctors_db: List[Dict[str, Any]] = []


# --- PATIENT LOGIC ---

def create_patient(patient_in: PatientCreate) -> PatientResponse:

    # Clean input data
    patient_in.name = patient_in.name.upper().strip()
    patient_in.cpf = patient_in.cpf.strip()
    patient_in.password = patient_in.password.strip()

    # 400 Bad Request: Name validation
    name_error = validate_name(patient_in.name)
    if name_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=name_error
        )

    # 400 Bad Request: CPF validation
    cpf_error = validate_cpf(patient_in.cpf)
    if cpf_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=cpf_error
        )

    # 400 Bad Request: Password validation
    password_error = check_password_complexity(patient_in.password)
    if password_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_error
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

def login_patient(credentials_in: PatientLogin) -> PatientResponse:
    
    # Clean input data
    credentials_in.cpf = credentials_in.cpf.strip()
    credentials_in.password = credentials_in.password.strip()

    # 400 Bad Request: CPF validation
    cpf_error = validate_cpf(credentials_in.cpf)
    if cpf_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=cpf_error
        )
    
    # 401 Unauthorized: Find user by CPF
    patient_record = next(
        (p for p in fake_patients_db if p.get("cpf") == credentials_in.cpf),
        None
    )
    if not patient_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

    # 401 Unauthorized: Password verification
    if patient_record.get("password") != credentials_in.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

    # 200 Successful Response: Authentication successful
    return PatientResponse(
        cpf=patient_record["cpf"],
        name=patient_record["name"]
    )

# --- DOCTOR LOGIC ---

def create_doctor(doctor_in: DoctorCreate) -> DoctorResponse:
    
    # Clean input data
    doctor_in.name = doctor_in.name.upper().strip()
    doctor_in.cpf = doctor_in.cpf.strip()
    doctor_in.crm = doctor_in.crm.upper().strip()
    doctor_in.password = doctor_in.password.strip()

    # 400 Bad Request: Name validation
    name_error = validate_name(doctor_in.name)
    if name_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=name_error
        )

    # 400 Bad Request: CPF validation
    cpf_error = validate_cpf(doctor_in.cpf)
    if cpf_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=cpf_error
        )

    # 400 Bad Request: CRM validation
    crm_error = validate_crm(doctor_in.crm)
    if crm_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=crm_error
        )

    # 400 Bad Request: Password validation
    password_error = check_password_complexity(doctor_in.password)
    if password_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_error
        )
     
    # 409 Conflict: CPF duplication
    if any(p.get("cpf") == doctor_in.cpf for p in fake_doctors_db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF already registered."
        )
    
    # 409 Conflict: CRM duplication
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

def login_doctor(credentials_in: DoctorLogin) -> DoctorResponse:
    
    # Clean input data
    credentials_in.crm = credentials_in.crm.strip()
    credentials_in.password = credentials_in.password.strip()

    # 400 Bad Request: CRM validation
    crm_error = validate_crm(credentials_in.crm)
    if crm_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=crm_error
        )

    # 401 Unauthorized: Find user by CRM
    doctor_record = next(
        (d for d in fake_doctors_db if d.get("crm") == credentials_in.crm),
        None
    )
    if not doctor_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

    # 401 Unauthorized: Password verification 
    if doctor_record.get("password") != credentials_in.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

    # 200 Successful Response: Authentication successful
    return DoctorResponse(
        cpf=doctor_record["cpf"],
        crm=doctor_record["crm"],
        name=doctor_record["name"]
    )
