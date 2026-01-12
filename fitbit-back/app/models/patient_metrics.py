from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base


class PatientMetrics(Base):
    """Model for storing Fitbit metrics data synchronized from Fitbit API."""
    
    __tablename__ = "patient_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_cpf = Column(String, ForeignKey("patients.cpf"), nullable=False, index=True)
    date = Column(String, nullable=False, index=True)  # YYYY-MM-DD format
    steps = Column(Integer, default=0)
    hr_avg = Column(Integer, default=0)  # Average heart rate
    sleep_hours = Column(Float, default=0.0)
    calories = Column(Integer, default=0)
    source = Column(String, default="fitbit")  # 'fitbit' or 'manual'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<PatientMetrics(cpf={self.patient_cpf}, date={self.date}, steps={self.steps})>"
