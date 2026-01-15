from datetime import datetime, timedelta
from app.models.mock import FitbitModel, FAKE_PATIENTS_DB
from app.core.fitbit_client import get_valid_token, fetch_fitbit_data
from app.repositories.patient_repository import PatientRepository
from fastapi import HTTPException
from typing import Optional
from functools import lru_cache
from sqlalchemy.orm import Session

@lru_cache(maxsize=100)
def get_cached_data(cpf: str, start_str: str, end_str: str):
    return FitbitModel.find_by_cpf_and_date(cpf, start_str, end_str)

def get_dashboard_metrics(
    cpf: str, 
    period: Optional[str] = None, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    db: Optional[Session] = None
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
            raise HTTPException(status_code=400, detail="Data inicial e final são obrigatórias para o período customizado.")
        
        try:
            calculated_start = datetime.strptime(start_date, "%Y-%m-%d")
            calculated_end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD.")

        if calculated_start > calculated_end:
            raise HTTPException(status_code=400, detail="Período inválido. Verifique as datas informadas.")
        
        if calculated_end > today:
            raise HTTPException(status_code=400, detail="A data final não pode ser posterior à data de hoje.")

        if (calculated_end - calculated_start).days > 365:
            raise HTTPException(status_code=400, detail="O período customizado não pode exceder 365 dias.")
    else:
        raise HTTPException(status_code=400, detail="Período inválido ou datas ausentes.")

    start_str = calculated_start.strftime("%Y-%m-%d")
    end_str = calculated_end.strftime("%Y-%m-%d")

    # If DB session provided, fetch from patient_metrics table (real data)
    if db:
        patient_repo = PatientRepository(db)
        raw_data_list = patient_repo.get_metrics(cpf, start_str, end_str)
        
        # If no data in DB, continue to fallback mock path (for unit tests)
        if raw_data_list:
            raw_data = [
                {
                    "date": str(m.date),
                    "steps": m.steps or 0,
                    "bpm": int(m.hr_avg) if m.hr_avg else 0,
                    "sleep_hours": m.sleep_hours or 0.0,
                    "calories": m.calories or 0
                }
                for m in raw_data_list
            ]
        else:
            raw_data = []
    else:
        # No DB session provided - fallback to cached/mock data (test compatibility)
        raw_data = get_cached_data(cpf, start_str, end_str)

    # Validate minimum data volume
    validate_data_volume(raw_data, period)

    if not raw_data:
        return {"activities-steps": [], "activities-heart": [], "sleep": []}

    raw_data.sort(key=lambda x: x["date"])
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
        ],
        "activities-calories": [
            {"dateTime": d["date"], "value": str(d.get("calories", 0))} for d in processed_data
        ]
    }

def validate_data_volume(records: list, period: str):
    # Restore minimum data rules for tests: monthly requires at least 7 records
    if period == "monthly" and len(records) < 7:
        raise HTTPException(status_code=400, detail="São necessários pelo menos 7 registros para visão mensal")
    
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
        total_calories = sum(d.get("calories", 0) for d in chunk)
        
        aggregated.append({
            "date": f"Week {(i//7)+1}",
            "steps": int(total_steps),
            "bpm": int(avg_bpm),
            "sleep_hours": avg_sleep,
            "calories": int(total_calories)
        })
    return aggregated


def get_metrics_summary(cpf: str, period: str, db: Session = None):
    """
    Calculate aggregated metrics summary for specified period.
    
    Args:
        cpf: Patient CPF
        period: "7d" for last 7 days, "30d" for last 30 days
        db: Database session (optional, for real data from patient_metrics)
        
    Returns:
        Dict with aggregated statistics
    """
    # Calculate date range
    days = 7 if period == "7d" else 30
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # Fetch data from patient_metrics if db available, else mock
    if db:
        repo = PatientRepository(db)
        metrics = repo.get_metrics(cpf, start_str, end_str)
        
        if not metrics:
            raw_data = []
        else:
            raw_data = [
                {
                    "date": m.date,
                    "steps": m.steps,
                    "bpm": m.hr_avg,
                    "sleep_hours": m.sleep_hours,
                    "calories": m.calories
                }
                for m in metrics
            ]
    else:
        # Fallback to mock data
        try:
            raw_data = get_cached_data(cpf, start_str, end_str)
        except:
            raw_data = []
    
    if not raw_data:
        return {
            "period": period,
            "days_analyzed": 0,
            "steps_total": 0,
            "steps_average": 0,
            "steps_max": 0,
            "hr_average": 0,
            "hr_min": 0,
            "hr_max": 0,
            "sleep_total_hours": 0.0,
            "sleep_average_hours": 0.0,
            "calories_total": 0,
            "calories_average": 0,
            "last_data_date": None,
            "days_since_last_data": None
        }
    
    # Calculate aggregations
    steps_list = [d["steps"] for d in raw_data]
    bpm_list = [d["bpm"] for d in raw_data if d["bpm"] > 0]
    sleep_list = [d["sleep_hours"] for d in raw_data]
    calories_list = [d["calories"] for d in raw_data]
    
    # Calculate days since last data
    last_date_str = raw_data[-1]["date"] if raw_data else None
    days_since_last = None
    if last_date_str:
        try:
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
            days_since_last = (datetime.now() - last_date).days
        except:
            days_since_last = None
    
    return {
        "period": period,
        "days_analyzed": len(raw_data),
        "steps_total": sum(steps_list),
        "steps_average": int(sum(steps_list) / len(steps_list)) if steps_list else 0,
        "steps_max": max(steps_list) if steps_list else 0,
        "hr_average": int(sum(bpm_list) / len(bpm_list)) if bpm_list else 0,
        "hr_min": min(bpm_list) if bpm_list else 0,
        "hr_max": max(bpm_list) if bpm_list else 0,
        "sleep_total_hours": round(sum(sleep_list), 1),
        "sleep_average_hours": round(sum(sleep_list) / len(sleep_list), 1) if sleep_list else 0.0,
        "calories_total": sum(calories_list),
        "calories_average": int(sum(calories_list) / len(calories_list)) if calories_list else 0,
        "last_data_date": last_date_str,
        "days_since_last_data": days_since_last
    }