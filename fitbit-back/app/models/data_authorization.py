from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base


class DataAuthorization(Base):
    """Model for doctor-patient data sharing authorization."""
    
    __tablename__ = "data_authorization"

    doctor_crm = Column(String, ForeignKey("doctors.crm"), primary_key=True, nullable=False)
    patient_cpf = Column(String, ForeignKey("patients.cpf"), primary_key=True, nullable=False)
    authorized = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<DataAuthorization(doctor_crm={self.doctor_crm}, patient_cpf={self.patient_cpf}, authorized={self.authorized})>"
