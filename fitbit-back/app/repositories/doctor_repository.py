from sqlalchemy.orm import Session
from app.models.doctor import Doctor
from app.schemas.auth_schema import DoctorCreate

class DoctorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, doctor_data: DoctorCreate, password_hash: str) -> Doctor:
        db_doctor = Doctor(
            cpf=doctor_data.cpf,
            name=doctor_data.name,
            crm=doctor_data.crm,
            password=password_hash
        )
        self.db.add(db_doctor)
        self.db.commit()
        self.db.refresh(db_doctor)
        return db_doctor

    def find_by_cpf(self, cpf: str) -> Doctor | None:
        return self.db.query(Doctor).filter(Doctor.cpf == cpf).first()

    def find_by_crm(self, crm: str) -> Doctor | None:
        return self.db.query(Doctor).filter(Doctor.crm == crm).first()
