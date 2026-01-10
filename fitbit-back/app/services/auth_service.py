from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

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

# Import Repositories
from app.repositories.patient_repository import PatientRepository
from app.repositories.doctor_repository import DoctorRepository


# --- PATIENT LOGIC ---

def create_patient(patient_in: PatientCreate, db: Session) -> JSONResponse:

    # Clean input data
    patient_in.name = patient_in.name.upper().strip()
    patient_in.cpf = patient_in.cpf.strip()
    patient_in.password = patient_in.password.strip()

    # 400 Bad Request: Name validation
    name_error = validate_name(patient_in.name)
    if name_error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": name_error}
        )

    # 400 Bad Request: CPF validation
    cpf_error = validate_cpf(patient_in.cpf)
    if cpf_error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": cpf_error}
        )

    # 400 Bad Request: Password validation
    password_error = check_password_complexity(patient_in.password)
    if password_error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": password_error}
        )

    # Inicializa o Repositório
    repository = PatientRepository(db)

    # 409 Conflict: CPF duplication
    if repository.find_by_cpf(patient_in.cpf):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "CPF already registered."}
        )

    # Persist Data
    hashed_password = get_password_hash(patient_in.password)
    new_patient = repository.create(patient_in, hashed_password)

    # Prepare Response Model
    response_data = PatientResponse(
        cpf=new_patient.cpf,
        name=new_patient.name
    )

    # 201 Successful Response
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(response_data)
    )


def login_patient(credentials_in: PatientLogin, db: Session) -> JSONResponse:
    
    # Clean input data
    credentials_in.cpf = credentials_in.cpf.strip()
    credentials_in.password = credentials_in.password.strip()

    # 400 Bad Request: CPF validation
    cpf_error = validate_cpf(credentials_in.cpf)
    if cpf_error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": cpf_error}
        )
    
    # Inicializa o Repositório
    repository = PatientRepository(db)

    # 401 Unauthorized: Find user by CPF
    patient_record = repository.find_by_cpf(credentials_in.cpf)
    if not patient_record:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials."}
        )

    # 401 Unauthorized: Password verification
    if not verify_password(credentials_in.password, patient_record.password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials."}
        )

    access_token = create_access_token(subject=patient_record.cpf, user_type="patient")

    # 200 Successful Response
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )


# --- DOCTOR LOGIC ---

def create_doctor(doctor_in: DoctorCreate, db: Session) -> JSONResponse:
    
    # Clean input data
    doctor_in.name = doctor_in.name.upper().strip()
    doctor_in.cpf = doctor_in.cpf.strip()
    doctor_in.crm = doctor_in.crm.upper().strip()
    doctor_in.password = doctor_in.password.strip()

    # 400 Bad Request: Name validation
    name_error = validate_name(doctor_in.name)
    if name_error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": name_error}
        )

    # 400 Bad Request: CPF validation
    cpf_error = validate_cpf(doctor_in.cpf)
    if cpf_error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": cpf_error}
        )

    # 400 Bad Request: CRM validation
    crm_error = validate_crm(doctor_in.crm)
    if crm_error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": crm_error}
        )

    # 400 Bad Request: Password validation
    password_error = check_password_complexity(doctor_in.password)
    if password_error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": password_error}
        )
     
    # Inicializa o Repositório
    repository = DoctorRepository(db)

    # 409 Conflict: CPF duplication
    if repository.find_by_cpf(doctor_in.cpf):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "CPF already registered."}
        )
    
    # 409 Conflict: CRM duplication
    if repository.find_by_crm(doctor_in.crm):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "CRM already registered."}
        )
        
    # Persist Data
    hashed_password = get_password_hash(doctor_in.password)
    new_doctor = repository.create(doctor_in, hashed_password)
    
    # Prepare Response Model
    response_data = DoctorResponse(
        cpf=new_doctor.cpf, 
        name=new_doctor.name, 
        crm=new_doctor.crm
    )

    # 201 Successful Response
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(response_data)
    )


def login_doctor(credentials_in: DoctorLogin, db: Session) -> JSONResponse:
    
    # Clean input data
    credentials_in.crm = credentials_in.crm.strip()
    credentials_in.password = credentials_in.password.strip()

    # 400 Bad Request: CRM validation
    crm_error = validate_crm(credentials_in.crm)
    if crm_error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": crm_error}
        )

    # Inicializa o Repositório
    repository = DoctorRepository(db)

    # 401 Unauthorized: Find user by CRM
    doctor_record = repository.find_by_crm(credentials_in.crm)
    if not doctor_record:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials."}
        )

    # 401 Unauthorized: Password verification
    if not verify_password(credentials_in.password, doctor_record.password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials."}
        )

    access_token = create_access_token(subject=doctor_record.crm, user_type="doctor")

    # 200 Successful Response
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )