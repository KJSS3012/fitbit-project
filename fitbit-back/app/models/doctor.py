from sqlalchemy import Column, String
from app.database.connection import Base

class Doctor(Base):
    __tablename__ = "doctors" # 'MEDIC' in diagram, typically 'doctors' in code

    # Per your diagram: CPF is PK, CRM is Unique
    cpf = Column(String(11), primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    crm = Column(String(8), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)