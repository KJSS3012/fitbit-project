from datetime import datetime, timedelta
from app.models.mock import FitbitModel
from fastapi import HTTPException
from typing import Optional
from functools import lru_cache

# Implement cache for performance optimization on larger queries
@lru_cache(maxsize=100)
def get_cached_data(cpf: str, start_str: str, end_str: str):
    return FitbitModel.find_by_cpf_and_date(cpf, start_str, end_str)

def get_dashboard_metrics(
    cpf: str, 
    period: Optional[str] = None, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None
):
    today = datetime.now()
    
    # Date calculation logic
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
        if not start_date or not end_date:
            raise HTTPException(status_code=400, detail="Initial and final dates are required for custom period.")
        
        try:
            calculated_start = datetime.strptime(start_date, "%Y-%m-%d")
            calculated_end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

        if calculated_start > calculated_end:
            raise HTTPException(status_code=400, detail="Initial date cannot be greater than final date.")
        
        if calculated_end > today:
            raise HTTPException(status_code=400, detail="The date cannot be later than today's date.")

        if (calculated_end - calculated_start).days > 365:
            raise HTTPException(status_code=400, detail="The custom period cannot exceed 365 days.")
    else:
        raise HTTPException(status_code=400, detail="Invalid period or missing dates")

    start_str = calculated_start.strftime("%Y-%m-%d")
    end_str = calculated_end.strftime("%Y-%m-%d")

    # Data Fetching with Cache
    try:
        raw_data = get_cached_data(cpf, start_str, end_str)
    except AttributeError:
        raise HTTPException(status_code=500, detail="Model method not implemented")

    # Validate minimum data volume
    validate_data_volume(raw_data, period)

    if not raw_data:
        return {"activities-steps": [], "activities-heart": [], "sleep": []}

    # Ensure chronological order for charts
    raw_data.sort(key=lambda x: x["date"])

    # Aggregate data (Process averages/totals for Monthly/Weekly)
    processed_data = aggregate_metrics(raw_data, period)

    # Format Response (Fitbit Standard)
    return {
        "activities-steps": [
            {"dateTime": d["date"], "value": str(d["steps"])} for d in processed_data
        ],
        "activities-heart": [
            {"dateTime": d["date"], "value": {"restingHeartRate": d["bpm"]}} for d in processed_data
        ],
        "sleep": [
            {"dateOfSleep": d["date"], "minutesAsleep": int(d["sleep_hours"] * 60)} for d in processed_data
        ]
    }

def validate_data_volume(records: list, period: str):
    """TA.2 - Ensures sufficient data volume for specific periods."""
    if period == "monthly" and len(records) < 7:
        raise HTTPException(
            status_code=400, 
            detail="Insufficient data for monthly view. At least 7 records are required."
        )
    
def aggregate_metrics(records: list, period: str):
    if period != "monthly" or len(records) <= 7:
        return records

    aggregated = []
    for i in range(0, len(records), 7):
        chunk = records[i:i + 7]
        if not chunk: continue
        
        avg_bpm = sum(d["bpm"] for d in chunk) / len(chunk)
        total_steps = sum(d["steps"] for d in chunk)
        avg_sleep = sum(d["sleep_hours"] for d in chunk) / len(chunk)
        
        aggregated.append({
            "date": f"Week {(i//7)+1}",
            "steps": int(total_steps),
            "bpm": int(avg_bpm),
            "sleep_hours": avg_sleep
        })
    return aggregated