from sqlalchemy import Column, String
from app.database.connection import Base

class Patient(Base):
    __tablename__ = "patients"

    # Per your diagram: CPF is PK (Primary Key)
    cpf = Column(String(11), primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    password = Column(String(255), nullable=False)

    # Relationships will be added here later (e.g., fitbit_data)
    # fitbit = relationship("Fitbit", back_populates="patient")
