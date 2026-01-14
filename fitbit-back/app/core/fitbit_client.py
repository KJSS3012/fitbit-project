import os, base64, requests, time, json
from app.models.mock import FAKE_PATIENTS_DB

DATA_FILE = "patients_data.json"

def load_persistence():
    """
    Ensures the data file exists and synchronizes it with the in-memory database.
    """
    # If file does not exist, create it as an empty list
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)
        return

    # If it exists, read and sync
    with open(DATA_FILE, "r") as f:
        try:
            content = f.read()
            if not content: 
                return
            data = json.loads(content)
            
            # Sync memory with file content
            FAKE_PATIENTS_DB.clear()
            FAKE_PATIENTS_DB.extend(data)
        except json.JSONDecodeError:
            # If file is corrupted, we treat it as empty to avoid crashes
            pass

def save_persistence():
    with open(DATA_FILE, "w") as f:
        json.dump(FAKE_PATIENTS_DB, f, indent=4)

def get_auth_header():
    client_id = os.getenv("FITBIT_CLIENT_ID")
    client_secret = os.getenv("FITBIT_CLIENT_SECRET")
    credentials = f"{client_id}:{client_secret}"
    return {"Authorization": f"Basic {base64.b64encode(credentials.encode()).decode()}"}

def get_valid_token(cpf: str):
    load_persistence()
    user = next((p for p in FAKE_PATIENTS_DB if p.get("cpf") == cpf), None)
    if not user or "fitbit_access_token" not in user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Fitbit not linked for this user")
    return user["fitbit_access_token"]

def fetch_fitbit_data(endpoint: str, cpf: str):
    token = get_valid_token(cpf)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    return response.json()