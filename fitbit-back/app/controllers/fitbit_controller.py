import os
import base64
import requests
from datetime import date, datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from typing import Dict, Optional
import time

from app.api.dependencies import get_current_user

load_dotenv()

router = APIRouter()

FITBIT_CLIENT_ID = os.getenv("FITBIT_CLIENT_ID")
FITBIT_CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET")
FITBIT_REDIRECT_URI = os.getenv("FITBIT_REDIRECT_URI")

FITBIT_AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
FITBIT_TOKEN_URL = "https://api.fitbit.com/oauth2/token"
FITBIT_API_BASE_URL = "https://api.fitbit.com/1/user/-"

user_tokens = {}
profile_cache = {}  # Cache for profile data
last_request_time = 0  # Track last API request for rate limiting

def get_access_token():
    if "fitbit" not in user_tokens:
        raise HTTPException(status_code=401, detail="Not authenticated with Fitbit")
    return user_tokens["fitbit"]["access_token"]

def fitbit_get(endpoint: str, cache_key: Optional[str] = None, cache_seconds: int = 0):
    """
    Make GET request to Fitbit API with optional caching and rate limiting.
    
    Args:
        endpoint: Full URL to Fitbit API endpoint
        cache_key: Optional cache key. If provided, response will be cached.
        cache_seconds: How long to cache the response (0 = no cache)
    """
    global last_request_time
    
    # Check cache first
    if cache_key and cache_key in profile_cache:
        cached_data, cache_time = profile_cache[cache_key]
        if datetime.now() - cache_time < timedelta(seconds=cache_seconds):
            return cached_data
    
    # Rate limiting: wait at least 0.5 seconds between requests
    current_time = time.time()
    if current_time - last_request_time < 0.5:
        time.sleep(0.5 - (current_time - last_request_time))
    
    headers = {
        "Authorization": f"Bearer {get_access_token()}"
    }
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Update cache if cache_key provided
        if cache_key:
            profile_cache[cache_key] = (data, datetime.now())
        
        last_request_time = time.time()
        return data
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            # Return cached data if available, otherwise raise
            if cache_key and cache_key in profile_cache:
                cached_data, _ = profile_cache[cache_key]
                return cached_data
            raise HTTPException(
                status_code=429, 
                detail="Fitbit API rate limit exceeded. Please try again in a few minutes."
            )
        raise

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
    return RedirectResponse("http://localhost:3000/dashboard/main?fitbit=connected")

@router.get("/status")
def get_fitbit_status(current_user: Dict = Depends(get_current_user)):
    """
    Check if user has connected Fitbit account and data availability.
    Requires: JWT token (patient or doctor)
    Returns: {"connected": bool, "hasData": bool, "lastSync": str|null}
    """
    is_connected = "fitbit" in user_tokens and user_tokens["fitbit"].get("access_token") is not None
    has_data = False
    last_sync = None
    
    if is_connected:
        try:
            profile_data = fitbit_get(f"{FITBIT_API_BASE_URL}/profile.json")
            has_data = profile_data is not None
            last_sync = profile_data.get("user", {}).get("memberSince") if profile_data else None
        except Exception:
            pass
    
    return {
        "connected": is_connected,
        "hasData": has_data,
        "lastSync": last_sync,
        "user_id": current_user["sub"] if is_connected else None
    }

@router.post("/disconnect")
def disconnect_fitbit(current_user: Dict = Depends(get_current_user)):
    """
    Disconnect Fitbit account.
    Requires: JWT token (patient or doctor)
    """
    if "fitbit" in user_tokens:
        del user_tokens["fitbit"]
    
    return {"success": True, "message": "Fitbit desconectado com sucesso"}

@router.get("/profile")
def profile(current_user: Dict = Depends(get_current_user)):
    """
    Get Fitbit profile.
    Requires: JWT token (patient or doctor)
    """
    return fitbit_get(f"{FITBIT_API_BASE_URL}/profile.json")

@router.get("/dashboard")
def dashboard(
    day: str = date.today().isoformat(),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get complete Fitbit dashboard data.
    Requires: JWT token (patient or doctor)
    User info: current_user["sub"] = CPF/CRM, current_user["type"] = patient/doctor
    
    Note: Profile data is cached for 1 hour to reduce API calls.
    """
    try:
        # Profile changes rarely, cache for 1 hour (3600 seconds)
        profile_data = fitbit_get(
            f"{FITBIT_API_BASE_URL}/profile.json",
            cache_key="profile",
            cache_seconds=3600
        )
        
        # Activity data for specific day
        activity_data = fitbit_get(f"{FITBIT_API_BASE_URL}/activities/date/{day}.json")
        
        # Heart rate data for specific day
        heartrate_data = fitbit_get(f"{FITBIT_API_BASE_URL}/activities/heart/date/{day}/1d.json")
        
        # Sleep data for specific day
        sleep_data = fitbit_get(f"{FITBIT_API_BASE_URL}/sleep/date/{day}.json")
        
        return {
            "profile": profile_data,
            "activity": activity_data,
            "heartrate": heartrate_data,
            "sleep": sleep_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Fitbit data: {str(e)}")

@router.get("/activity")
def activity(
    day: str = date.today().isoformat(),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get Fitbit activity for a specific day.
    Requires: JWT token (patient or doctor)
    """
    return fitbit_get(f"{FITBIT_API_BASE_URL}/activities/date/{day}.json")

@router.get("/heartrate")
def heartrate(
    day: str = date.today().isoformat(),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get Fitbit heart rate for a specific day.
    Requires: JWT token (patient or doctor)
    """
    return fitbit_get(f"{FITBIT_API_BASE_URL}/activities/heart/date/{day}/1d.json")

@router.get("/sleep")
def sleep(
    day: str = date.today().isoformat(),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get Fitbit sleep data for a specific day.
    Requires: JWT token (patient or doctor)
    """
    return fitbit_get(f"{FITBIT_API_BASE_URL}/sleep/date/{day}.json")

@router.get("/dashboard")
def dashboard(
    day: str = date.today().isoformat(),
    current_user: Dict = Depends(get_current_user)
):
    """
    Get complete Fitbit dashboard data.
    Requires: JWT token (patient or doctor)
    User info: current_user["sub"] = CPF/CRM, current_user["type"] = patient/doctor
    """
    return {
        "profile": fitbit_get(f"{FITBIT_API_BASE_URL}/profile.json"),
        "activity": fitbit_get(f"{FITBIT_API_BASE_URL}/activities/date/{day}.json"),
        "heartrate": fitbit_get(f"{FITBIT_API_BASE_URL}/activities/heart/date/{day}/1d.json"),
        "sleep": fitbit_get(f"{FITBIT_API_BASE_URL}/sleep/date/{day}.json"),
    }
