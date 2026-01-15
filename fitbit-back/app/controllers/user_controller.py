from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.database.connection import get_db
from app.api.dependencies import get_current_user
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.patient_metrics import PatientMetrics
from app.core.security import get_password_hash, verify_password
from app.repositories.authorization_repository import AuthorizationRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.doctor_repository import DoctorRepository

router = APIRouter(tags=["User"])


class UserResponse(BaseModel):
    id: str
    name: str
    type: str


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None


class PatientMetricResponse(BaseModel):
    """Response model for patient health metrics."""
    date: str
    steps: int
    hr_avg: int
    sleep_hours: float
    calories: int
    source: str
    
    class Config:
        from_attributes = True


class HealthMetricsResponse(BaseModel):
    """Response model for GET /patients/{cpf}/health-metrics."""
    patient_cpf: str
    patient_name: str
    metrics: List[PatientMetricResponse]
    last_sync: Optional[str] = None
    is_data_outdated: bool = False
    total_records: int


class DoctorPatientResponse(BaseModel):
    """Response model for doctor's authorized patients."""
    cpf: str
    name: str


@router.get("/me")
def get_current_user_info(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get current authenticated user information.
    Returns: {id, name, type}
    """
    user_id = current_user["sub"]
    user_type = current_user["type"]
    
    if user_type == "patient":
        user = db.query(Patient).filter(Patient.cpf == user_id).first()
    else:
        user = db.query(Doctor).filter(Doctor.crm == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Fallback name for doctors if not set
    user_name = user.name
    if user_type == "doctor" and (not user_name or user_name.strip() == ""):
        user_name = f"Dr. {user_id}"
    
    return UserResponse(
        id=user_id,
        name=user_name,
        type=user_type
    )


@router.patch("/me")
def update_current_user(
    updates: UserUpdateRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user name and/or password.
    """
    user_id = current_user["sub"]
    user_type = current_user["type"]
    
    if user_type == "patient":
        user = db.query(Patient).filter(Patient.cpf == user_id).first()
    else:
        user = db.query(Doctor).filter(Doctor.crm == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if updates.name:
        user.name = updates.name
    
    if updates.new_password:
        if not updates.current_password:
            raise HTTPException(
                status_code=400,
                detail="Senha atual é obrigatória para alterar a senha"
            )
        if not verify_password(updates.current_password, user.password):
            raise HTTPException(
                status_code=400,
                detail="Senha atual incorreta"
            )
        if len(updates.new_password) < 12:
            raise HTTPException(
                status_code=400,
                detail="Nova senha deve ter pelo menos 12 caracteres"
            )
        user.password = get_password_hash(updates.new_password)
    
    db.commit()
    db.refresh(user)
    
    return {"success": True, "message": "Dados atualizados com sucesso"}


@router.get("/patients/{cpf}/health-metrics", response_model=HealthMetricsResponse)
def get_patient_health_metrics(
    cpf: str,
    doctor_crm: str = Query(..., description="Doctor's CRM number for authorization check"),
    period: Optional[str] = Query(None, pattern="^(daily|weekly|monthly|custom)$", description="Filter period"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> HealthMetricsResponse:
    """
    Get patient health metrics for authorized doctors.
    
    Authorization flow:
    1. Verify current user is a doctor
    2. Check data_authorization table for doctor_crm + patient_cpf
    3. Return 403 if not authorized
    4. Return metrics with >24h outdated flag
    
    Args:
        cpf: Patient CPF to query
        doctor_crm: Doctor CRM for authorization (must match JWT)
        start_date: Optional filter start date
        end_date: Optional filter end date
        
    Returns:
        HealthMetricsResponse with metrics array and metadata
        
    Raises:
        403: Patient has not authorized data sharing
        404: Patient not found
    """
    # Security: Verify JWT user is a doctor and matches provided CRM
    if current_user["type"] != "doctor":
        raise HTTPException(
            status_code=403,
            detail="Apenas médicos podem acessar dados de pacientes"
        )
    
    if current_user["sub"] != doctor_crm:
        raise HTTPException(
            status_code=403,
            detail="CRM fornecido não corresponde ao usuário autenticado"
        )
    
    # Check authorization
    auth_repo = AuthorizationRepository(db)
    is_authorized = auth_repo.check_authorization(doctor_crm, cpf)
    
    if not is_authorized:
        raise HTTPException(
            status_code=403,
            detail="Paciente não autorizou compartilhamento de dados"
        )
    
    # Get patient info
    patient_repo = PatientRepository(db)
    patient = patient_repo.find_by_cpf(cpf)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Validate and calculate date range for custom period
    if period == "custom" or (start_date and end_date):
        if not start_date or not end_date:
            raise HTTPException(
                status_code=400, 
                detail="Data inicial e final são obrigatórias para o período customizado."
            )
        
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Formato de data inválido. Use YYYY-MM-DD."
            )
        
        if start_dt > end_dt:
            raise HTTPException(
                status_code=400, 
                detail="Período inválido. Verifique as datas informadas."
            )
        
        now = datetime.now()
        if end_dt > now:
            raise HTTPException(
                status_code=400, 
                detail="A data final não pode ser posterior à data de hoje."
            )
        
        if (end_dt - start_dt).days > 365:
            raise HTTPException(
                status_code=400, 
                detail="O período customizado não pode exceder 365 dias."
            )
    elif period == "daily":
        today = datetime.now().date().isoformat()
        start_date = end_date = today
    elif period == "weekly":
        end_date = datetime.now().date().isoformat()
        start_date = (datetime.now() - timedelta(days=7)).date().isoformat()
    elif period == "monthly":
        end_date = datetime.now().date().isoformat()
        start_date = (datetime.now() - timedelta(days=30)).date().isoformat()
    else:
        # Default to last 7 days if no period specified
        end_date = datetime.now().date().isoformat()
        start_date = (datetime.now() - timedelta(days=7)).date().isoformat()
    
    # Get metrics from database only - no mock data for doctors
    metrics = patient_repo.get_metrics(cpf, start_date, end_date)
    
    # Calculate last sync and outdated flag
    last_sync = None
    is_outdated = False
    
    if metrics:
        # Most recent metric date
        latest_metric = metrics[0]  # Already ordered by date DESC
        last_sync = latest_metric.date
        
        # Check if data is >24h old
        try:
            metric_date = datetime.fromisoformat(latest_metric.date)
            now = datetime.now()
            time_diff = now - metric_date
            is_outdated = time_diff > timedelta(hours=24)
        except:
            is_outdated = False
    
    return HealthMetricsResponse(
        patient_cpf=cpf,
        patient_name=patient.name,
        metrics=[PatientMetricResponse.model_validate(m) for m in metrics],
        last_sync=last_sync,
        is_data_outdated=is_outdated,
        total_records=len(metrics)
    )


@router.get("/doctor/patients", response_model=List[DoctorPatientResponse])
def get_doctor_patients(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[DoctorPatientResponse]:
    """
    Get list of patients authorized for current doctor.
    
    **PB11**: Doctor can view list of patients who shared their data.
    
    Returns:
        List of authorized patients with CPF and name
    """
    # Only doctors can access this endpoint
    if current_user.get("type") != "doctor":
        raise HTTPException(
            status_code=403,
            detail="Apenas médicos podem acessar esta funcionalidade."
        )
    
    doctor_crm = current_user.get("sub")
    if not doctor_crm:
        raise HTTPException(status_code=400, detail="CRM do médico não encontrado.")
    
    auth_repo = AuthorizationRepository(db)
    patients = auth_repo.get_patients_by_doctor(doctor_crm)
    
    return [DoctorPatientResponse(**patient) for patient in patients]
