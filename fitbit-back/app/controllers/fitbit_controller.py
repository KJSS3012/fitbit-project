import os
import time
import requests
from datetime import date
from typing import Dict

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.repositories.patient_repository import PatientRepository
from app.core.fitbit_client import get_auth_header
from app.core.security import get_current_user_cpf

router = APIRouter()

FITBIT_CLIENT_ID = os.getenv("FITBIT_CLIENT_ID")
FITBIT_REDIRECT_URI = os.getenv("FITBIT_REDIRECT_URI")
FITBIT_API_BASE_URL = "https://api.fitbit.com/1/user/-"
FITBIT_TOKEN_URL = "https://api.fitbit.com/oauth2/token"


# =========================
# Helpers
# =========================
def fitbit_get(endpoint: str, cpf: str, db: Session):
    """Make authenticated request to Fitbit API."""
    patient_repo = PatientRepository(db)
    patient = patient_repo.find_by_cpf(cpf)
    
    if not patient or not patient.fitbit_access_token:
        raise HTTPException(status_code=401, detail="Fitbit não conectado")
    
    headers = {"Authorization": f"Bearer {patient.fitbit_access_token}"}
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    return response.json()


# =========================
# OAuth Flow
# =========================
@router.get("/auth")
def auth(cpf: str):
    """Initializes Fitbit OAuth2 flow."""
    params = {
        "response_type": "code",
        "client_id": FITBIT_CLIENT_ID,
        "redirect_uri": FITBIT_REDIRECT_URI,
        "scope": "activity heartrate sleep profile",
        "state": cpf,
    }
    return RedirectResponse(
        url=f"https://www.fitbit.com/oauth2/authorize?{urlencode(params)}"
    )


@router.get("/callback")
def callback(
    code: str = Query(None), 
    error: str = Query(None), 
    state: str = Query(...),
    db: Session = Depends(get_db)
):
    """Exchange authorization code for tokens and persist them."""
    frontend_url = "http://localhost:3000/dashboard/settings/fitbit"
    
    # Usuário negou acesso
    if error == "access_denied":
        return RedirectResponse(f"{frontend_url}?fitbit=denied")
    
    # Outro erro OAuth
    if error:
        return RedirectResponse(f"{frontend_url}?fitbit=error")
    
    # Sem code = erro
    if not code:
        return RedirectResponse(f"{frontend_url}?fitbit=error")
    
    target_cpf = state

    data = {
        "grant_type": "authorization_code",
        "redirect_uri": FITBIT_REDIRECT_URI,
        "code": code,
    }

    try:
        resp = requests.post(FITBIT_TOKEN_URL, headers=get_auth_header(), data=data)
        if resp.status_code != 200:
            return RedirectResponse(f"{frontend_url}?fitbit=error")

        token_data = resp.json()
    except Exception:
        return RedirectResponse(f"{frontend_url}?fitbit=error")

    # Salva tokens no banco de dados
    patient_repo = PatientRepository(db)
    patient = patient_repo.update_fitbit_tokens(
        cpf=target_cpf,
        access_token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token", ""),
        expires_at=time.time() + token_data.get("expires_in", 3600)
    )
    
    if not patient:
        return RedirectResponse(f"{frontend_url}?fitbit=error")

    return RedirectResponse("http://localhost:3000/dashboard/main?fitbit=connected")


# =========================
# Connection Management
# =========================
@router.get("/status")
def fitbit_status(
    cpf: str = Depends(get_current_user_cpf),
    db: Session = Depends(get_db)
):
    """Check if user has connected Fitbit account."""
    patient_repo = PatientRepository(db)
    patient = patient_repo.find_by_cpf(cpf)
    
    if not patient or not patient.fitbit_access_token:
        return {"connected": False}
    
    return {
        "connected": True,
        "scopes": ["activity", "heartrate", "sleep", "profile"]
    }


@router.post("/disconnect")
def disconnect_fitbit(
    cpf: str = Depends(get_current_user_cpf),
    db: Session = Depends(get_db)
):
    """Disconnect Fitbit account by removing tokens."""
    patient_repo = PatientRepository(db)
    patient = patient_repo.remove_fitbit_tokens(cpf)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return {"message": "Fitbit desconectado com sucesso"}


# =========================
# Fitbit Endpoints (JWT required)
# =========================
@router.get("/profile")
def profile(
    cpf: str = Depends(get_current_user_cpf),
    db: Session = Depends(get_db)
):
    return fitbit_get(f"{FITBIT_API_BASE_URL}/profile.json", cpf, db)


@router.get("/activity")
def activity(
    day: str = date.today().isoformat(),
    cpf: str = Depends(get_current_user_cpf),
    db: Session = Depends(get_db)
):
    return fitbit_get(
        f"{FITBIT_API_BASE_URL}/activities/date/{day}.json", cpf, db
    )


@router.get("/heartrate")
def heartrate(
    day: str = date.today().isoformat(),
    cpf: str = Depends(get_current_user_cpf),
    db: Session = Depends(get_db)
):
    return fitbit_get(
        f"{FITBIT_API_BASE_URL}/activities/heart/date/{day}/1d.json", cpf, db
    )


@router.get("/sleep")
def sleep(
    day: str = date.today().isoformat(),
    cpf: str = Depends(get_current_user_cpf),
    db: Session = Depends(get_db)
):
    return fitbit_get(
        f"{FITBIT_API_BASE_URL}/sleep/date/{day}.json", cpf, db
    )


@router.get("/dashboard")
def dashboard(
    day: str = date.today().isoformat(),
    cpf: str = Depends(get_current_user_cpf),
    db: Session = Depends(get_db)
):
    return {
        "profile": fitbit_get(f"{FITBIT_API_BASE_URL}/profile.json", cpf, db),
        "activity": fitbit_get(
            f"{FITBIT_API_BASE_URL}/activities/date/{day}.json", cpf, db
        ),
        "heartrate": fitbit_get(
            f"{FITBIT_API_BASE_URL}/activities/heart/date/{day}/1d.json", cpf, db
        ),
        "sleep": fitbit_get(
            f"{FITBIT_API_BASE_URL}/sleep/date/{day}.json", cpf, db
        ),
    }
