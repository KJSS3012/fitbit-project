from app.models.mock import FitbitModel 

def get_dashboard_metrics(cpf: str, period: str):

    # 1. Find data by CPF
    raw_data = FitbitModel.find_by_cpf(cpf)
    
    # Empty data handling
    if not raw_data:
        return {
            "period": period,
            "summary": {"avg_steps": 0, "avg_bpm": 0, "avg_sleep": 0, "days_analyzed": 0},
            "charts": {"dates": [], "steps": [], "bpm": [], "sleep": []}
        }

    # 2. Filter by ... (Por enquanto pegamos tudo, depois implementamos datas)
    filtered_data = raw_data

    # 3. Metrics calculation
    count = len(filtered_data)
    total_steps = sum(d["steps"] for d in filtered_data)
    total_bpm = sum(d["bpm"] for d in filtered_data)
    total_sleep = sum(d["sleep_hours"] for d in filtered_data)

    # 4. Transform data for charts
    dates_list = [d["date"] for d in filtered_data]
    steps_list = [d["steps"] for d in filtered_data]
    bpm_list   = [d["bpm"] for d in filtered_data]
    sleep_list = [d["sleep_hours"] for d in filtered_data]

    # 5. SchemafFormatting and return
    return {
        "period": period,
        "summary": {
            "days_analyzed": count,
            "avg_steps": int(total_steps / count),
            "avg_bpm": int(total_bpm / count),
            "avg_sleep": round(total_sleep / count, 1)
        },
        "charts": {
            "dates": dates_list,
            "steps": steps_list,
            "bpm": bpm_list,
            "sleep": sleep_list
        }
    }