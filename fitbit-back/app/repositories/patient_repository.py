from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.schemas.auth_schema import PatientCreate

class PatientRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, patient_data: PatientCreate, password_hash: str) -> Patient:
        db_patient = Patient(
            cpf=patient_data.cpf,
            name=patient_data.name,
            password=password_hash
        )
        self.db.add(db_patient)
        self.db.commit()
        self.db.refresh(db_patient)
        return db_patient

    def find_by_cpf(self, cpf: str) -> Patient | None:
        return self.db.query(Patient).filter(Patient.cpf == cpf).first()
    
    def update_fitbit_tokens(
        self, 
        cpf: str, 
        access_token: str, 
        refresh_token: str, 
        expires_at: float
    ) -> Patient | None:
        """Update Fitbit OAuth tokens for a patient."""
        patient = self.find_by_cpf(cpf)
        if not patient:
            return None
        
        patient.fitbit_access_token = access_token
        patient.fitbit_refresh_token = refresh_token
        patient.fitbit_expires_at = expires_at
        
        self.db.commit()
        self.db.refresh(patient)
        return patient
    
    def remove_fitbit_tokens(self, cpf: str) -> Patient | None:
        """Remove Fitbit tokens (disconnect)."""
        patient = self.find_by_cpf(cpf)
        if not patient:
            return None
        
        patient.fitbit_access_token = None
        patient.fitbit_refresh_token = None
        patient.fitbit_expires_at = None
        
        self.db.commit()
        self.db.refresh(patient)
        return patient
