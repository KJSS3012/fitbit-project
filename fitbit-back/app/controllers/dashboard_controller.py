from fastapi import APIRouter, Depends, Query, status
from typing import Optional

from app.schemas.dashboard_schema import DashboardResponse 
from app.services.dashboard_service import get_dashboard_metrics
from app.api.dependencies import get_current_user_cpf 

router = APIRouter(tags=["Dashboard"])

@router.get(
    "/metrics",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK
)
def read_dashboard_metrics(
    period: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    current_user_cpf: str = Depends(get_current_user_cpf) 
):
    dashboard_data = get_dashboard_metrics(cpf=current_user_cpf, period=period)
    return dashboard_data