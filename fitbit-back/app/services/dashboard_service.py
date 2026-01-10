from app.models.mock import FitbitModel 

def get_dashboard_metrics(cpf: str, period: str):
    # 1. Busca dados pelo CPF no Mock/Model
    raw_data = FitbitModel.find_by_cpf(cpf)
    
    # Tratamento para dados vazios (Formato Fitbit vazio)
    if not raw_data:
        return {
            "activities-steps": [],
            "activities-heart": [],
            "sleep": []
        }

    # 2. Transformação para o padrão Fitbit
    fitbit_data = {
        "activities-steps": [],
        "activities-heart": [],
        "sleep": []
    }

    for d in raw_data:
        # Passos: dateTime e value (string)
        fitbit_data["activities-steps"].append({
            "dateTime": d["date"],
            "value": str(d["steps"])
        })
        
        # BPM: dateTime e value com restingHeartRate
        fitbit_data["activities-heart"].append({
            "dateTime": d["date"],
            "value": {"restingHeartRate": d["bpm"]}
        })
        
        # Sono: dateOfSleep e minutesAsleep (Horas * 60)
        fitbit_data["sleep"].append({
            "dateOfSleep": d["date"],
            "minutesAsleep": int(d["sleep_hours"] * 60)
        })

    return fitbit_data