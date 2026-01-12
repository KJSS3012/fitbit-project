from sqlalchemy import Column, String, Date, DateTime, Text
from sqlalchemy.sql import func
from app.database.connection import Base

class ClinicalNote(Base):
    __tablename__ = "clinical_notes"

    id = Column(String, primary_key=True, index=True)
    patient_cpf = Column(String, nullable=False, index=True)
    doctor_crm = Column(String, nullable=False, index=True)
    text = Column(Text, nullable=False)
    metric_type = Column(String, nullable=True)  # "hr", "steps", "sleep"
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)