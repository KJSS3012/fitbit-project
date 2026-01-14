from sqlalchemy.orm import Session
from app.models.clinical_notes import ClinicalNote
from typing import List

class ClinicalNotesRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create_note(self, note: ClinicalNote) -> ClinicalNote:
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    async def get_notes_by_patient(self, cpf: str, limit: int = 50) -> List[ClinicalNote]:
        return self.db.query(ClinicalNote).filter(
            ClinicalNote.patient_cpf == cpf
        ).order_by(ClinicalNote.created_at.desc()).limit(limit).all()

    async def delete_note(self, note_id: str) -> bool:
        note = self.db.query(ClinicalNote).filter(ClinicalNote.id == note_id).first()
        if not note:
            return False
        self.db.delete(note)
        self.db.commit()
        return True