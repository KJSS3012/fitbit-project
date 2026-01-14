from sqlalchemy import Column, String, Float
from app.database.connection import Base

class Patient(Base):
    __tablename__ = "patients"

    # Per your diagram: CPF is PK (Primary Key)
    cpf = Column(String(11), primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    password = Column(String(255), nullable=False)
    
    # Fitbit OAuth tokens
    fitbit_access_token = Column(String(512), nullable=True)
    fitbit_refresh_token = Column(String(512), nullable=True)
    fitbit_expires_at = Column(Float, nullable=True)

    # Relationships will be added here later (e.g., fitbit_data)
    # fitbit = relationship("Fitbit", back_populates="patient")
