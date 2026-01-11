import os, requests, time
from datetime import date
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

from app.models.mock import FAKE_PATIENTS_DB
from app.core.fitbit_client import get_auth_header, get_valid_token, save_persistence, load_persistence
from app.core.security import get_current_user_cpf

router = APIRouter()
FITBIT_CLIENT_ID = os.getenv("FITBIT_CLIENT_ID")
FITBIT_REDIRECT_URI = os.getenv("FITBIT_REDIRECT_URI")
FITBIT_API_BASE_URL = "https://api.fitbit.com/1/user/-"

def fitbit_get(endpoint: str, cpf: str):
    token = get_valid_token(cpf)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    return response.json()

@router.get("/auth")
def auth(cpf: str):
    """Initializes the OAuth2 flow. No JWT required here to allow browser redirect."""
    params = {
        "response_type": "code",
        "client_id": FITBIT_CLIENT_ID,
        "redirect_uri": FITBIT_REDIRECT_URI,
        "scope": "activity heartrate sleep profile",
        "state": cpf
    }
    return RedirectResponse(url=f"https://www.fitbit.com/oauth2/authorize?{urlencode(params)}")

@router.get("/callback")
def callback(code: str = Query(...), state: str = Query(...)):
    """The fitbit OAuth2 callback endpoint to exchange code for tokens and save them."""
    target_cpf = state 
    
    data = {
        "grant_type": "authorization_code",
        "redirect_uri": FITBIT_REDIRECT_URI,
        "code": code,
    }

    resp = requests.post("https://api.fitbit.com/oauth2/token", headers=get_auth_header(), data=data)
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get token from Fitbit")
    
    token_data = resp.json()

    load_persistence()
    
    user = next((p for p in FAKE_PATIENTS_DB if p.get("cpf") == target_cpf), None)
    if not user:
        user = {"cpf": target_cpf}
        FAKE_PATIENTS_DB.append(user)

    user.update({
        "fitbit_access_token": token_data["access_token"],
        "fitbit_refresh_token": token_data.get("refresh_token"),
        "fitbit_expires_at": time.time() + token_data.get("expires_in", 3600)
    })
    
    save_persistence()
    return {"status": "Success", "message": f"Fitbit linked to CPF {target_cpf} and saved."}

@router.get("/profile")
def profile(cpf: str = Depends(get_current_user_cpf)):
    return fitbit_get(f"{FITBIT_API_BASE_URL}/profile.json", cpf)

@router.get("/dashboard")
def dashboard(day: str = date.today().isoformat(), cpf: str = Depends(get_current_user_cpf)):
    return {
        "profile": fitbit_get(f"{FITBIT_API_BASE_URL}/profile.json", cpf),
        "heartrate": fitbit_get(f"{FITBIT_API_BASE_URL}/activities/heart/date/{day}/1d.json", cpf)
    }