from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from pydantic import BaseModel

from app.database.connection import get_db
from app.api.dependencies import get_current_user
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.core.security import get_password_hash

router = APIRouter(tags=["User"])


class UserResponse(BaseModel):
    id: str
    name: str
    type: str


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None


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
    
    return UserResponse(
        id=user_id,
        name=user.name,
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
    
    if updates.password:
        if len(updates.password) < 12:
            raise HTTPException(
                status_code=400,
                detail="Senha deve ter pelo menos 12 caracteres"
            )
        user.password = get_password_hash(updates.password)
    
    db.commit()
    db.refresh(user)
    
    return {"success": True, "message": "Dados atualizados com sucesso"}
