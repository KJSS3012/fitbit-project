"""
Authorization controller for managing doctor-patient data sharing permissions.
PB11: Patient controls which doctors can access their health data.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from pydantic import BaseModel

from app.database.connection import get_db
from app.api.dependencies import get_current_user
from app.repositories.authorization_repository import AuthorizationRepository
from app.repositories.doctor_repository import DoctorRepository

router = APIRouter(tags=["Authorization"])


class DoctorAuthorizationResponse(BaseModel):
    """Response model for doctor authorization status."""
    crm: str
    doctor_name: str
    authorized: bool


class ToggleAuthorizationResponse(BaseModel):
    """Response model for toggle authorization action."""
    success: bool
    message: str
    authorized: bool


class AddDoctorRequest(BaseModel):
    """Request model for adding new doctor authorization."""
    doctor_crm: str


@router.get("/doctors", response_model=List[DoctorAuthorizationResponse])
def list_authorized_doctors(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[DoctorAuthorizationResponse]:
    """
    Get list of doctors with authorization status for current patient.
    
    **PB11 Scenario 4**: Empty state returns []
    
    Returns:
        List of doctors with CRM, name, and authorization status
    """
    # Only patients can manage authorizations
    if current_user["type"] != "patient":
        raise HTTPException(status_code=403, detail="Apenas pacientes podem gerenciar autorizações")
    
    patient_cpf = current_user["sub"]
    auth_repo = AuthorizationRepository(db)
    
    doctors = auth_repo.get_patient_authorized_doctors(patient_cpf)
    
    return [
        DoctorAuthorizationResponse(
            crm=doctor["crm"],
            doctor_name=doctor["doctor_name"],
            authorized=doctor["authorized"]
        )
        for doctor in doctors
    ]


@router.patch("/doctors/{crm}", response_model=ToggleAuthorizationResponse)
def toggle_doctor_authorization(
    crm: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ToggleAuthorizationResponse:
    """
    Toggle doctor's authorization to access patient data.
    
    **PB11 Scenario 1**: Grant authorization → "Compartilhamento ativado"
    **PB11 Scenario 2**: Revoke authorization → "Revogado" + audit log
    **PB11 Scenario 3**: Audit error → rollback + error message
    
    Args:
        crm: Doctor's CRM number
        
    Returns:
        Success message with new authorization status
    """
    # Only patients can toggle authorizations
    if current_user["type"] != "patient":
        raise HTTPException(status_code=403, detail="Apenas pacientes podem alterar autorizações")
    
    patient_cpf = current_user["sub"]
    auth_repo = AuthorizationRepository(db)
    
    try:
        result = auth_repo.toggle_authorization_with_audit(crm, patient_cpf)
        
        if result["authorized"]:
            message = "Compartilhamento ativado com sucesso"
        else:
            message = "Compartilhamento revogado com sucesso"
        
        return ToggleAuthorizationResponse(
            success=True,
            message=message,
            authorized=result["authorized"]
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except RuntimeError as e:
        # PB11 Scenario 3: Audit error
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao registrar auditoria. Operação não concluída: {str(e)}"
        )


@router.post("/doctors", response_model=ToggleAuthorizationResponse)
def add_doctor_authorization(
    request: AddDoctorRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ToggleAuthorizationResponse:
    """
    Add new doctor authorization for patient.
    
    Args:
        request: Contains doctor_crm to authorize
        
    Returns:
        Success message with authorization created
    """
    # Only patients can add authorizations
    if current_user["type"] != "patient":
        raise HTTPException(status_code=403, detail="Apenas pacientes podem adicionar médicos")
    
    patient_cpf = current_user["sub"]
    
    # Validate doctor exists
    doctor_repo = DoctorRepository(db)
    doctor = doctor_repo.find_by_crm(request.doctor_crm)
    
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Médico com CRM {request.doctor_crm} não encontrado")
    
    # Create authorization
    auth_repo = AuthorizationRepository(db)
    
    try:
        auth_repo.grant_new_authorization(request.doctor_crm, patient_cpf)
        
        return ToggleAuthorizationResponse(
            success=True,
            message=f"Dr. {doctor.name} adicionado com sucesso",
            authorized=True
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao adicionar médico: {str(e)}"
        )
