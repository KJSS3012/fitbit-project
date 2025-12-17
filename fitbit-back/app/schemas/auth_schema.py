from pydantic import BaseModel

# --- PATIENT ---
class PatientBase(BaseModel):
    cpf: str
    name: str

class PatientCreate(PatientBase):
    password: str

class PatientLogin(BaseModel): 
    cpf: str
    password: str

class PatientResponse(PatientBase):
    class ConfigDict:
        from_attributes = True

# --- DOCTOR ---
class DoctorBase(BaseModel):
    cpf: str
    crm: str
    name: str

class DoctorCreate(DoctorBase):
    password: str

class DoctorResponse(DoctorBase):
    class ConfigDict:
        from_attributes = True