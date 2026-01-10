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


    # Unique CPF with more extensive data for testing
    {"id": 21, "cpf": "60440964083", "date": "2026-01-09", "steps": 9500, "sleep_hours": 7.4, "calories": 2300, "bpm": 72},
    {"id": 22, "cpf": "60440964083", "date": "2026-01-08", "steps": 8200, "sleep_hours": 6.8, "calories": 2100, "bpm": 70},
    {"id": 23, "cpf": "60440964083", "date": "2026-01-07", "steps": 10400, "sleep_hours": 7.9, "calories": 2450, "bpm": 75},
    {"id": 24, "cpf": "60440964083", "date": "2026-01-06", "steps": 7300, "sleep_hours": 8.1, "calories": 1950, "bpm": 68},
    {"id": 25, "cpf": "60440964083", "date": "2026-01-05", "steps": 9800, "sleep_hours": 7.0, "calories": 2350, "bpm": 74},

    {"id": 26, "cpf": "60440964083", "date": "2026-01-03", "steps": 8800, "sleep_hours": 6.6, "calories": 2200, "bpm": 71},
    {"id": 27, "cpf": "60440964083", "date": "2026-01-01", "steps": 6200, "sleep_hours": 8.5, "calories": 1800, "bpm": 65},

    {"id": 28, "cpf": "60440964083", "date": "2025-12-29", "steps": 9100, "sleep_hours": 7.2, "calories": 2250, "bpm": 73},
    {"id": 29, "cpf": "60440964083", "date": "2025-12-26", "steps": 10000, "sleep_hours": 6.4, "calories": 2500, "bpm": 78},
    {"id": 30, "cpf": "60440964083", "date": "2025-12-23", "steps": 7600, "sleep_hours": 7.8, "calories": 2000, "bpm": 69},

    {"id": 31, "cpf": "60440964083", "date": "2025-12-20", "steps": 8900, "sleep_hours": 7.1, "calories": 2150, "bpm": 72},
    {"id": 32, "cpf": "60440964083", "date": "2025-12-17", "steps": 10800, "sleep_hours": 6.9, "calories": 2600, "bpm": 80},
    {"id": 33, "cpf": "60440964083", "date": "2025-12-14", "steps": 7000, "sleep_hours": 8.0, "calories": 1900, "bpm": 67},

    {"id": 34, "cpf": "60440964083", "date": "2025-12-10", "steps": 9300, "sleep_hours": 7.3, "calories": 2250, "bpm": 73},
    {"id": 35, "cpf": "60440964083", "date": "2025-12-06", "steps": 8400, "sleep_hours": 6.7, "calories": 2100, "bpm": 70},
    {"id": 36, "cpf": "60440964083", "date": "2025-12-02", "steps": 10200, "sleep_hours": 7.6, "calories": 2450, "bpm": 76},

    {"id": 37, "cpf": "60440964083", "date": "2025-11-28", "steps": 7800, "sleep_hours": 8.2, "calories": 1950, "bpm": 66},
    {"id": 38, "cpf": "60440964083", "date": "2025-11-24", "steps": 9600, "sleep_hours": 7.0, "calories": 2300, "bpm": 74},
    {"id": 39, "cpf": "60440964083", "date": "2025-11-20", "steps": 11000, "sleep_hours": 6.5, "calories": 2700, "bpm": 82},

    {"id": 40, "cpf": "60440964083", "date": "2025-11-15", "steps": 7200, "sleep_hours": 7.9, "calories": 2000, "bpm": 68},
    {"id": 41, "cpf": "60440964083", "date": "2025-11-10", "steps": 8900, "sleep_hours": 7.1, "calories": 2150, "bpm": 71},
    {"id": 42, "cpf": "60440964083", "date": "2025-11-05", "steps": 10100, "sleep_hours": 6.8, "calories": 2500, "bpm": 77},

    {"id": 43, "cpf": "60440964083", "date": "2025-10-31", "steps": 8600, "sleep_hours": 7.4, "calories": 2200, "bpm": 72},
    {"id": 44, "cpf": "60440964083", "date": "2025-10-26", "steps": 9400, "sleep_hours": 6.9, "calories": 2350, "bpm": 75},
    {"id": 45, "cpf": "60440964083", "date": "2025-10-21", "steps": 10800, "sleep_hours": 7.7, "calories": 2600, "bpm": 79},

    {"id": 46, "cpf": "60440964083", "date": "2025-10-15", "steps": 7300, "sleep_hours": 8.1, "calories": 1900, "bpm": 66},
    {"id": 47, "cpf": "60440964083", "date": "2025-10-09", "steps": 9100, "sleep_hours": 7.2, "calories": 2250, "bpm": 73},
    {"id": 48, "cpf": "60440964083", "date": "2025-10-03", "steps": 10000, "sleep_hours": 6.6, "calories": 2400, "bpm": 76},

    {"id": 49, "cpf": "60440964083", "date": "2025-09-27", "steps": 8200, "sleep_hours": 7.8, "calories": 2100, "bpm": 69},
    {"id": 50, "cpf": "60440964083", "date": "2025-09-21", "steps": 9700, "sleep_hours": 7.0, "calories": 2300, "bpm": 74},

    {"id": 51, "cpf": "60440964083", "date": "2025-09-14", "steps": 8800, "sleep_hours": 7.3, "calories": 2200, "bpm": 71},
    {"id": 52, "cpf": "60440964083", "date": "2025-09-07", "steps": 10500, "sleep_hours": 6.9, "calories": 2550, "bpm": 78},
    {"id": 53, "cpf": "60440964083", "date": "2025-08-31", "steps": 7600, "sleep_hours": 8.0, "calories": 1950, "bpm": 67},

    {"id": 54, "cpf": "60440964083", "date": "2025-08-23", "steps": 9200, "sleep_hours": 7.1, "calories": 2250, "bpm": 73},
    {"id": 55, "cpf": "60440964083", "date": "2025-08-15", "steps": 10100, "sleep_hours": 6.7, "calories": 2450, "bpm": 77},

    {"id": 56, "cpf": "60440964083", "date": "2025-08-07", "steps": 6900, "sleep_hours": 8.3, "calories": 1800, "bpm": 65},
    {"id": 57, "cpf": "60440964083", "date": "2025-07-30", "steps": 8700, "sleep_hours": 7.2, "calories": 2150, "bpm": 71},
    {"id": 58, "cpf": "60440964083", "date": "2025-07-22", "steps": 9800, "sleep_hours": 6.8, "calories": 2350, "bpm": 75},

    {"id": 59, "cpf": "60440964083", "date": "2025-07-14", "steps": 11200, "sleep_hours": 7.6, "calories": 2700, "bpm": 81},
    {"id": 60, "cpf": "60440964083", "date": "2025-07-06", "steps": 7400, "sleep_hours": 8.1, "calories": 1900, "bpm": 66},

    {"id": 61, "cpf": "60440964083", "date": "2025-06-28", "steps": 9000, "sleep_hours": 7.0, "calories": 2200, "bpm": 72},
    {"id": 62, "cpf": "60440964083", "date": "2025-06-20", "steps": 10300, "sleep_hours": 6.6, "calories": 2500, "bpm": 78},

    {"id": 63, "cpf": "60440964083", "date": "2025-06-12", "steps": 7800, "sleep_hours": 7.9, "calories": 2000, "bpm": 68},
    {"id": 64, "cpf": "60440964083", "date": "2025-06-04", "steps": 9100, "sleep_hours": 7.1, "calories": 2250, "bpm": 73},

    {"id": 65, "cpf": "60440964083", "date": "2025-05-27", "steps": 10000, "sleep_hours": 6.8, "calories": 2400, "bpm": 76},
    {"id": 66, "cpf": "60440964083", "date": "2025-05-19", "steps": 8500, "sleep_hours": 7.4, "calories": 2150, "bpm": 71},

    {"id": 67, "cpf": "60440964083", "date": "2025-05-11", "steps": 10800, "sleep_hours": 7.7, "calories": 2600, "bpm": 79},
    {"id": 68, "cpf": "60440964083", "date": "2025-05-03", "steps": 7200, "sleep_hours": 8.2, "calories": 1900, "bpm": 66},

    {"id": 69, "cpf": "60440964083", "date": "2025-04-25", "steps": 8900, "sleep_hours": 7.0, "calories": 2200, "bpm": 72},
    {"id": 70, "cpf": "60440964083", "date": "2025-04-17", "steps": 10400, "sleep_hours": 6.9, "calories": 2450, "bpm": 77}

]

class FitbitModel:
    @staticmethod
    def find_by_cpf_and_date(cpf: str, start_date: str, end_date: str):
        # Access your data (assuming fake_database is defined in the file)
        user_records = [d for d in fake_database if d["cpf"] == cpf]
        
        # Filter by date range
        filtered = [
            d for d in user_records 
            if start_date <= d["date"] <= end_date
        ]
        return filtered
    

FAKE_PATIENTS_DB: List[Dict[str, Any]] = [
    {
        "name": "TEST USER",
        "cpf": "12345678900", 
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxwKc.6IymCs7CN52au9gm.ma1xey"
    }
]

# Tabela Mock de Médicos
FAKE_DOCTORS_DB: List[Dict[str, Any]] = []