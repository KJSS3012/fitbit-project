from datetime import datetime, timedelta
from app.models.mock import FitbitModel
from fastapi import HTTPException
from typing import Optional

def get_dashboard_metrics(
    cpf: str, 
    period: Optional[str] = None, # Alterado para opcional
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None
):
    today = datetime.now()
    
    # 1. Date calculation logic
    if period == "daily":
        calculated_start = today
        calculated_end = today
    elif period == "weekly":
        calculated_start = today - timedelta(days=7)
        calculated_end = today
    elif period == "monthly":
        calculated_start = today - timedelta(days=30)
        calculated_end = today
    elif period == "custom" or (start_date and end_date):

        # Scenario 6: Mandatory dates for custom period
        if not start_date or not end_date:
            raise HTTPException(
                status_code=400, 
                detail="Initial and final dates are required for custom period."
            )
        
        try:
            calculated_start = datetime.strptime(start_date, "%Y-%m-%d")
            calculated_end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

        # Scenario 5: Initial date cannot be greater than final date
        if calculated_start > calculated_end:
            raise HTTPException(
                status_code=400, 
                detail="Initial date cannot be greater than final date."
            )
        
        if calculated_end > today:
            raise HTTPException(
                status_code=400, 
                detail="The date cannot be later than today's date."
            )

        if (calculated_end - calculated_start).days > 365:
            raise HTTPException(
                status_code=400, 
                detail="The custom period cannot exceed 365 days."
            )

    else:
        # Erro caso o front não mande nem período, nem datas
        raise HTTPException(status_code=400, detail="Invalid period or missing dates")

    start_str = calculated_start.strftime("%Y-%m-%d")
    end_str = calculated_end.strftime("%Y-%m-%d")

    # 2. Call the model method
    try:
        raw_data = FitbitModel.find_by_cpf_and_date(cpf, start_str, end_str)
    except AttributeError:
        raise HTTPException(status_code=500, detail="Model method not implemented")
    
    # 3. Format Response (Fitbit Standard)
    return {
        "activities-steps": [
            {"dateTime": d["date"], "value": str(d["steps"])} for d in raw_data
        ],
        "activities-heart": [
            {"dateTime": d["date"], "value": {"restingHeartRate": d["bpm"]}} for d in raw_data
        ],
        "sleep": [
            {"dateOfSleep": d["date"], "minutesAsleep": int(d["sleep_hours"] * 60)} for d in raw_data
        ]
    }