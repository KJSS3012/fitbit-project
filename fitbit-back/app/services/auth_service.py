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
    DoctorLogin,
)
from app.services.auth_validators import (
    check_password_complexity,
    validate_cpf,
    validate_name,
    validate_crm,
)
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.repositories.patient_repository import PatientRepository
from app.repositories.doctor_repository import DoctorRepository


# =========================
# PATIENT LOGIC
# =========================
def create_patient(patient_in: PatientCreate, db: Session) -> JSONResponse:
    """Cria um novo paciente com validação cruzada de CPF."""
    patient_in.name = patient_in.name.strip()
    patient_in.cpf = patient_in.cpf.strip()
    patient_in.password = patient_in.password.strip()

    # Validações
    name_error = validate_name(patient_in.name)
    if name_error:
        return JSONResponse(status_code=400, content={"detail": name_error})

    cpf_error = validate_cpf(patient_in.cpf)
    if cpf_error:
        return JSONResponse(status_code=400, content={"detail": cpf_error})

    password_error = check_password_complexity(patient_in.password)
    if password_error:
        return JSONResponse(status_code=400, content={"detail": password_error})

    # Repositórios para checagem cruzada
    patient_repo = PatientRepository(db)
    doctor_repo = DoctorRepository(db)

    # Verifica se CPF já existe em qualquer um dos perfis
    if patient_repo.find_by_cpf(patient_in.cpf) or doctor_repo.find_by_cpf(patient_in.cpf):
        return JSONResponse(status_code=409, content={"detail": "O CPF já está cadastrado"})

    # Cria paciente
    password_hash = get_password_hash(patient_in.password)
    db_patient = patient_repo.create(patient_in, password_hash)

    response_data = PatientResponse(cpf=db_patient.cpf, name=db_patient.name.upper())
    return JSONResponse(status_code=201, content=jsonable_encoder(response_data))


def login_patient(credentials_in: PatientLogin, db: Session) -> JSONResponse:
    """Autentica um paciente."""
    credentials_in.cpf = credentials_in.cpf.strip()

    patient_repo = PatientRepository(db)
    patient_record = patient_repo.find_by_cpf(credentials_in.cpf)

    if not patient_record or not verify_password(
        credentials_in.password, patient_record.password
    ):
        return JSONResponse(status_code=401, content={"detail": "Credenciais inválidas"})

    access_token = create_access_token(
        subject=patient_record.cpf, user_type="patient"
    )

    return JSONResponse(
        status_code=200,
        content={"access_token": access_token, "token_type": "bearer"},
    )


# =========================
# DOCTOR LOGIC
# =========================
def create_doctor(doctor_in: DoctorCreate, db: Session) -> JSONResponse:
    """Cria um novo médico com validação cruzada de CPF."""
    doctor_in.cpf = doctor_in.cpf.strip()
    doctor_in.crm = doctor_in.crm.upper().strip()
    doctor_in.name = doctor_in.name.strip()
    doctor_in.password = doctor_in.password.strip()

    # Validações
    crm_error = validate_crm(doctor_in.crm)
    if crm_error:
        return JSONResponse(status_code=400, content={"detail": crm_error})

    name_error = validate_name(doctor_in.name)
    if name_error:
        return JSONResponse(status_code=400, content={"detail": name_error})

    password_error = check_password_complexity(doctor_in.password)
    if password_error:
        return JSONResponse(status_code=400, content={"detail": password_error})

    # Repositórios
    doctor_repo = DoctorRepository(db)
    patient_repo = PatientRepository(db)

    # Verifica duplicidade de CRM
    if doctor_repo.find_by_crm(doctor_in.crm):
        return JSONResponse(status_code=409, content={"detail": "Médico já cadastrado"})

    # Verifica duplicidade de CPF em ambos os perfis
    if doctor_repo.find_by_cpf(doctor_in.cpf) or patient_repo.find_by_cpf(doctor_in.cpf):
        return JSONResponse(status_code=409, content={"detail": "O CPF já está cadastrado"})

    # Cria médico
    password_hash = get_password_hash(doctor_in.password)
    db_doctor = doctor_repo.create(doctor_in, password_hash)

    response_data = DoctorResponse(
        cpf=db_doctor.cpf,
        name=db_doctor.name.upper(),
        crm=db_doctor.crm,
    )

    return JSONResponse(status_code=201, content=jsonable_encoder(response_data))


def login_doctor(credentials_in: DoctorLogin, db: Session) -> JSONResponse:
    """Autentica um médico."""
    credentials_in.crm = credentials_in.crm.strip().upper()

    doctor_repo = DoctorRepository(db)
    doctor_record = doctor_repo.find_by_crm(credentials_in.crm)

    if not doctor_record or not verify_password(
        credentials_in.password, doctor_record.password
    ):
        return JSONResponse(status_code=401, content={"detail": "Credenciais inválidas"})

    access_token = create_access_token(
        subject=doctor_record.cpf, user_type="doctor"
    )

    return JSONResponse(
        status_code=200,
        content={"access_token": access_token, "token_type": "bearer"},
    )
