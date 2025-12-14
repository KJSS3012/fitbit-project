from app.schemas.auth_schema import PatientCreate, PatientResponse

# In-memory "tables"
fake_patients_db = []
fake_doctors_db = []

# --- Patient Logic ---
def create_patient(patient_in: PatientCreate) -> PatientResponse:
    user_data = {
        "cpf": patient_in.cpf,
        "name": patient_in.name,
        "password": patient_in.password
    }
    fake_patients_db.append(user_data)
    return PatientResponse(**user_data)