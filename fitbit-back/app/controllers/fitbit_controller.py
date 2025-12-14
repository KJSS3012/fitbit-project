import os
import base64
import requests
from datetime import date
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

FITBIT_CLIENT_ID = os.getenv("FITBIT_CLIENT_ID")
FITBIT_CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET")
FITBIT_REDIRECT_URI = os.getenv("FITBIT_REDIRECT_URI")

FITBIT_AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
FITBIT_TOKEN_URL = "https://api.fitbit.com/oauth2/token"
FITBIT_API_BASE_URL = "https://api.fitbit.com/1/user/-"

user_tokens = {}

def get_access_token():
    if "fitbit" not in user_tokens:
        raise HTTPException(status_code=401, detail="Not authenticated with Fitbit")
    return user_tokens["fitbit"]["access_token"]

def fitbit_get(endpoint: str):
    headers = {
        "Authorization": f"Bearer {get_access_token()}"
    }
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    return response.json()

@router.get("/auth")
def auth():
    url = (
        f"{FITBIT_AUTH_URL}"
        f"?response_type=code"
        f"&client_id={FITBIT_CLIENT_ID}"
        f"&redirect_uri={FITBIT_REDIRECT_URI}"
        f"&scope=activity heartrate sleep profile"
    )
    return RedirectResponse(url)

@router.get("/callback")
def callback(code: str = Query(...)):
    credentials = f"{FITBIT_CLIENT_ID}:{FITBIT_CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "authorization_code",
        "redirect_uri": FITBIT_REDIRECT_URI,
        "code": code,
    }

    response = requests.post(FITBIT_TOKEN_URL, headers=headers, data=data)
    response.raise_for_status()

    user_tokens["fitbit"] = response.json()
    return {"status": "authenticated"}

@router.get("/profile")
def profile():
    return fitbit_get(f"{FITBIT_API_BASE_URL}/profile.json")

@router.get("/activity")
def activity(day: str = date.today().isoformat()):
    return fitbit_get(f"{FITBIT_API_BASE_URL}/activities/date/{day}.json")

@router.get("/heartrate")
def heartrate(day: str = date.today().isoformat()):
    return fitbit_get(f"{FITBIT_API_BASE_URL}/activities/heart/date/{day}/1d.json")

@router.get("/sleep")
def sleep(day: str = date.today().isoformat()):
    return fitbit_get(f"{FITBIT_API_BASE_URL}/sleep/date/{day}.json")

@router.get("/dashboard")
def dashboard(day: str = date.today().isoformat()):
    return {
        "profile": fitbit_get(f"{FITBIT_API_BASE_URL}/profile.json"),
        "activity": fitbit_get(f"{FITBIT_API_BASE_URL}/activities/date/{day}.json"),
        "heartrate": fitbit_get(f"{FITBIT_API_BASE_URL}/activities/heart/date/{day}/1d.json"),
        "sleep": fitbit_get(f"{FITBIT_API_BASE_URL}/sleep/date/{day}.json"),
    }
