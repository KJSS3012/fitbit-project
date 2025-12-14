from pydantic import BaseModel

# --- PATIENT ---
class PatientBase(BaseModel):
    cpf: str
    name: str

class PatientCreate(PatientBase):
    password: str

class PatientResponse(PatientBase):
    class Config:
        from_attributes = True