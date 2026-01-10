from fastapi import APIRouter, Depends, Query, status
from typing import Optional, Dict

from app.schemas.dashboard_schema import DashboardResponse 
from app.services.dashboard_service import get_dashboard_metrics
from app.api.dependencies import get_current_user

router = APIRouter(tags=["Dashboard"])

@router.get(
    "/metrics",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK
)
def read_dashboard_metrics(
    period: Optional[str] = Query(None, pattern="^(daily|weekly|monthly|custom)$"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get dashboard metrics for authenticated user.
    
    JWT provides:
    - current_user["sub"]: CPF (patient) or CRM (doctor)
    - current_user["type"]: "patient" or "doctor"
    
    Logic:
    - Patient: can only see their own data
    - Doctor: can see all patients' data (future: add patient_cpf parameter)
    """
    user_identifier = current_user["sub"]  # CPF or CRM
    user_type = current_user["type"]  # "patient" or "doctor"
    
    # For patients, always use their own CPF
    # For doctors, this would need a patient_cpf parameter (future enhancement)
    cpf_to_query = user_identifier if user_type == "patient" else user_identifier
    
    dashboard_data = get_dashboard_metrics(
        cpf=cpf_to_query, 
        period=period, 
        start_date=start_date, 
        end_date=end_date
    )
    return dashboard_data
