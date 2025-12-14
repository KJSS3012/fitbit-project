from fastapi import APIRouter, status
from app.schemas.auth_schema import PatientCreate, PatientResponse 
from app.services.auth_service import create_patient

# Initialize the router to group these endpoints under the "/auth" URL prefix
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Define a POST endpoint at "/auth/register/patient"
@router.post("/register/patient", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def register_patient(patient: PatientCreate):
    return create_patient(patient)
