import os
import base64
import requests
from fastapi import APIRouter, Query
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

@router.get("/fitbit")
def initiate_fitbit_auth():
    authorization_url = (
        f"{FITBIT_AUTH_URL}"
        f"?response_type=code"
        f"&client_id={FITBIT_CLIENT_ID}"
        f"&redirect_uri={FITBIT_REDIRECT_URI}"
        f"&scope=activity heartrate sleep profile"
    )
    return RedirectResponse(authorization_url)

@router.get("/fitbit/callback")
def handle_fitbit_callback(code: str = Query(...)):
    credentials = f"{FITBIT_CLIENT_ID}:{FITBIT_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    token_request_data = {
        "grant_type": "authorization_code",
        "redirect_uri": FITBIT_REDIRECT_URI,
        "code": code,
    }

    token_response = requests.post(FITBIT_TOKEN_URL, headers=headers, data=token_request_data)
    token_response.raise_for_status()

    user_tokens["fitbit"] = token_response.json()

    return {"message": "Successfully authenticated", "tokens": user_tokens["fitbit"]}

@router.get("/fitbit/profile")
def get_fitbit_profile():
    access_token = user_tokens["fitbit"]["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    profile_response = requests.get(f"{FITBIT_API_BASE_URL}/profile.json", headers=headers)
    return profile_response.json()