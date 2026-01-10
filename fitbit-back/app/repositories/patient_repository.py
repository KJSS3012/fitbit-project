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
