from typing import List, Dict, Any

# Simulating 'fitbit_data' table in a real database
fake_database = [
    {"id": 1, "cpf": "12345678900", "date": "2023-10-25", "steps": 8000, "sleep_hours": 7.5, "calories": 2100, "bpm": 72},
    {"id": 2, "cpf": "12345678900", "date": "2023-10-26", "steps": 10200, "sleep_hours": 6.0, "calories": 2400, "bpm": 78},
    {"id": 3, "cpf": "12345678900", "date": "2023-10-27", "steps": 5000, "sleep_hours": 8.0, "calories": 1800, "bpm": 68},

    {"id": 4, "cpf": "99999999999", "date": "2023-10-25", "steps": 3000, "sleep_hours": 5.0, "calories": 1200, "bpm": 82},
    {"id": 5, "cpf": "99999999999", "date": "2023-10-26", "steps": 4500, "sleep_hours": 6.5, "calories": 1500, "bpm": 76},
    {"id": 6, "cpf": "99999999999", "date": "2023-10-27", "steps": 7000, "sleep_hours": 7.0, "calories": 1900, "bpm": 74},

    {"id": 7, "cpf": "11122233344", "date": "2023-10-20", "steps": 12000, "sleep_hours": 8.5, "calories": 2600, "bpm": 65},
    {"id": 8, "cpf": "11122233344", "date": "2023-10-21", "steps": 4000, "sleep_hours": 4.5, "calories": 1400, "bpm": 88},
    {"id": 9, "cpf": "11122233344", "date": "2023-10-22", "steps": 9500, "sleep_hours": 7.0, "calories": 2300, "bpm": 70},

    {"id": 10, "cpf": "55566677788", "date": "2023-09-15", "steps": 2000, "sleep_hours": 3.5, "calories": 1100, "bpm": 90},
    {"id": 11, "cpf": "55566677788", "date": "2023-09-16", "steps": 6500, "sleep_hours": 6.0, "calories": 1700, "bpm": 77},
    {"id": 12, "cpf": "55566677788", "date": "2023-09-17", "steps": 11000, "sleep_hours": 8.0, "calories": 2500, "bpm": 69},

    {"id": 13, "cpf": "88877766655", "date": "2023-08-01", "steps": 300, "sleep_hours": 2.0, "calories": 900, "bpm": 95},
    {"id": 14, "cpf": "88877766655", "date": "2023-08-02", "steps": 15000, "sleep_hours": 9.0, "calories": 3000, "bpm": 62},
    {"id": 15, "cpf": "88877766655", "date": "2023-08-03", "steps": 7800, "sleep_hours": 6.8, "calories": 2100, "bpm": 73},

    {"id": 16, "cpf": "22233344455", "date": "2023-07-10", "steps": 5600, "sleep_hours": 7.2, "calories": 2000, "bpm": 71},
    {"id": 17, "cpf": "22233344455", "date": "2023-07-11", "steps": 8900, "sleep_hours": 7.9, "calories": 2200, "bpm": 68},
    {"id": 18, "cpf": "22233344455", "date": "2023-07-12", "steps": 10000, "sleep_hours": 6.0, "calories": 2400, "bpm": 75},

    {"id": 19, "cpf": "44455566677", "date": "2023-06-05", "steps": 0, "sleep_hours": 10.0, "calories": 1600, "bpm": 60},
    {"id": 20, "cpf": "44455566677", "date": "2023-06-06", "steps": 3200, "sleep_hours": 5.5, "calories": 1300, "bpm": 85},

    {"id": 21, "cpf": "60440964083", "date": "2023-10-21", "steps": 9000, "sleep_hours": 7.5, "calories": 2100, "bpm": 72},
    {"id": 22, "cpf": "60440964083", "date": "2023-10-24", "steps": 10000, "sleep_hours": 6.0, "calories": 2400, "bpm": 78},
    {"id": 23, "cpf": "60440964083", "date": "2023-10-26", "steps": 7000, "sleep_hours": 8.0, "calories": 1800, "bpm": 68}
]

class FitbitModel:
    @staticmethod
    def find_by_cpf(cpf: str) -> List[Dict[str, Any]]:
        """
        Simulating: SELECT * FROM fitbit_data WHERE cpf = :cpf
        """
        # Filter for records matching the given CPF
        return [record for record in fake_database if record["cpf"] == cpf]
    

FAKE_PATIENTS_DB: List[Dict[str, Any]] = [
    {
        "name": "TEST USER",
        "cpf": "12345678900", 
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxwKc.6IymCs7CN52au9gm.ma1xey"
    }
]

# Tabela Mock de Médicos
FAKE_DOCTORS_DB: List[Dict[str, Any]] = []