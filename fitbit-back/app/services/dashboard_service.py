from datetime import datetime, timedelta
from app.models.mock import FitbitModel
from fastapi import HTTPException

def get_dashboard_metrics(cpf: str, period: str):
    # 1. Date calculation
    today = datetime.now()
    if period == "daily":
        start_date = today
    elif period == "weekly":
        start_date = today - timedelta(days=7)
    elif period == "monthly":
        start_date = today - timedelta(days=30)
    else:
        raise HTTPException(status_code=400, detail="Invalid period")

    start_str = start_date.strftime("%Y-%m-%d")
    end_str = today.strftime("%Y-%m-%d")

    # 2. Call the UPDATED model method
    try:
        raw_data = FitbitModel.find_by_cpf_and_date(cpf, start_str, end_str)
    except AttributeError:
        # This catches if you forgot to add the method to FitbitModel
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