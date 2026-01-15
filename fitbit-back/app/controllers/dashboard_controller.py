from fastapi import APIRouter, Depends, Query, status
from typing import Optional, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.schemas.dashboard_schema import DashboardResponse 
from app.services.dashboard_service import get_dashboard_metrics, get_metrics_summary
from app.api.dependencies import get_current_user
from app.database.connection import get_db


class MetricsSummaryResponse(BaseModel):
    """Aggregated metrics summary for specified period."""
    period: str
    days_analyzed: int
    steps_total: int
    steps_average: int
    steps_max: int
    hr_average: int
    hr_min: int
    hr_max: int
    sleep_total_hours: float
    sleep_average_hours: float
    calories_total: int
    calories_average: int
    last_data_date: Optional[str] = None
    days_since_last_data: Optional[int] = None


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
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
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
        end_date=end_date,
        db=db
    )
    return dashboard_data


@router.get(
    "/metrics/summary",
    response_model=MetricsSummaryResponse,
    status_code=status.HTTP_200_OK
)
def read_metrics_summary(
    period: str = Query(..., pattern="^(7d|30d)$", description="Period: 7d or 30d"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get aggregated metrics summary for last 7 or 30 days.
    
    Returns calculated statistics:
    - Steps: total, average, max
    - Heart Rate: average, min, max
    - Sleep: total hours, average hours
    - Calories: total, average
    - Data freshness: days since last data
    
    Args:
        period: "7d" for last 7 days, "30d" for last 30 days
        
    Returns:
        MetricsSummaryResponse with aggregated statistics
    """
    user_identifier = current_user["sub"]
    user_type = current_user["type"]
    
    cpf_to_query = user_identifier if user_type == "patient" else user_identifier
    
    summary = get_metrics_summary(cpf=cpf_to_query, period=period, db=db)
    return summary
