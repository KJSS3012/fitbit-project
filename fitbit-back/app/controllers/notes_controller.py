from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from app.database.connection import get_db
from app.api.dependencies import get_current_user
from app.models.clinical_notes import ClinicalNote
from app.repositories.clinical_notes_repository import ClinicalNotesRepository
import uuid

router = APIRouter()

class CreateNoteRequest(BaseModel):
    patient_cpf: str
    text: str
    metric_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class NoteResponse(BaseModel):
    id: str
    patient_cpf: str
    doctor_crm: str
    text: str
    metric_type: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    created_at: str

@router.post("/notes", response_model=dict)
async def create_note(
    request: CreateNoteRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.get("type") != "medico":
        raise HTTPException(status_code=403, detail="Apenas médicos podem criar anotações")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Texto da anotação não pode ser vazio")

    repo = ClinicalNotesRepository(db)
    note = ClinicalNote(
        id=str(uuid.uuid4()),
        patient_cpf=request.patient_cpf,
        doctor_crm=current_user["crm"],
        text=request.text.strip(),
        metric_type=request.metric_type,
        start_date=request.start_date,
        end_date=request.end_date
    )
    await repo.create_note(note)
    return {"success": True, "message": "Anotação registrada com sucesso"}

@router.get("/notes/{cpf}", response_model=List[NoteResponse])
async def get_notes(
    cpf: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Allow patient to see their own notes, or doctor with access
    if current_user["cpf"] != cpf and current_user.get("type") != "medico":
        raise HTTPException(status_code=403, detail="Acesso negado")

    repo = ClinicalNotesRepository(db)
    notes = await repo.get_notes_by_patient(cpf)
    return [
        NoteResponse(
            id=note.id,
            patient_cpf=note.patient_cpf,
            doctor_crm=note.doctor_crm,
            text=note.text,
            metric_type=note.metric_type,
            start_date=note.start_date,
            end_date=note.end_date,
            created_at=note.created_at.isoformat()
        ) for note in notes
    ]