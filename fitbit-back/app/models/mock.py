from typing import List, Dict, Any

# Simulating 'fitbit_data' table in a real database
fake_database = [
    {"id": 1, "cpf": "12345678900", "date": "2023-10-25", "steps": 8000, "sleep_hours": 7.5, "calories": 2100, "bpm": 72},
    {"id": 2, "cpf": "12345678900", "date": "2023-10-26", "steps": 10200, "sleep_hours": 6.0, "calories": 2400, "bpm": 78},
    {"id": 21, "cpf": "60440964083", "date": "2026-01-09", "steps": 9500, "sleep_hours": 7.4, "calories": 2300, "bpm": 72},
    {"id": 70, "cpf": "60440964083", "date": "2025-04-17", "steps": 10400, "sleep_hours": 6.9, "calories": 2450, "bpm": 77}
]

class FitbitModel:
    @staticmethod
    def find_by_cpf_and_date(cpf: str, start_date: str, end_date: str):
        user_records = [d for d in fake_database if d["cpf"] == cpf]
        filtered = [
            d for d in user_records 
            if start_date <= d["date"] <= end_date
        ]
        return filtered

FAKE_PATIENTS_DB: List[Dict[str, Any]] = []

FAKE_DOCTORS_DB: List[Dict[str, Any]] = []