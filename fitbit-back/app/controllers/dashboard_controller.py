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
    period: Optional[str] = Query(None, pattern="^(daily|weekly|monthly|custom)$"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    current_user_cpf: str = Depends(get_current_user_cpf) 
):
    dashboard_data = get_dashboard_metrics(
        cpf=current_user_cpf, 
        period=period, 
        start_date=start_date, 
        end_date=end_date
    )
    return dashboard_data